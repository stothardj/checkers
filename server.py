#!/usr/bin/env python3
import socket
import random

import checkers

random.seed()

# Using localhost will be faster but only allow accessing locally
# If you want access from other computers use socket.gethostname()
HOST = 'localhost'
ATTEMPT_PORTS = range(8080, 8090)

def find_port(attempt_ports):
  for port in attempt_ports:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
      s.bind((HOST, port))
      return s, port
    except OSError:
      pass
  raise RuntimeError("Could not find open port")

serversocket, PORT = find_port(ATTEMPT_PORTS)

print('Starting server on host %s port %s' % (HOST, PORT))

serversocket.listen(2)

# A data source from a socket. Converts the byte array to a string before
# returning it.
class SocketSource:
  def __init__(self, conn):
    self.conn = conn

  def read(self):
    data = self.conn.recv(1024)
    if data:
      return data.decode()
    return data

# Given a source on which you can call "read" to retrieve some amount
# of data as a string, LineReader provides a simple read_line functionality.
# Source should return None when it is empty. read_line will return when
# the source has indicated it is empty for all subsequent calls.
class LineReader:
  def __init__(self, source):
    self.source = source
    self.remaining = ''
    self.closed = False

  def read_line(self):
    if self.closed:
      return None
    newline_pos = self.remaining.find('\n')
    while newline_pos == -1:
      new_text = self.source.read()
      if not new_text:
        self.closed = True
        if self.remaining == '':
          return None
        return self.remaining
      self.remaining += new_text
      newline_pos = self.remaining.find('\n')
    ret = self.remaining[0:newline_pos]
    if ret[-1] == '\r':
      ret = ret[:-1]
    self.remaining = self.remaining[newline_pos+1:]
    return ret

# Wraps a socket to hide the annoying details and lack of guarentees
class SimpleSocket:
  def __init__(self, conn):
    self.conn = conn
    self.lr = LineReader(SocketSource(conn))

  # Reads a line from the socket. Returns None if connection is broken
  def read_line(self):
    return self.lr.read_line()

  # Writes a line to the socket. Appends a newline to msg so DON'T put it in
  # there yourself. msg should be a string. Will encode into bytes for you.
  # Returns True on Success, False on fail (socket is closed)
  def write_line(self, msg):
    msg += '\n'
    msg = msg.encode()
    to_send = len(msg)
    total_sent = 0
    while total_sent < to_send:
      sent = self.conn.send(msg[total_sent:])
      if sent == None:
        return False
      total_sent += sent
    return True

  def close(self):
    self.conn.close()

def parse_command(s):
  (command, colon, details) = s.partition(':')
  if colon == '':
    raise ValueError("Command %s did not contain colon. Not a valid command" % s)
  return command, details

class ServerPlayer:
  def __init__(self, color, conn):
    self.color = color
    self.conn = conn

  def get_command(self):
    while 1:
      line = self.conn.read_line()
      if not line:
        return
      try:
        return parse_command(line)
      except ValueError:
        self.conn.write_line('REJECTED:Unparseable command')

connections = []

while len(connections) < 2:
  print('Waiting for 2 connections. Currently have %s' % len(connections))
  conn, addr = serversocket.accept()
  print('Connected to from', addr)
  connections.append(SimpleSocket(conn))

print('All players connected')
random.shuffle(connections)
players = []

board_size = 8
board_rows = 3
for (c, turn, color) in zip(connections, ('first', 'second'), (checkers.Color.RED, checkers.Color.BLACK)):
  players.append(ServerPlayer(color, c))
  c.write_line('GAMESTART:board_size=%s,board_rows=%s,turn=%s,color=%s' \
    % (board_size, board_rows, turn, color))

board = checkers.CheckerBoard(board_size, board_rows)
game = checkers.CheckerGame(board, checkers.Color.RED, players)

print(game.board)
while game.take_turn():
  print(game.board)

for c in connections:
  c.close()

serversocket.close()
