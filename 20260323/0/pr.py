import socket, http.server
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.connect(("1.1.1.1", 80))
print(s)

s.close()

http.server.test(http.server.SimpleHTTPRequestHandler)

