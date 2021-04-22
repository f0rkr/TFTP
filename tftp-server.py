#!/usr/bin/env python3
# Welcome to my tftp client implementation
# Created by: F0rkr

# import section
import sys
import os
import argparse
import tftp

# Configuring arguments parser
parser = argparse.ArgumentParser()
parser.add_argument('-p', '--port', dest='port', type=int,  default=6969, help='indique le numéro de port du serveur (par défaut, 6969).')
parser.add_argument('-t', "--timeout", dest='timeout', type=int, default=2, help="indique le délai en secondes à partir duquel on considère que l'envoi ou la réception échoue (par défaut, 2).")
parser.add_argument('-c', '--cwd', dest='cwd', type=str, default='', help='permet de changer le répertoire courant dans lequel les fichiers (avec des chemins relatifs) sont lus ou écrits.')
parser.add_argument('--thread', type=bool, default=False, help='indique au serveur de traiter des requêtes clientes en parallèle, en déléguant chaque transfert de fichier à un thread particulier côté serveur (par défaut, False).')
args = parser.parse_args()

# change current working directory
if args.cwd != '': os.chdir(args.cwd)

# run main server loop
tftp.runServer(('', args.port), args.timeout, args.thread)

# EOF