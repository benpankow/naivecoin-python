import socket, select, pickle, threading

class TerminalInterface:

    def __init__(self, node):
        self.node = node

    def start(self):
        while True:
            message = input('> ').strip()
            if message == 'view':
                for block in self.node.get_blockchain():
                    print(str(block))
            elif message == 'mine':
                new_block = self.node.create_next_block('test')
                print(str(new_block))
                self.node.p2p.broadcast_latest()
            elif message == 'peers':
                peers = ['{}:{}'.format(key[0], key[1]) for key in self.node.p2p.peer_sockets.keys()]
                print(('Connected peers:\n' + '\n'.join(peers)))
            elif len(message) > 4 and message[:4] == 'add ':
                ip_and_port = message[4:]
                ip, port = ip_and_port.split(':')
                peer_addr = (ip, int(port))
                print(peer_addr)

                if self.node.p2p.add_peer(peer_addr):
                    print('Connected to peer {}'.format(peer_addr[1]))
                else:
                    print('Already connected to peer {}'.format(peer_addr[1]))
            else:
                print('No command with name \'{}\' found'.format(message))
            print('')
