import socket, pickle
from block import *

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect(('', 5000))
create_next_block('test')
dumpo = b'2 ' + pickle.dumps(get_blockchain())
client_socket.send(dumpo)
