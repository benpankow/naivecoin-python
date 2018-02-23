import socket
from block import *

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock.bind(('', 12006))
sock.listen(1)

while True:
    conn_socket, addr = sock.accept()
    try:
        message = conn_socket.recv(1024)
        endpoint = message.split()[1]
        if endpoint == b'/' or endpoint == b'/blocks':
            conn_socket.send(b'HTTP/1.0 200 OK\r\n\r\n')
            for block in get_blockchain():
                conn_socket.send(str(block).encode())
        if endpoint == b'/mine':
            conn_socket.send(b'HTTP/1.0 200 OK\r\n\r\n')
            new_block = create_next_block('test')
            conn_socket.send(str(new_block).encode())
        conn_socket.close()
    except IOError:
        conn_socket.close()
sock.close()
