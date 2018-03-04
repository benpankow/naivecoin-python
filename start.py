from node import Node
from webinterface import WebInterface
import threading

def main():
    socket_num = int(input('Node socket: '))
    node = Node(socket_num)
    interface = WebInterface(node, socket_num + 1)
    threading.Thread(
            target = interface.start,
            args = (None,)
    ).start()
    print('Node running on socket {}, web interface accessible at localhost:{}'.format(socket_num, socket_num + 1))
    node.start()

if __name__ == '__main__':
    main()
