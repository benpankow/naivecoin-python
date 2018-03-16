import datetime
import block
from block import Block
from p2p import P2P

class Node:
    def __init__(self, socket):
        self.socket = socket
        self.blockchain = [ block.genesis_block ]
        self.p2p = P2P(self, socket)

    def start(self, _):
        self.p2p.start()

    def set_blockchain(self, new_blockchain):
        self.blockchain = new_blockchain

    def get_blockchain(self):
        return self.blockchain

    def get_latest_block(self):
        return self.get_blockchain()[-1]

    def add_block(self, new_block):
        """Attempts to add a block to the end of the block chain, returns whether
        this was successful"""
        try:
            block.validate_block(new_block, self.get_latest_block())
        except ValueError:
            return False

        self.get_blockchain().append(new_block)
        return True

    def create_next_block(self, next_data):
        """Mines the next block and appends it to the end of the blockchain. Does
        not broadcast to other nodes, that must be handled seperately"""
        prev_block = self.get_latest_block();
        next_index = prev_block.index + 1
        next_timestamp = int(datetime.datetime.now().timestamp())
        next_hash = block.calculate_hash(next_index, next_data, next_timestamp, prev_block.hash)

        new_block = Block(next_index, next_data, next_timestamp, next_hash, prev_block.hash)

        self.add_block(new_block)
        return new_block


    def replace_blockchain(self, new_blockchain):
        """Attempts to replace the existing blockchain with a new one, returns True
        if this succeeds and returns False if there is a problem with the passed
        blockchain"""
        try:
            block.validate_blockchain(new_blockchain)

            current_blockchain = self.get_blockchain()
            if len(new_blockchain) > len(current_blockchain):
                self.set_blockchain(new_blockchain)
                return True
            else:
                return False
        except ValueError:
            return False
