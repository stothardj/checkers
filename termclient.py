#!/usr/bin/env python3
import socket
import argparse

import ipc

parser = argparse.ArgumentParser(description = 'Terminal checkers client')
parser.add_argument('--hostname', default='localhost')
parser.add_argument('-p', '--port', default=8080)

args = parser.parse_args()

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((args.hostname, args.port))

conn = ipc.SimpleSocket(s)

def game_loop():
  while 1:
    # Read loop
    while 1:
      data = conn.read_line()
      if not data: return
      print(data)
      # TODO: Proper command parsing.
      # Enumerate cases where we need to read again
      if data.startswith('GAMESTART') and 'second' in data:
        continue
      if data.startswith('ACCEPTED'):
        continue
      # Otherwise we are done reading
      break
    # Write single response
    conn.write_line(input())

game_loop()
