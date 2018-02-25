import socket, pickle
from block import *
from enum import Enum

class MessageType(Enum):
    QUERY_LATEST_BLOCK = 0
    QUERY_ALL = 1
    RESPONSE_BLOCKCHAIN = 2

class Message():
    def __init__(self, message_type, message_data):
        self.type = message_type
        self.data = message_data

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect(('', 5000))
create_next_block('test')
dump = pickle.dumps(Message(MessageType.RESPONSE_BLOCKCHAIN, get_blockchain()))
client_socket.send(dump)
