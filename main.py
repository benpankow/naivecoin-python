import socket, select, pickle, threading
from block import *
from enum import Enum

class MessageType(Enum):
    QUERY_LATEST_BLOCK = 0
    QUERY_ALL = 1
    RESPONSE_BLOCKCHAIN = 2

class Message():
    def __init__(self, message_type, message_data, reply_addr):
        self.type = message_type
        self.data = message_data
        self.reply_addr = reply_addr

peer_sockets = {}

def broadcast_latest():
    global peer_sockets
    for peer_addr in peer_sockets:
        threading.Thread(
                target = send_message,
                args = (peer_addr, Message(MessageType.RESPONSE_BLOCKCHAIN, [get_latest_block()], p2p_addr))
        ).start()

def send_message(peer_addr, data):
    global peer_sockets
    if not peer_addr in peer_sockets or True:
        peer_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        peer_socket.connect(peer_addr)
        peer_sockets[peer_addr] = peer_socket
    else:
        peer_socket = peer_sockets[peer_addr]
        peer_socket.connect(peer_addr)
    peer_socket.send(pickle.dumps(data))

def process_response_chain(message):
    global peer_sockets
    received_chain = message.data
    if len(received_chain) == 0:
        print('Received zero-length chain from {}'.format(message.reply_addr[1]))
        return

    latest_received_block = received_chain[len(received_chain) - 1]
    try:
        validate_block_types(latest_received_block)
    except ValueError:
        print('Received invalid chain from {}'.format(message.reply_addr[1]))
        return

    current_latest_block = get_latest_block()
    if latest_received_block.index > current_latest_block.index:
        if latest_received_block.prev_hash == current_latest_block.hash:
            add_block(latest_received_block)
            print('Received one block from {}'.format(message.reply_addr[1]))
            broadcast_latest()
        elif len(received_chain) == 1:
            threading.Thread(
                    target = send_message,
                    args = (message.reply_addr, Message(MessageType.QUERY_ALL, '', p2p_addr))
            ).start()
            print('Chain far behind {}, requesting entire chain'.format(message.reply_addr[1]))
        elif replace_blockchain(received_chain):
            print('Received updated chain from {}'.format(message.reply_addr[1]))
            broadcast_latest()
    else:
        print('Received chain from {} not longer than current chain'.format(message.reply_addr[1]))


def main():
    global p2p_addr, peer_sockets
    socket_num = int(input('Base socket: '))

    control_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    control_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    control_socket.bind(('', socket_num))
    control_socket.listen(1)

    p2p_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    p2p_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    p2p_addr = ('', socket_num + 1)
    p2p_socket.bind(p2p_addr)
    p2p_socket.listen(5)

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
                elif endpoint == b'/mine':
                    conn_socket.send(b'HTTP/1.0 200 OK\r\n\r\n')
                    new_block = create_next_block('test')
                    conn_socket.send(str(new_block).encode())
                    broadcast_latest()
                elif endpoint == b'/peers':
                    conn_socket.send(b'HTTP/1.0 200 OK\r\n\r\n')
                    conn_socket.send(', '.join(peer_sockets.keys()).encode())
                elif b'/add-peer/' in endpoint:
                    conn_socket.send(b'HTTP/1.0 200 OK\r\n\r\n')
                    peer_addr = ('', int(endpoint[len(b'/add-peer/'):].decode()))

                    if not peer_addr in peer_sockets:
                        threading.Thread(
                                target = send_message,
                                args = (peer_addr, Message(MessageType.QUERY_LATEST_BLOCK, '', p2p_addr))
                        ).start()
                        conn_socket.send('Connected to peer {}'.format(peer_addr[1]).encode())
                    else:
                        conn_socket.send('Already connected to peer {}'.format(peer_addr[1]).encode())
                conn_socket.close()
            except IOError:
                conn_socket.close()
        else:
            conn_socket, addr = p2p_socket.accept()

            message = conn_socket.recv(4096)
            message = pickle.loads(message)

            peer_addr = message.reply_addr
            if not peer_addr in peer_sockets:
                threading.Thread(
                        target = send_message,
                        args = (peer_addr, Message(MessageType.QUERY_LATEST_BLOCK, '', p2p_addr))
                ).start()

            if message.type == MessageType.RESPONSE_BLOCKCHAIN:
                process_response_chain(message)
            elif message.type == MessageType.QUERY_ALL:
                print('Dispatching all blocks to {}'.format(message.reply_addr[1]))
                threading.Thread(
                        target = send_message,
                        args = (peer_addr, Message(MessageType.RESPONSE_BLOCKCHAIN, get_blockchain(), p2p_addr))
                ).start()
            elif message.type == MessageType.QUERY_LATEST_BLOCK:
                print('Dispatching latest block to {}'.format(message.reply_addr[1]))
                threading.Thread(
                        target = send_message,
                        args = (peer_addr, Message(MessageType.RESPONSE_BLOCKCHAIN, [get_latest_block()], p2p_addr))
                ).start()

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

if __name__ == '__main__':
    main()
