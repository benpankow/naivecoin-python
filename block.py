import hashlib

class Block:
    def __init__(self, index, data, timestamp, hash, prev_hash):
        self.index = index
        self.data = data
        self.timestamp = timestamp
        self.hash = hash
        self.prev_hash = prev_hash

    def calculate_hash(self):
        """Shortcut method to calculate the hash for this block"""
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

def calculate_hash(index, data, timestamp, prev_hash):
    """Calculates the hash for a block that would contain the passed attributes"""
    to_hash = str(index) + str(prev_hash) + str(timestamp) + data
    to_hash = to_hash.encode('utf-8')
    return hashlib.sha256(to_hash).hexdigest()

def validate_block_types(block):
    """Returns whether all of the types in the given block are correct"""
    return (
            type(block.index) == int
            and type(block.data) == str
            and type(block.timestamp) == int
            and type(block.hash) == str
            and type(block.prev_hash) == str
    )

def validate_genesis_block(block):
    """Makes sure a given genesis block matches the preset, raises a ValueError
    if this is not the case"""
    if not genesis_block == block:
        raise ValueError('Invalid genesis block')

def validate_block(block, prev_block):
    """Validates a given non-genesis block, raising a ValueError if a problem
    is found"""
    if not validate_block_types(block):
        raise ValueError('Block types invalid')
    elif block.index != prev_block.index + 1:
        raise ValueError('Invalid block index')
    elif block.prev_hash != prev_block.hash:
        raise ValueError('Invalid previous hash')
    elif block.calculate_hash() != block.hash:
        raise ValueError('Invalid hash')

def validate_blockchain(chain):
    """When given a blockchain, validates that all blocks are valid, raising
    a ValueError if an inconsistency or other problem is found"""
    if len(chain) < 1:
        raise ValueError('Zero-length blockchain')
    validate_genesis_block(chain[0])
    for i in range(1, len(chain)):
        validate_block(chain[i], chain[i - 1])

genesis_block = Block(
    0,
    'Genesis Block',
    1519415703,
    'c131a06110cc8d2f43c046c542ab4778d25f202aaa376e220e8371332cbff4fe',
    None
)
