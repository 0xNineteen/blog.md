from radix16 import _insert, Node
from account import Account
from dataclasses import dataclass

import hashlib

# need 16-bit radix 
# create tree with values 
# create hashes by traversing the tree 

@dataclass
class Block: 
    state_root: any

# extend radix node for merkle things
class MerkleNode(Node): 

    @staticmethod
    def default(): 
        return MerkleNode(None, None, [None] * 16)

    @staticmethod
    def deserialize(data):
        node = MerkleNode.default()
        node.children = data['children']
        node.key = data['key']
        node.value = data['value']
        return node

    # traverse tree and insert all accounts in a database
    def commit(self, db): 
        m = hashlib.sha256()
        serialized = {}

        if self.key:
            m.update(bytes(self.key, 'utf-8'))
        serialized['key'] = self.key

        if self.value:
            m.update(bytes(self.value, 'utf-8'))
        serialized['value'] = self.value

        child_digests = []
        for child in self.children: 
            child: MerkleNode
            if child: 
                child_digest = child.commit(db) # recursive call
                m.update(bytes.fromhex(child_digest))
                child_digests.append(child_digest)

        serialized['children'] = child_digests

        ## in prod would store the bytes (not the obj directly)
        # serialized = bytes(json.dumps(serialized), 'utf-8')

        digest = m.hexdigest()[:16]
        db[digest] = serialized

        return digest

# init the tree
TREE = MerkleNode.default()

def insert(key: str, value: any):
    print(f'COMMAND: insert({key}, {value})')
    _insert(TREE, key, value)
    print('')

db = {} # manage accounts 

account = Account(100, 'ball')
digest = account.digest16()
insert(account.address, digest)
db[digest] = account.serialize()

account = Account(20, 'abc')
digest = account.digest16()
insert(account.address, digest)
db[digest] = account.serialize()

account = Account(22, 'abcde')
digest = account.digest16()
insert(account.address, digest)
db[digest] = account.serialize()

state_root = TREE.commit(db)
block0 = Block(state_root)

print(block0)
TREE.print()
# print(db)

def get_account(address, state_root, db): 
    node = MerkleNode.deserialize(db[state_root]) # lookup state / tree root

    # helper fcn iterating over children
    def search_children(node, address):
        for digest in node.children: 
            child = MerkleNode.deserialize(db[digest])

            if child.key == address: 
                return child, address, True # search is done

            if child.key in address: 
                address = address[len(child.key):]
                return child, address, False # continue search

        return None # dne

    # parse the tree for the address 
    steps = 0
    while 1:
        result = search_children(node, address)
        steps += 1
        if result is None: # dne
            return None 

        (node, address, is_done) = result

        if is_done: 
            print(f"INFO: found account in {steps} steps...")
            account = Account.deserialize(db[node.value])
            return account

# account = get_account('abc', state_root, db)
account = get_account('abcde', state_root, db)
assert account.address == 'abcde'
assert account.amount == 22
print(account)

print("state0 size:", len(db))

# new block
account = Account(25, 'abcde')
digest = account.digest16()
insert(account.address, digest)
db[digest] = account.serialize()

# OPTIM: can optimize the commit process to only commit the log(N) updates on insert
state_root = TREE.commit(db) 
block1 = Block(state_root)

# db size goes from 7 => 11 
# need 1) new state_root 2) new child digest ('abc') 3) new account digest ('abcdef')
print("state1 size:", len(db)) 

# new data
account = get_account('abcde', block1.state_root, db)
assert account.address == 'abcde'
assert account.amount == 25

# rollback from different state root (fork data)
account = get_account('abcde', block0.state_root, db)
assert account.address == 'abcde'
assert account.amount == 22


print('----')