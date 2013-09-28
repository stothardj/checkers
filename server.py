import socket
import checkers

# Using localhost will be faster but only allow accessing locally
# If you want access from other computers use socket.gethostname()
HOST = 'localhost'
PORT = 8080

print('Starting server on host %s port %s' % (HOST, PORT))
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

s.bind((HOST, PORT))
s.listen(2)

class SocketSource:
  def __init__(self, conn):
    self.conn = conn

  def read(self):
    return self.conn.recv(1024)

# Given a source on which you can call "read" to retrieve some amount
# of data as a byte array, LineReader provides a simple read functionality. Source
# should return None when it is empty
class LineReader:
  def __init__(self, source):
    self.source = source
    self.remaining = b''

  def read_line(self):
    newline_pos = self.remaining.find(b'\n')
    while newline_pos == -1:
      self.remaining += self.source.read()
      newline_pos = self.remaining.find(b'\n')
    ret = self.remaining[0:newline_pos]
    if ret[-1:] == b'\r':
      ret = ret[:-1]
    self.remaining = self.remaining[newline_pos+1:]
    return ret

while 1:
  print('Waiting for connections')
  conn, addr = s.accept()
  print('Connected to from', addr)
  lr = LineReader(SocketSource(conn))
  while 1:
    data = lr.read_line()
    if not data: break
    print(data.decode())
  conn.close()

s.close()
