import socket, select, pickle
from block import *
from enum import Enum

class MessageType(Enum):
    QUERY_LATEST_BLOCK = 0
    QUERY_ALL = 1
    RESPONSE_BLOCKCHAIN = 2

class Message():
    def __init__(self, message_type, message_data, reply_port):
        self.type = message_type
        self.data = message_data
        self.reply_port = reply_port

socket_num = int(input('Base socket: '))

control_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
control_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
control_socket.bind(('', socket_num))
control_socket.listen(1)

p2p_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
p2p_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
p2p_socket.bind(('', socket_num + 1))
p2p_socket.listen(1)

poll = select.poll()
poll.register(control_socket.fileno())
poll.register(p2p_socket.fileno())

peer_sockets = []

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
            elif endpoint == b'/mine':
                conn_socket.send(b'HTTP/1.0 200 OK\r\n\r\n')
                new_block = create_next_block('test')
                conn_socket.send(str(new_block).encode())
            elif b'/add-peer/' in endpoint:
                peer_socket_num = int(endpoint[len(b'/add-peer/'):].decode())

                peer_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                peer_socket.connect(('', peer_socket_num))
                peer_sockets.append(peer_socket)
                peer_socket.send(pickle.dumps(Message(MessageType.QUERY_ALL, '', socket_num + 1)))
                print(peer_socket)

                conn_socket.send('Connected to peer {}'.format(socket_num).encode())
            conn_socket.close()
        except IOError:
            conn_socket.close()
    else:
        conn_socket, addr = p2p_socket.accept()

        message = conn_socket.recv(4096)
        message = pickle.loads(message)
        if message.type == MessageType.RESPONSE_BLOCKCHAIN:
            if (replace_blockchain(message.data)):
                print('Got longer chain!')
            else:
                print('Got worse chain')
        elif message.type == MessageType.QUERY_ALL:
            print('doot doot')
            print(addr)
            print(conn_socket)
            peer_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            peer_socket.connect((addr[0], message.reply_port))
            peer_socket.send(pickle.dumps(Message(MessageType.QUERY_LATEST_BLOCK, '', socket_num + 1)))

        elif message.type == MessageType.QUERY_LATEST_BLOCK:
            print('deet')
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
