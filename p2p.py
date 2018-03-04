import socket, select, pickle, threading
import block
from block import Block
from enum import Enum

class MessageType(Enum):
    QUERY_LATEST_BLOCK = 0
    QUERY_ALL = 1
    RESPONSE_BLOCKCHAIN = 2

class Message:
    def __init__(self, message_type, message_data, reply_addr):
        self.type = message_type
        self.data = message_data
        self.reply_addr = reply_addr

class P2P:
    def __init__(self, node, socket):
        self.p2p_addr = ('', socket)
        self.node = node
        self.peer_sockets = {}
        self.p2p_socket = None

    def add_peer(self, peer_addr):
        if peer_addr in self.peer_sockets:
            return False
        else:
            threading.Thread(
                    target = self.send_message,
                    args = (peer_addr, Message(MessageType.QUERY_LATEST_BLOCK, '', self.p2p_addr))
            ).start()
            return True

    def broadcast_latest(self):
        """Broadcasts the latest block in the chain to connected peers, which
        will request the entire chain if needed"""
        for peer_addr in self.peer_sockets:
            threading.Thread(
                    target = self.send_message,
                    args = (peer_addr, Message(MessageType.RESPONSE_BLOCKCHAIN, [self.node.get_latest_block()], self.p2p_addr))
            ).start()

    def send_message(self, peer_addr, data):
        """Sends a message with provided data to a given address, opening a new
        p2p socket if neccesary"""
        try:
            if not peer_addr in self.peer_sockets or True:
                peer_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                peer_socket.connect(peer_addr)
                self.peer_sockets[peer_addr] = peer_socket
            else:
                peer_socket = self.peer_sockets[peer_addr]
                peer_socket.connect(peer_addr)
            peer_socket.send(pickle.dumps(data))
        except ConnectionRefusedError:
            pass

    def process_response_chain(self, message):
        """Given a message with blockchain response, validates the result and
        either updates the local blockchain, requests more data, or rejects
        the response chain"""
        received_chain = message.data
        if len(received_chain) == 0:
            print('Received zero-length chain from {}'.format(message.reply_addr[1]))
            return

        latest_received_block = received_chain[len(received_chain) - 1]
        try:
            block.validate_block_types(latest_received_block)
        except ValueError:
            print('Received invalid chain from {}'.format(message.reply_addr[1]))
            return

        current_latest_block = self.node.get_latest_block()
        if latest_received_block.index > current_latest_block.index:
            if latest_received_block.prev_hash == current_latest_block.hash:
                self.node.add_block(latest_received_block)
                print('Received one block from {}'.format(message.reply_addr[1]))
                self.broadcast_latest()
            elif len(received_chain) == 1:
                threading.Thread(
                        target = self.send_message,
                        args = (message.reply_addr, Message(MessageType.QUERY_ALL, '', self.p2p_addr))
                ).start()
                print('Chain far behind {}, requesting entire chain'.format(message.reply_addr[1]))
            elif self.node.replace_blockchain(received_chain):
                print('Received updated chain from {}'.format(message.reply_addr[1]))
                self.broadcast_latest()
        else:
            print('Received chain from {} not longer than current chain'.format(message.reply_addr[1]))

    def start(self):
        self.p2p_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.p2p_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.p2p_socket.bind(self.p2p_addr)
        self.p2p_socket.listen(5)
        while True:
            conn_socket, addr = self.p2p_socket.accept()

            message = conn_socket.recv(4096)
            message = pickle.loads(message)

            peer_addr = (addr[0], message.reply_addr[1])
            message.reply_addr = peer_addr
            if not peer_addr in self.peer_sockets:
                threading.Thread(
                        target = self.send_message,
                        args = (peer_addr, Message(MessageType.QUERY_LATEST_BLOCK, '', self.p2p_addr))
                ).start()

            if message.type == MessageType.RESPONSE_BLOCKCHAIN:
                self.process_response_chain(message)
            elif message.type == MessageType.QUERY_ALL:
                print('Dispatching all blocks to {}'.format(message.reply_addr[1]))
                threading.Thread(
                        target = self.send_message,
                        args = (peer_addr, Message(MessageType.RESPONSE_BLOCKCHAIN, self.node.get_blockchain(), self.p2p_addr))
                ).start()
            elif message.type == MessageType.QUERY_LATEST_BLOCK:
                print('Dispatching latest block to {}'.format(message.reply_addr[1]))
                threading.Thread(
                        target = self.send_message,
                        args = (peer_addr, Message(MessageType.RESPONSE_BLOCKCHAIN, [self.node.get_latest_block()], self.p2p_addr))
                ).start()

        self.p2p_socket.close()
