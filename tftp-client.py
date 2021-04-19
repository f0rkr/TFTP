# Welcome to my tftp client implementation
# Created by: OroShi

# import section
import socket
import sys
import argparse


# Configuring arguments parser
parser = argparse.ArgumentParser()
# parser.add_argument('-h', type=int, help="affiche l'aide sur la commande.")
parser.add_argument('-p', dest='PORT', type=int,  default=6969, help='indique le numéro de port du serveur (par défaut, 6969).')
parser.add_argument('-t', dest="TIMEOUT", type=int, default=2, help="indique le délai en secondes à partir duquel on considère que l'envoi ou la réception échoue (par défaut, 2).")
parser.add_argument('-c', dest='CWD', type=str, help='permet de changer le répertoire courant dans lequel les fichiers (avec des chemins relatifs) sont lus ou écrits.')
parser.add_argument('cmd', type=str, choices=['get', 'put'])
parser.add_argument('host', type=str)
parser.add_argument('filename', type=str)
parser.add_argument('targetname', type=str, nargs='?', default='')
parser.add_argument('-b', dest='BLKSIZE', type=int, default=512, help='indique la taille en octet du bloc de données utilisée pour transférer les fichiers (par défaut, 512).')
parser.add_argument('--thread', type=bool, default=False, help='indique au serveur de traiter des requêtes clientes en parallèle, en déléguant chaque transfert de fichier à un thread particulier côté serveur (par défaut, False).')
args = parser.parse_args()

print(args)


# This is help function: does print usage of the client
def Help():
    print("usage: tftp-client [-h] [-p PORT] [-t TIMEOUT] [-c CWD] [-b BLKSIZE] {get,put} host filename [targetname]")
    return 0


# Main Function for the client
def Main():
    return 0


if __name__ == "__main__":
    Main()
