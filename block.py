import hashlib
import datetime

class Block:
    def __init__(self, index, data, timestamp, hash, prev_hash):
        self.index = index
        self.data = data
        self.timestamp = timestamp
        self.hash = hash
        self.prev_hash = prev_hash

    def calculate_hash(self):
        return calculate_hash(self.index, self.data, self.timestamp, self.prev_hash)

    def __eq__(self, other):
        return (
                self.index == other.index
                and self.data == other.data
                and self.timestamp == other.timestamp
                and self.hash == other.hash
                and self.prev_hash == other.prev_hash
        )

    def __str__(self):
        return 'Block {}:\n-data: {}\n-timestamp: {}\n-hash: {}\n-prev_hash: {}\n'.format(
            self.index,
            self.data,
            self.timestamp,
            self.hash,
            self.prev_hash
        )

def set_blockchain(new_blockchain):
    global blockchain
    blockchain = new_blockchain

def get_blockchain():
    return blockchain

def get_latest_block():
    return get_blockchain()[-1]

def calculate_hash(index, data, timestamp, prev_hash):
    to_hash = str(index) + str(prev_hash) + str(timestamp) + data
    to_hash = to_hash.encode('utf-8')
    return hashlib.sha256(to_hash).hexdigest()

def add_block(new_block):
    try:
        validate_block(new_block, get_latest_block())
    except ValueError:
        return False

    get_blockchain().append(new_block)
    return True

def create_next_block(next_data):
    prev_block = get_latest_block();
    next_index = prev_block.index + 1
    next_timestamp = int(datetime.datetime.now().timestamp())
    next_hash = calculate_hash(next_index, next_data, next_timestamp, prev_block.hash)

    new_block = Block(next_index, next_data, next_timestamp, next_hash, prev_block.hash)

    add_block(new_block)
    return new_block

def validate_block_types(block):
    return (
            type(block.index) == int
            and type(block.data) == str
            and type(block.timestamp) == int
            and type(block.hash) == str
            and type(block.prev_hash) == str
    )

def validate_genesis_block(block):
    if not genesis_block == block:
        raise ValueError('Invalid genesis block')

def validate_block(block, prev_block):
    if not validate_block_types(block):
        raise ValueError('Block types invalid')
    elif block.index != prev_block.index + 1:
        raise ValueError('Invalid block index')
    elif block.prev_hash != prev_block.hash:
        raise ValueError('Invalid previous hash')
    elif block.calculate_hash() != block.hash:
        raise ValueError('Invalid hash')

def validate_blockchain(chain):
    if len(chain) < 1:
        raise ValueError('Zero-length blockchain')
    validate_genesis_block(chain[0])
    for i in range(1, len(chain)):
        validate_block(chain[i], chain[i - 1])

def replace_blockchain(new_blockchain):
    try:
        validate_blockchain(new_blockchain)

        current_blockchain = get_blockchain()
        if len(new_blockchain) > len(current_blockchain):
            set_blockchain(new_blockchain)
            return True
        else:
            return False
    except ValueError:
        return False

genesis_block = Block(
    0,
    'Genesis Block',
    1519415703,
    'c131a06110cc8d2f43c046c542ab4778d25f202aaa376e220e8371332cbff4fe',
    None
)

blockchain = [ genesis_block ]
