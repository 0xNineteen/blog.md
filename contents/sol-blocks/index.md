# Building Blocks in Solana

This post will explain how blocks are built in solana using the diagram below as a reference

![](2023-06-13-11-04-48.png)

Theres two main stages for blocks in solana: 
  - The Transaction Processing Unit (TPU): this stage is for when you **are a leader**
  and need to build your own block
  - The Transaction Validation Unit (TVU): this stage is for when you **are not 
  a leader**, and you recieve a block from a leader, and need to replay the block 
  to reproduce the state

## TPU Flow

We'll start with the TPU (the top right in the diagram)

### receiving txs 


In solana, there is no mempool, txs are forwarded directly to the leader.
So, starting a validator, dedicated ports are opened to receive these txs
including:
  - `tpu`, `vote`, and `tpu_forwards` sockets
  - the tpu socket is for normal txs (eg, { send token A to bob })
  - the vote socket is only for votes 
    - votes are a special transaction which only validators send - 
    when a validator sends a vote tx they are saying that a specific block 
    is valid (the tx data includes the hash of the block which they are voting for)
  - the tpu_forwards socket is less important for this post, so well leave it alone

txs and votes are recieved, sigantures are verified, and are then sent to the 
`BankingStage`

*note:* txs are sent to the banking stage in batches, **as they're recieved**, so sometimes
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

*note:* the `bank`/`Bank` struct is used to represent a slot, including all the accounts 
state at that slot 

### proof-of-history and the `Entry` struct 

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
the entries yourself, you can make use of the same codeflow as the TVU - 
this will make more sense when we talk about the TPUs flow 

#### when are we no longer the leader 

- the code stops producing blocks of txs after reaching the max PoH height which is decide by two things 
  - either the max number of 'ticks' (hash loops) were produced
  - or the bank was created more than ns_per_slot time ago 
    - note: ns_per_slot is computed based on the max ticks per slot and 
    the hash time 

*note:* the PoH infinite loop will still continue, its just no new txs 
will be included

for example, say the block at slot 19 is ok, and the leader of slot 20 never 
produces a block (bc its offline of smthn), if you start building a new block 
for slot 21, you'll need to also share your PoH loop which covers the time 
in slot 20 to prove you waited the full slot time before starting to produce 
the block for slot 21

## TVU 

- next, the TVU flow (starting at the top left)
- for more info on the TVU checkout [this post](https://github.com/0xNineteen/blog.md/blob/master/contents/sol-tvu/index.md)
  - if you dont want to read it, the tldr is shreds from the leaders TPU are
  received on dedicated TVU sockets, verified they were signed by the leader, 
  and stored in the blockstore
- we'll start at the `ReplayStage` which replays entries' txs to 
reproduce the state which the leader propogated to the network 

### finding a bank to replay

- the most important fcn is `replay_active_banks` which reads from the `bank_forks` variable
  - the `bank_forks` variable is a major var in the codebase - it organizes all the node's banks
  - *note:* a bank is either frozen: read-only and cannot be modified, or active:
  its state can be modified
- the first thing the fcn does is find all 'active' banks in the bank_forks var

### reading from the blockstore

- the next thing is for each of these active banks, query the blockstore 
for the associated entries with that bank's slot using `blockstore::get_slot_entries_with_shred_info`
  - *note:* since entries aren't all propogated at once, the blockstore 
    wont always have all the entries, so calling the above 
    fcn is guaranteed to return all the entries - the solution is to track the 
    progress of what entry indexs have been processed and keep the bank as 
    active until all the entries have been processed (which is exactly what the
    `ConfirmationProgress` struct does)
    - once all the entries have been processed, the bank will be frozen and will 
    no longer be considered in the replay loop 
- from these entries, we then verify all is good: ie, certain 
properties hold (`::verify_ticks`), the entries are a valid PoH chain 
(`hash([last_hash, tx_root]) == entry.hash`), and that all the transactions include 
valid signatures

### replaying a bank

- we now have a batch of verified PoH entries for a specific slot which we 
want to process

*note:* since TPU blocks (whos state have already been processed) are also 
following this code flow, before fully replaying the block, we only fully replay 
a bank if `bank.collector_id() != my_pubkey`

- to process the entries the code uses `::process_entries`
  - which loops through the entries and either registers ticks (entries with no txs)
    or processes transactions (txs)
- ticks: each tick is registered, and on the last tick, that entries hash is 
- txs: processing txs uses the same fcns as the TPU 
(`load_and_execute_transactions` and `commit_transactions`)
recorded as the 'blockhash'

### freezing banks

- after the replay is complete, if the bank is complete
(enough ticks have been registered), its frozen (using `bank.freeze()`)
  - freezing a bank, hashes its internal state, and makes it read-only 
  - the interal hash consists of the parent's bank hash, a hash of the accounts modified, 
  the signature count, and the blockhash of the entries 
  - if all is valid, validators produce votes as signatures on bankhashes

*note:* TPU banks are also frozen here