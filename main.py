import socket, select, pickle
from block import *

control_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
control_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
control_socket.bind(('', 8000))
control_socket.listen(1)

p2p_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
p2p_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
p2p_socket.bind(('', 5000))
p2p_socket.listen(1)

poll = select.poll()
poll.register(control_socket.fileno())
poll.register(p2p_socket.fileno())

while True:
    fd = poll.poll()
    while type(fd) is tuple or type(fd) is list:
        fd = fd[0]

    if fd == control_socket.fileno():
        conn_socket, addr = control_socket.accept()
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
    else:
        conn_socket, addr = p2p_socket.accept()
        message = conn_socket.recv(4096)
        if len(message) > 2:
            message_type = int(chr(message[0]))
            message = message[2:]
            print(message_type)
            if message_type == 2:
                block_list = pickle.loads(message)
                if (replace_blockchain(block_list)):
                    print('Got longer chain!')
                else:
                    print('Got worse chain')
    '''conn_socket, addr = control_socket.accept()
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

    conn_socket, addr = p2p_socket.accept()'''

p2p_socket.close()
control_socket.close()
