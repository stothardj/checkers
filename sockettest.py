import socket

s = socket.socket(
  socket.AF_INET, socket.SOCK_STREAM)

# Using localhost will be faster but only allow accessing locally
# If you want access from other computers use socket.gethostname()
HOST = 'localhost'
PORT = 8080
s.bind((HOST, PORT))

s.listen(2)

while 1:
  print('Waiting for connections')
  conn, addr = s.accept()
  print('Connected to from', addr)
  while 1:
    data = conn.recv(1024)
    if not data: break
    print(data)
  conn.close()

s.close()
