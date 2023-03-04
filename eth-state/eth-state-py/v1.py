#%%
from utils import *

# dict state -> used in v1 and v2
class State:
    def __init__(self) -> None:
        self.state = {}  # address => account

    def process_tx(self, tx: Transaction):
        self.state[tx.address] = tx.amount

    def generate_merkle_tree(self) -> MerkleTree:
        tree = MerkleTree()
        for address, amount in self.state.items():
            tree.insert([bytes(address, "utf-8"), bytes(amount)])
        tree.commit()
        return tree

    def get(self, address):
        return self.state.get(address, None)

    def serialize(self):
        return bytes(json.dumps(self.state), "utf-8")

    @staticmethod
    def deserialize(data):
        data = json.loads(data.decode("utf-8"))
        state = State()
        state.state = data
        return state

    def __repr__(self) -> str:
        return self.state.__repr__()


class Blockchain:
    def __init__(self) -> None:
        self.db = DB("blocks.db", resume=False)
        self.state = State()
        state_root = self.state.generate_merkle_tree().root
        genesis = Block(bytes(0), state_root)
        self.db.put(state_root, self.state.serialize())

        # NOTE: this doesnt support forks
        self.chain = [genesis]

    def get_account(self, address):
        state = State.deserialize(self.db.get(self.chain[-1].state_root))
        return state.get(address)

    def process_tx(self, tx: Transaction):
        parent = self.chain[-1]

        # create the new state
        # NOTE: this is expensive state cloning (in terms of full account data cloning)
        state: State = State.deserialize(self.db.get(parent.state_root))
        state.process_tx(tx)

        # generate the merkle tree
        # NOTE: this is expensive re-creating the merkle tree
        tree = state.generate_merkle_tree()
        state_root = tree.root
        self.db.put(state_root, state.serialize())

        # create the block
        # NOTE: this needs the transaction root too
        block = Block(parent.block_hash, state_root)
        self.chain.append(block)


if __name__ == "__main__":
    chain = Blockchain()
    print(chain.get_account("dog"))

    tx = Transaction("dog", 10)
    chain.process_tx(tx)
    print(chain.get_account("dog"))

    tx = Transaction("dog", 20)
    chain.process_tx(tx)
    print(chain.get_account("dog"))
