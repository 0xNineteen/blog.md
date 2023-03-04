import hashlib


def hexhash(x):
    if type(x) != list:
        x = [x]
    m = hashlib.sha256()
    for _x in x:
        m.update(_x)
    y = m.hexdigest()
    return y


def hash(x):
    if type(x) != list:
        x = [x]
    m = hashlib.sha256()
    for _x in x:
        m.update(_x)
    y = m.digest()
    return y


class MerkleTree:
    def __init__(self) -> None:
        self.leafs = []
        self.merkle_tree = []

    @property
    def root(self):
        self.commit()
        if len(self.merkle_tree) == 0:
            return bytes(0)
        root = self.merkle_tree[-1]
        assert len(root) == 1
        return bytes(root[0])

    def insert(self, x):
        self.leafs.append(x)

    def commit(self):
        # builds the merkle tree

        # self.merkle_tree[0] = lowest level
        # self.merkle_tree[1] = 2nd-lowest level
        # ...
        # self.mt[0][0, 1] =parent=> self.mt[1][0]
        # self.mt[0][2, 3] =parent=> self.mt[1][1]

        # self.mt[j-1][(2i), (2i + 1)] =parent=> self.mt[j][i]
        if len(self.leafs) == 0:
            return

        self.merkle_tree = []  # clear
        y = [hash(x) for x in self.leafs]

        # note: this is an unordered merkle tree so different insertions = different state root
        # we can order the hashes though and get a sorted/consistent merkle tree
        # note: this is O(nlogn) but can probs get O(logn) if we do it on insertion
        y.sort()

        self.merkle_tree.append(y)
        while len(y) > 1:
            parents = []
            for i in range(0, len(y), 2):
                if (i + 1) == len(y):
                    children = y[i]
                else:
                    children = [y[i], y[i + 1]]
                print(children)
                parent = hash(children)
                parents.append(parent)
            y = parents
            self.merkle_tree.append(y)


import leveldb
import os
import shutil


class DB:
    def __init__(self, dbfile, resume=True):
        if not resume and os.path.exists(dbfile):
            # delete the db directory
            shutil.rmtree(dbfile)

        self.db = leveldb.LevelDB(dbfile)

    def get(self, key):
        try:
            return self.db.Get(key)
        except:
            return ""

    def put(self, key, value):
        return self.db.Put(key, value)

    def delete(self, key):
        return self.db.Delete(key)


from dataclasses import dataclass
from copy import deepcopy
import json


@dataclass
class Block:
    parent_hash: bytes
    state_root: bytes
    block_hash: bytes = None

    def __post_init__(self):
        self.block_hash = hash([self.parent_hash, self.state_root])


@dataclass
class Transaction:
    address: str
    amount: int

    def hash(self):
        return hash([bytes(self.address, "utf-8"), bytes(self.amount)])

    def serialize(self):
        return bytes(json.dumps(self.__dict__), "utf-8")

    @staticmethod
    def deserialize(data):
        data = json.loads(data.decode("utf-8"))
        tx = Transaction(data["address"], data["amount"])
        return tx


@dataclass
class Account:
    address: str
    amount: int

    def hash(self):
        return hexhash([bytes(self.address, "utf-8"), bytes(self.amount)])

    def hash_bytes(self):
        return bytes(self.hash(), "utf-8")

    def apply(self, tx: Transaction):
        assert self.address == tx.address
        self.amount = tx.amount
        return self

    def serialize(self):
        return bytes(json.dumps(self.__dict__), "utf-8")

    @staticmethod
    def deserialize(data):
        data = json.loads(data.decode("utf-8"))
        tx = Account(data["address"], data["amount"])
        return tx


if __name__ == "__main__":
    tree = MerkleTree()
    tree.insert(b"hi")
    tree.insert(b"there")
    tree.commit()
    root1 = tree.root

    tree = MerkleTree()
    tree.insert(b"there")
    tree.insert(b"hi")
    tree.commit()
    root2 = tree.root
    root2 == root1

    data = Transaction("dog", 10).serialize()
    tx = Transaction.deserialize(data)

    # state = State()
    # state.process_tx(tx)
    # data = state.serialize()
    # state = state.deserialize(data)

    # db = DB("tmp.db")
    # state = State()
    # tree = MerkleTree()
    # state_root = tree.root
    # genesis = Block(bytes(0), state_root)

    # db.put(state_root, state.serialize())

    # state = db.get(state_root)
    # state = State.deserialize(state)
    # state
