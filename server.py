#!/usr/bin/env python3
import socket
import random

import ipc
import checkers

random.seed()

# Using localhost will be faster but only allow accessing locally
# If you want access from other computers use socket.gethostname()
HOST = 'localhost'
ATTEMPT_PORTS = range(8080, 8090)

def find_port(attempt_ports):
  s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  for port in attempt_ports:
    try:
      s.bind((HOST, port))
      return s, port
    except OSError:
      pass
  raise RuntimeError("Could not find open port")

serversocket, PORT = find_port(ATTEMPT_PORTS)

print('Starting server on host %s port %s' % (HOST, PORT))

serversocket.listen(2)

class ServerPlayer:
  def __init__(self, color, conn):
    self.color = color
    self.conn = conn

  def get_command(self):
    while 1:
      line = self.conn.read_line()
      if not line: return
      try:
        return ipc.parse_command(line)
      except ValueError:
        self.conn.write_line('REJECTED:Unparseable command')

  def show_player(self, line):
    self.conn.write_line(line)

connections = []

while len(connections) < 2:
  print('Waiting for 2 connections. Currently have %s' % len(connections))
  conn, addr = serversocket.accept()
  print('Connected to from', addr)
  connections.append(ipc.SimpleSocket(conn))

print('All players connected')
random.shuffle(connections)
players = []

board_size = 8
board_rows = 3
for (c, turn, color) in zip(connections, ('first', 'second'), (checkers.Color.RED, checkers.Color.BLACK)):
  players.append(ServerPlayer(color, c))
  c.write_line('GAMESTART:board_size=%s,board_rows=%s,turn=%s,color=%s' \
    % (board_size, board_rows, turn, color))

if players[0].color != checkers.Color.RED:
  players.reverse()

board = checkers.CheckerBoard(board_size, board_rows)
game = checkers.CheckerGame(board, players)

game.play()

for c in connections:
  c.close()

serversocket.close()
