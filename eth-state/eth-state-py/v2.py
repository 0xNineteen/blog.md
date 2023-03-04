#%%
from utils import *

# chain:
# get parent state [x]
# modify state [x]
# compute new account_hash
# hash(account, block_uniq) - whats block_uniq? [tx_root, parent_hash]
# cant be state_root bc its derived from the account hashes
# cant be block_root bc its derived from the state_root
# can it be the tx_root? ... [todo: add tx_root to block]
#   in POW you can have two blocks which have the same tx_root, parent_hash, but different nonce
#   and then you have a fake fork (same chain differnt hash) -- thats probs pretty unlikley so i think its ok
# store new serialized account
# generate state_root [x]
# get parent_root
# remove the old account_hash
# insert the new account_hash ()
# compute the new root hash
# store new_root_hash => [new-account-hashes]

# eg,
# first tx occurs
# db is empty
# create account
# key = hash([address, tx_root, parent_root])
#   # this ALONE wont work bc this requires to know the tx_root+parent_root of the most recently updated block
#   # combine it with (HASH, ADDRESS) and we have lookup working
# ...
# address = hash(serialized(account)) <- can just do this if we have lookup handled by the list
# account_keys = [(key, address)]
# db.put(state_root, account_keys) # state_root => [(account_hash, address)]
# db.put(key, account) # hash => account
# second tx occurs (which updates address)
# get the list of previous accounts
# addresses = state_db.get(parent_block.state_root)
# key, _ = find(address, addresses)
# account = account_db.get(key)
# new_account = update(account, tx)
# new_addresses = clone(addresses).update(new_account, address) # this is a cheapER clone than full account data
# new_key = hash([address, tx_root, parent_root])
# account_db.put(new_key, new_account.serialize())
# state_root = hash(new_addresses)
# state_db.put(state_root, new_addresses)
# block(state_root, parent_root, tx_root)

# state
# store 1) db with account_hash => account
#       2) db with state_root => [account_hashs] (to generate the root)
# hash the account of interest
# lookup account with account_hash
# lookup state with state_root

# note: compared to v1 account cloning is reduced to only the modified account
# however, we always need to clone O(N) account hashes for each modification (... v3?)


@dataclass
class Block:
    parent_hash: bytes
    state_root: bytes
    tx_root: bytes  # !new
    block_hash: bytes = None

    def __post_init__(self):
        self.block_hash = hash([self.parent_hash, self.tx_root, self.state_root])


class State:
    db = DB("state.db")

    def __init__(self, account_hashes=[]) -> None:
        self.account_hashes = account_hashes

    def put_account(self, account: Account):
        self.db.put(account.hash_bytes(), account.serialize())

    def set_account_hashes(self, account_hashes):
        self.account_hashes = account_hashes

    def generate_merkle_root(self):
        # list of (hash, address) we group hash the hashes
        return hash([bytes(h, "utf-8") for h, _ in self.account_hashes])

    def serialize(self):
        return bytes(json.dumps(self.account_hashes), "utf-8")

    @staticmethod
    def deserialize(data):
        data = json.loads(data.decode("utf-8"))
        state = State()
        state.account_hashes = data
        return state


class Blockchain:
    def __init__(self) -> None:
        # init state/genesis block
        state = State()
        state_root = state.generate_merkle_root()

        self.db = DB("blocks.db", resume=False)
        self.db.put(state_root, state.serialize())

        # NOTE: this doesnt support forks
        genesis = Block(bytes(0), state_root, bytes(0))
        self.chain: list[Block] = [genesis]

    def get_account(self, address) -> Account:
        head = self.chain[-1]
        return self.get_account_block(address, head)

    def get_account_block(self, address, block) -> Account:
        # lookup parent block's state
        state = State.deserialize(self.db.get(block.state_root))
        state_account_hashes = state.account_hashes

        # find account
        address_hash = [h for (h, addr) in state_account_hashes if addr == address]
        if len(address_hash) == 0:
            return None
        assert len(address_hash) == 1
        address_hash = address_hash[0]

        account = state.db.get(bytes(address_hash, "utf-8"))
        account = Account.deserialize(account)

        return account

    def process_tx(self, tx: Transaction):
        parent_block = self.chain[-1]

        tx_root = tx.hash()

        # lookup parent block's state
        state = State.deserialize(self.db.get(parent_block.state_root))
        state_account_hashes = state.account_hashes

        # find the tx's address account
        address = tx.address
        address_hash_index = [
            i for i, (_, addr) in enumerate(state_account_hashes) if addr == address
        ]

        if len(address_hash_index) == 0:
            # account DNE -- init account
            account = Account(tx.address, tx.amount)

        else:
            assert len(address_hash_index) == 1
            # lookup existing account
            i = address_hash_index[0]
            address_hash, _ = state_account_hashes[i]
            account_data = state.db.get(bytes(address_hash, "utf-8"))
            account = Account.deserialize(account_data)

            # modify account with tx
            account = account.apply(tx)

            # update state_account_hashes
            del state_account_hashes[i]

        state.put_account(account)

        # update new state root
        state_account_hashes.append((account.hash(), tx.address))
        new_state = State(state_account_hashes)
        state_root = new_state.generate_merkle_root()
        self.db.put(state_root, new_state.serialize())

        # create new block
        block = Block(parent_block.block_hash, state_root, tx_root)
        self.chain.append(block)


if __name__ == "__main__":
    chain = Blockchain()

    tx = Transaction("dog", 10)
    chain.process_tx(tx)
    dog_block = chain.chain[-1]

    tx = Transaction("cat", 9)
    chain.process_tx(tx)

    tx = Transaction("dog", 20)
    chain.process_tx(tx)

    # head block state
    print("dog", chain.get_account("dog"))
    print("cat", chain.get_account("cat"))

    # rollbacks for forks
    print("dog @ init", chain.get_account_block("dog", dog_block))

    s = State()
    n_accounts = -1
    for k in s.db.db.RangeIter(include_value=False):
        n_accounts += 1
        print("key:", k)
    print("N accounts (dog1, cat1, dog2):", n_accounts)

    import time

    print("done", time.time())
