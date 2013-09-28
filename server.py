import socket
import checkers

# Using localhost will be faster but only allow accessing locally
# If you want access from other computers use socket.gethostname()
HOST = 'localhost'
PORT = 8081

print('Starting server on host %s port %s' % (HOST, PORT))
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

s.bind((HOST, PORT))
s.listen(2)

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
  return (command, details)

connections = []

while len(connections) < 2:
  print('Waiting for 2 connections. Currently have %s' % len(connections))
  conn, addr = s.accept()
  print('Connected to from', addr)
  connections.append(SimpleSocket(conn))

print('All players connected')

turn = 0
while 1:
  data = connections[turn].read_line()
  turn = 1 - turn
  if not data: break
  print(data)

for c in connections:
  c.close()

s.close()
