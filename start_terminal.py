from node import Node
from terminal_interface import TerminalInterface
import threading

def main():
    socket_num = int(input('Node socket: '))
    node = Node(socket_num)
    interface = TerminalInterface(node)
    interface.start()
    threading.Thread(
            target = node.start,
            args = (None,)
    ).start()
    print('Node running on socket {}'.format(socket_num, socket_num + 1))

if __name__ == '__main__':
    main()
