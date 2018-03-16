from node import Node
from web_interface import WebInterface
import threading

def main():
    socket_num = int(input('Node socket: '))
    node = Node(socket_num)
    interface = WebInterface(node, socket_num + 1)
    interface.start()
    threading.Thread(
            target = node.start,
            args = (None,)
    ).start()
    print('Node running on socket {}, web interface accessible at localhost:{}'.format(socket_num, socket_num + 1))

if __name__ == '__main__':
    main()
