#!/usr/bin/env python3
import socket
import argparse

parser = argparse.ArgumentParser(description = 'Terminal checkers client')
parser.add_argument('--hostname', default='localhost')
parser.add_argument('-p', '--port', default=8080)

args = parser.parse_args()

print(args.port)
