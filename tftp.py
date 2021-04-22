#!/usr/bin/env python3

"""
TFTP Module.
"""
from typing import Any

import socket
import struct
import sys
import threading

########################################################################
#                          DEAFULT VALUES                              #
########################################################################

BLKSIZE_DEFAULT = 512
PORT_DEFAULT = 6969
RRQ_OPCODE = 1
WRQ_OPCODE = 2
DAT_OPCODE = 3
ACK_OPCODE = 4
OPCODE_DIC = {RRQ_OPCODE:"RRQ", WRQ_OPCODE:"WRQ", DAT_OPCODE:"DAT", ACK_OPCODE:"ACK"}
BLOCK_NUMBER = 0
ACK_LEN = 4 # 4 Bytes for ACK packet
CLIENT = 101
SERVER = 102
MODE_DEFAULT = 'octet'
TIMEOUT_DEFAULT = 2
THREAD_DEFAULT = False

########################################################################
#                          COMMON ROUTINES                             #
########################################################################

def print_verbose(opcode, sock, addr, counter, packet, flag):
    if flag == CLIENT:
        print("[myclient:{0} -> myserver:{1}] {2}{3}={4}".format(sock.getsockname()[1], addr[1], OPCODE_DIC[opcode],
                                                                 counter, packet))  # Printing Verbose to screen
    elif flag == SERVER:
        print("[myserver:{0} -> myclient:{1}] {2}{3}={4}".format(addr[1], sock.getsockname()[1], OPCODE_DIC[opcode],
                                                                 counter, packet))  # Printing Verbose to screen
    else:
        print("[myclient:{0} -> myserver:{1}] {2}={3}".format(sock.getsockname()[1], addr[1], OPCODE_DIC[opcode], packet))
    return 0

def unpack_packet(frame):
    packet_unpacked = []
    frame1 = frame[0:2]
    frame2 = frame[2:]
    packet_unpacked.append(int(int.from_bytes(frame1, byteorder='big')))  # Extracting opcode
    args = frame2.split(b'\x00')  # args = [b'test.txt', b'octet', b'',]
    for i in range(len(args)):
        packet_unpacked.append(args[i].decode('ascii'))
    return packet_unpacked

# ACK PACKET UNPACK
def ack_unpack(data):
    packet_unpacked = [] # data = '\x00\x04\x00\x01'
    frame1 = data[0:2]  # frame1 = b'\x00\x04'
    frame2 = data[2:]  # frame2 = b'\x00\x01'
    packet_unpacked.append(int.from_bytes(frame1, byteorder='big'))  # Extracting opcode
    packet_unpacked.append(int.from_bytes(frame2, byteorder='big')) # Extracting Block number
    return packet_unpacked

# DAT PACKET UNPACK
def dat_unpack(data):
    packet_unpacked = []  # data = '\x00\x04\x00\x01DATA'
    frame1 = data[0:2]  # frame1 = b'\x00\x04'
    frame2 = data[2:4]  # frame2 = b'\x00\x01'
    frame3 = data[4:]   # frame3 = b'DATA'
    packet_unpacked.append(int.from_bytes(frame1, byteorder='big'))  # Extracting opcode
    packet_unpacked.append(int.from_bytes(frame2, byteorder='big'))  # Extracting Block number
    packet_unpacked.append(frame3)
    return packet_unpacked

def rq_packet_formater(filename, opcode, blksize):
    # Parsing data into rrq packet
    # Format without header
    #     2 bytes    string    1 byte    string         1 byte
    #     --------------------------------------------------------
    #    | 01/02 |  Filename  |   0  |    Mode    |   blksize     |      |
    #     --------------------------------------------------------
    if blksize == BLKSIZE_DEFAULT:
        formatter = '>H{}sB{}sB'  # { > - Big Endian, h - short , s - char, B - 1 byte }
        formatter = formatter.format(len(filename), len(MODE_DEFAULT))
        return struct.pack(formatter, opcode, bytes(filename, 'ascii'), 0, bytes(MODE_DEFAULT, 'ascii'), 0)
    else:
        formatter = '>H{}sB{}sB{}sB{}sB'  # { > - Big Endian, h - short , s - char, B - 1 byte }
        formatter = formatter.format(len(filename), len(MODE_DEFAULT), len("blksize"), len(str(blksize)))
        return struct.pack(formatter, opcode, bytes(filename, 'ascii'), 0, bytes(MODE_DEFAULT, 'ascii'), 0, bytes("blksize", "ascii"), 0, bytes(str(blksize), "ascii"), 0)

def dat_packet_formater(data, block_number):
    # Parsing data into DAT packet
    # Format without header
    #     2 bytes     2-bytes             512-bytes
    #     ------------------------------------------------
    #    | 01/02 |  Block Number  |          Data         |
    #     ------------------------------------------------
    formatter = '>HH{}s' # { > - Big Endian, h - short , s - char, B - 1 byte }
    formatter = formatter.format(len(data))
    return struct.pack(formatter, DAT_OPCODE, block_number, data)

def ack_packet_formater(ack_counter):
    # Formatting an ACK packet
    formatter = '>HH'  # { > - Big Endian, h - short , h - short}
    return struct.pack(formatter, 4, ack_counter)

########################################################################
#                             SERVER SIDE                              #
########################################################################

def handle_put_server(addr, unpacked_data, timeout):
    sock = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM) # Creating new socket
    sock.bind(('', 34209)) # Bind socket on localhost
    sock.settimeout(timeout) # Setting timeout to socket
    ack_counter = 0  # ACK counter
    ack_packet = ack_packet_formater(ack_counter)  # Packing an ACK packet into TFTP format
    sock.sendto(ack_packet, addr)  # Sending ACK packet to server
    filename = unpacked_data[1]
    try:
        with open(filename, "wb+") as file:  # Opening targetname as a file
            while True:
                frame, addr = sock.recvfrom(1024)  # Recv data from server
                data = dat_unpack(frame)  # Unpacking DAT request
                if (data[2] == b''):
                    break
                ack_packet = ack_packet_formater(ack_counter)  # Packing an ACK packet into TFTP format
                sock.sendto(ack_packet, addr)  # Sending ACK packet to server
                file.write(data[2])  # Writing data recvd to file
                ack_counter += 1
    except Exception as e:
        print("Error: ", e)
        sock.close()
    file.close()  # Close file
    sock.close()
    return 0

def handle_get_server(addr, frame_data, timeout):
    sock = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM) # Creating new socket
    sock.bind(('', 34208)) # Bind socket on localhost
    sock.settimeout(timeout) # Setting timeout to socket
    filename = frame_data[1] # Getting filename
    blksize = BLKSIZE_DEFAULT # Setting block size to default
    if len(frame_data) > 5: # Checking if block size is in RRQ packet
         blksize = int(frame_data[4])
    try:
        with open(filename, "rb") as file:
            start = 0
            block_number = 0
            file_data = file.read(blksize)
            while True:
                packet = dat_packet_formater(file_data, block_number) # Packing line into DAT packet
                sock.sendto(packet, addr)
                if file_data == b'':
                    break
                data, addr1 = sock.recvfrom(1024) # Waiting for ACK packet
                ack_packet = ack_unpack(data)
                if ack_packet[0] != ACK_OPCODE:
                    break
                start += blksize
                block_number += 1
                file_data = file.read(blksize)
            file.close()
    except Exception as e:
        print("Error: ", e)
        sock.close()
    sock.close()
    return 0

def sockStart(addr, timeout):
    sock = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
    sock.bind(addr)
    try:
        data , addr1 = sock.recvfrom(1024)
        unpacked_data = unpack_packet(data)
        if unpacked_data[0] == RRQ_OPCODE:
            sock.close()
            handle_get_server(addr1, unpacked_data, timeout)
        elif unpacked_data[0] == WRQ_OPCODE:
            sock.close()
            handle_put_server(addr1, unpacked_data, timeout)
        sock.close()
        return 0
    except Exception as e:
        print("Error: ", e)
        sock.close()
        sockStart(addr, timeout)

def runServer(addr, timeout, thread):
    while 1:
        if thread:
            t = threading.Thread(None, sockStart, None, (addr, timeout))
            t.start()  # start to execute sockStart() in thread
        else:
            sockStart(addr, timeout)
    return 0


########################################################################
#                             CLIENT SIDE                              #
########################################################################

# Putting file from server
def put_file(sock, addr, filename, blksize):
    with open(filename, "rb") as file:
        start = 0
        block_number = 0
        ack_counter = 1
        file_data = file.read(blksize)
        while True:
            packet = dat_packet_formater(file_data, block_number)  # Packing line into DAT packet
            sock.sendto(packet, addr)
            if file_data == b'':
                break
            print_verbose(WRQ_OPCODE, sock, addr, ack_counter, packet, CLIENT)
            data, addr = sock.recvfrom(1024)  # Waiting for ACK packet
            print_verbose(ACK_OPCODE, sock, addr, 0, data, 0)
            ack_packet = ack_unpack(data)
            if ack_packet[0] != ACK_OPCODE:
                break
            block_number += 1
            file_data = file.read(blksize)
        file.close()
    sock.close()
    return 0

def put(addr, filename, targetname, blksize, timeout):
    # Creating udp socket
    s = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
    s.settimeout(timeout)  # Setting socket to timeout
    request = rq_packet_formater(targetname, WRQ_OPCODE, blksize)  # Getting formatted wrq packet
    s.sendto(request, addr)  # Sending TFTP WRQ packet to server
    print_verbose(WRQ_OPCODE, s, addr, 0, request, 0)
    data, addr1 = s.recvfrom(1024)  # Waiting for ACK packet
    print_verbose(ACK_OPCODE, s, addr1, 0, data, SERVER)
    try:
       put_file(s, addr1, filename, blksize)
    except Exception as e:
        print("Error: ", e)
        sys.exit(1)
    return 0


########################################################################

# Getting the file from the server
def get_file(sock, blksize, targetname):
    ack_counter = 1 # ACK counter
    with open(targetname, "wb+") as file: # Opening targetname as a file
        while True:
            frame, addr = sock.recvfrom(1024)  # Recv data from server
            data = dat_unpack(frame)  # Unpacking DAT request
            if data[2] == b'':
                break
            print_verbose(DAT_OPCODE, sock, addr, ack_counter, frame, SERVER)  # Writing DAT verbose to terminal
            ack_packet = ack_packet_formater(ack_counter) # Packing an ACK packet into TFTP format
            sock.sendto(ack_packet, addr) # Sending ACK packet to server
            print_verbose(ACK_OPCODE, sock, addr, ack_counter, ack_packet, CLIENT) # Writing ACK verbose to terminal
            file.write(data[2]) # Writing data recvd to file
            ack_counter += 1
    file.close() # Close file

def get(addr, filename, targetname, blksize, timeout):
    request = rq_packet_formater(filename, RRQ_OPCODE, blksize) # Getting formatted rrq packet
    # Creating udp socket
    s = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
    s.settimeout(timeout)  # Setting socket to timeout
    print_verbose(RRQ_OPCODE, s, addr, 0, request, 0)
    s.sendto(request, addr)  # Sending TFTP RRQ packet to server
    try:
        get_file(s, blksize, targetname)
    except Exception as e:
        print("Error: ", e)
    return 0

# EOF

