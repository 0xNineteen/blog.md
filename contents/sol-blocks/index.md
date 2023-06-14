- post will be explaining how blocks are built in solana with the following diagram

![](2023-06-13-11-04-48.png)

- theres two main stages
  - TPU: when you are a leader and building blocks 
  - TVU: when you recieve a block from a leader and need to replay the results 

## TPU
- we start with the TPU

### receiving txs 

- starting a validator, ports are opened to receive txs 
  - this includes, tpu, tpu_forwards, and vote sockets
  - the tpu socket is for normal txs (eg, { send token A to bob })
  - the vote socket is only for votes 
    - votes are a special transaction which only validators send - 
    when a validator sends a vote tx they are saying that a specific block 
    is valid (the tx data includes the hash of the block which they are voting for)
  - the tpu_forwards socket is less important for this post, so well leave it
- txs are recieved, sigantures on votes are verified, and are then sent to the 
`BankingStage`

*note:* txs are sent in batches as they're recieved, so sometimes
the banking stage will be operating on a large number of txs, 
and othertimes a small number of txs

*note:* for more info on how txs flow checkout
[this post](https://github.com/0xNineteen/blog.md/blob/master/contents/sol-rpcs/index.md)

### banking stage 

- this stage is responsible for building new blocks from the txs recieved from the 
previous stage
- we wont go indepth on the code for this (bc it should be a post on its own)
- but there are three main stages:
  - `bank.load_and_execute_transactions`: executes to get new state
  - `transaction_recorder.record_transactions`: sends to proof-of-history generator 
  - `bank.commit_transactions`: updates other info related to a block
 (store the updated accounts, caches current stakers, collects validatore fees for block, etc.)
- the second one is where things get interesting 

### proof-of-history 

- the reciever from `transaction_recorder.record_transactions` recieves a batch of txs to include in PoH
- PoH is a infinite hash loop, and since hash functions are a one-way function, 
this loop record a proof that some time has passed 
  - the loop produces entries which are either a loop of hashes which include tx hashes in the hash 
  or just a plain loop of hashes (with no txs)
  - this is the key struct: `Entry`

```rust 
pub struct Entry {
    /// The number of hashes since the previous Entry ID.
    pub num_hashes: u64,

    /// The SHA-256 hash `num_hashes` after the previous Entry ID.
    pub hash: Hash,

    /// An unordered list of transactions that were observed before the Entry ID was
    /// generated. They may have been observed before a previous Entry ID but were
    /// pushed back into this list to ensure deterministic interpretation of the ledger.
    pub transactions: Vec<VersionedTransaction>,
}
```
- This creates a sequential hash list of `Entry` structs which have a pointer 
to the previous entries hash and a list of txs 
    - the first entry begins the hash off the last block's `blockhash` 
    - the second begins off the first entry's hash 
    - ... 
    - the last entries final hash is that block's `blockhash`
- relative to other blockchains, in solana, a collection of these entries is a block

```python 
parent_hash = state.get_parent(slot)
last_hash = parent_hash
entries = []
while true: 
    txs = state.receive_new_txs()?
    tx_root = compute_merkle_root(txs)
    entry_hash = hash([last_hash, tx_root])
    entries.push(Entry { entry_hash, txs })

    last_hash = entry_hash 
block = entries # different terminology

# explained soon
shreds = shred_entries(block)
broadcast(shreds)
blockstore.store(shreds)
```

- how are txs included in the entries? 
- each batch of txs are hashed using a merkle tree of the tx signatures
  - the tx signature is a signed hash of the message 
  - each leaf would be a signature 
  - the merkle root would uniquely represent the batch of txs 
  - the merkle root is then sent to be 'mixed in' with the PoH

![](2023-06-13-11-30-35.png)

- as these entries are produced, they are given to the `BroadcastStage` 
where they are
  - turned into shreds 
    - since blocks are too big to send over UDP directly, solana chunks a block into 
  smaller data chunks (called shreds) which are broadcasted
  - these shreds are sent to the local nodes blockstore 
    - the blockstore stores a bunch of useful metadata on the chain including
    the shreds
  - these shreds are also transmitted to other node's TVUs in the network

*notice:* though we havent talked about it yet, in the TVU, shreds are recieved by 
the network and stored in the blockstore - which are then later read - 
notice how by storing the shreds in the blockstore even when you produced 
the entries yourself, you can make use of the same codeflow as the TVU

## TVU 

- next, the TVU flow (top left)
- see the [TVU post](https://github.com/0xNineteen/blog.md/blob/master/contents/sol-tvu/index.md)
for more info
- it begins with the `ReplayStage` which continuously reads from the blockstore
  - *note:* when shreds are recieved, 
- 