- post will be explaining the following diagram 
- on how blocks are built in solana 

![](2023-06-13-11-04-48.png)

- theres two main stages 
  - TPU: when you are a leader and building blocks 
  - TVU: when you recieve a block from a leader and need to replay the results 

## TPU
- we start with the TPU

### receiving txs 

- starting a validator, ports are opened to receive txs 
  - this includes, tpu, tpu_forwards, and vote sockets
  - the tpu socket is for normal txs (eg, send token A to bob)
  - the vote socket is only for votes (well explain votes later on)
  - the tpu_forwards socket is less important
- for more info checkout the 
[post on how txs flow](https://github.com/0xNineteen/blog.md/blob/master/contents/sol-rpcs/index.md)
- txs are recieved, sigantures on votes are verified, and are then sent to the 
`BankingStage`

*note:* txs are sent in batches as they're recieved, so sometimes
the banking stage will be operating on a large number of txs, 
and othertimes a small number of txs

### banking stage 

- this stage is responsible for building new blocks from txs recieved 
- wont go indepth on this (bc it should be a post on its own)
- the three main stages include 
  - `bank.load_and_execute_transactions`: executes to get new state
  - `transaction_recorder.record_transactions`: sends to proof-of-history generator 
  - `bank.commit_transactions`: updates other info related to a block
 (caches current stakers, collects validatore fees for block, etc.)
- the second one is where things get interesting 

### proof-of-history 

- each batch of txs are hashed using a merkle tree of the tx signatures
  - the tx signature is a signed hash of the message 
  - each leaf would be a signature 
  - the merkle root would uniquely represent the batch of txs 
- this is then sent to the `PoHService` which runs an infinite loop either mixing in
batches of txs (`PoH.record(mixin)` where `mixin` is the merkle root of txs) 
or empty hashes (`PoH.hash()`) until more txs are recieved
- This creates a sequential hash list of `Entry` structs which have a pointer 
to the previous entries hash and a list of txs 
    - the first entry begins the hash off the last block's `blockhash` 
    - the second begins off the first entry's hash 
    - ... 
    - the last entries final hash is that block's `blockhash`

![](2023-06-13-11-30-35.png)

- these entries are then given to the `BroadcastStage`
- each entry is: 
  - turned into shreds 
  - sent to the local nodes blockstore 
  - and transmitted to other nodes in the network  

## TVU 

- next, the TVU flow (top left)
- see the [TVU post](https://github.com/0xNineteen/blog.md/blob/master/contents/sol-tvu/index.md)
for more info
- it begins with the `ReplayStage` which continuously reads from the blockstore
  - *note:* when shreds are recieved, 
- 