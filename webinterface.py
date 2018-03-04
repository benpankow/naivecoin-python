import socket, select, pickle, threading

class WebInterface:

    def __init__(self, node, socket):
        self.socket = socket
        self.node = node
        self.control_socket = None

    def start(self, _):
        self.control_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.control_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.control_socket.bind(('', self.socket))
        self.control_socket.listen(1)

        while True:
            conn_socket, addr = self.control_socket.accept()
            try:
                message = conn_socket.recv(1024)
                endpoint = message.split()[1]
                if endpoint == b'/' or endpoint == b'/blocks':
                    conn_socket.send(b'HTTP/1.0 200 OK\r\n\r\n')
                    for block in self.node.get_blockchain():
                        conn_socket.send(str(block).encode())
                elif endpoint == b'/mine':
                    conn_socket.send(b'HTTP/1.0 200 OK\r\n\r\n')
                    new_block = self.node.create_next_block('test')
                    conn_socket.send(str(new_block).encode())
                    self.node.p2p.broadcast_latest()
                elif endpoint == b'/peers':
                    conn_socket.send(b'HTTP/1.0 200 OK\r\n\r\n')
                    peers = ['{}:{}'.format(key[0], key[1]) for key in self.node.p2p.peer_sockets.keys()]
                    conn_socket.send(('Connected peers:\n' + '\n'.join(peers)).encode())
                elif b'/add-peer/' in endpoint:
                    conn_socket.send(b'HTTP/1.0 200 OK\r\n\r\n')
                    ip_and_port = endpoint[len(b'/add-peer/'):].decode()
                    ip, port = ip_and_port.split('/')
                    peer_addr = (ip, int(port))

                    if self.node.p2p.add_peer(peer_addr):
                        conn_socket.send('Connected to peer {}'.format(peer_addr[1]).encode())
                    else:
                        conn_socket.send('Already connected to peer {}'.format(peer_addr[1]).encode())

                conn_socket.close()
            except IOError:
                conn_socket.close()
        control_socket.close()
