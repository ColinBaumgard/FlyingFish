import socket

a = socket.gethostbyname_ex(socket.gethostname())[2]

print(a)