#!/usr/bin/env python3

# import section
import socket
import sys
import os
import argparse
import tftp

# Configuring arguments parser
parser = argparse.ArgumentParser()
parser.add_argument('-p', '--port', dest='port', type=int,  default=6969, help='indique le numéro de port du serveur (par défaut, 6969).')
parser.add_argument('-t', "--timeout", dest='timeout', type=int, default=2, help="indique le délai en secondes à partir duquel on considère que l'envoi ou la réception échoue (par défaut, 2).")
parser.add_argument('-c', '--cwd', dest='cwd', type=str, default='', help='permet de changer le répertoire courant dans lequel les fichiers (avec des chemins relatifs) sont lus ou écrits.')
# parser.add_argument('ff', type=str)
subparsers = parser.add_subparsers(dest='cmd')
subparsers.add_parser('get', help="la récupération d'un fichier stocké sur le serveur distant sur la machine locale.")
subparsers.add_parser('put', help="la recopie d'un fichier stocké sur la machine locale vers le serveur distant.")
parser.add_argument('host', type=str, default='', help='Hostname')
parser.add_argument('filename', type=str, default='', help='Filename')
parser.add_argument('targetname' , type=str, nargs='?', default='', help="Targetname")
parser.add_argument('-b', '--blksize', dest='blksize', type=int, default=512, help='indique la taille en octet du bloc de données utilisée pour transférer les fichiers (par défaut, 512).')
args = parser.parse_args()

# change target filename
if args.targetname == '': args.targetname = args.filename

# change current working directory
if args.cwd != '': os.chdir(args.cwd)

# get request
if args.cmd == 'get':
    tftp.get((args.host, args.port), args.filename, args.targetname, args.blksize, args.timeout)

# put request
if args.cmd == 'put':
    tftp.put((args.host, args.port), args.filename, args.targetname, args.blksize, args.timeout)

# EOF
