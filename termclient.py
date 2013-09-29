#!/usr/bin/env python3
import socket
import argparse
import sys

import ipc
import checkers

parser = argparse.ArgumentParser(description = 'Terminal checkers client')
parser.add_argument('--hostname', default='localhost')
parser.add_argument('-p', '--port', default=8080, type=int)

args = parser.parse_args()

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((args.hostname, args.port))

conn = ipc.SimpleSocket(s)

# Represent the player at this keyboard
class HumanPlayer:
  def __init__(self, color, conn):
    self.color = color
    self.conn = conn

  def get_command(self):
    while 1:
      line = input()
      if not line: return
      try:
        ret = ipc.parse_command(line)
        self.conn.write_line(line)
        return ret
      except ValueError:
        print('Command will not parse successfully, refusing to send')

  def show_player(self, line):
    print(line)

# Represents the other player we are connected to from
# the server. We track their moves based on what the server
# tells us they did.
class RemotePlayer:
  def __init__(self, color, conn):
    self.color = color
    self.conn = conn

  def get_command(self):
    line = self.conn.read_line()
    if line:
      return ipc.parse_command(line)

  def show_player(self, line):
    pass

def quit():
  conn.close()
  sys.exit()

def parse_gamestart_details(details):
  r = {}
  for (k,_,v) in (kv.partition('=') for kv in details.split(',')):
    r[k] = v
  return r

gamestart = conn.read_line()
if not gamestart: quit()
print(gamestart)
command, details = ipc.parse_command(gamestart)
if 'GAMESTART' != command: quit()
game_opts = parse_gamestart_details(details)

def setup_game(game_opts):
  board_size = int(game_opts['board_size'])
  board_rows = int(game_opts['board_rows'])
  human = HumanPlayer(game_opts['color'], conn)
  remote = RemotePlayer(checkers.Color.other(game_opts['color']), conn)
  board = checkers.CheckerBoard(board_size, board_rows)
  players = [human, remote]
  if game_opts['turn'] == 'second':
    players.reverse()
  return checkers.CheckerGame(board, players)

game = setup_game(game_opts)

game.play()

conn.close()
