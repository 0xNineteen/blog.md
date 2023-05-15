## PBFT ordering 

## pbft

- there are three main stages of PBFT 
  - pre-prepare: leader sends out a block of txs 
  - prepare: group of validators send out votes for the block 
    - I have seen the block and its valid
  - commit: group of validators send out votes on the votes 
    - I have seen that everyone else has seen the block and knows its valid
- on leader changes PBFT uses the commit signatures to convince any other nodes of a new state 
- the pre-prepare is obv required so people know of the state change 
- the prepare is required to know if enough people have seen it and agree on it 
- to know why the commit stage is required consider after the prepare stage one node recieves everyones votes but noone else recieves any - then the leader change occurs - the node with the votes will have a different state than the ones which never recieved the votes 
  - the commit stage is used to prove that a majority have recieved the prepare votes (ie, they know the majority has voted)

## btc: chains and implicit ordering

- pbft orders blocks by agreeing on a sequence number 
  - ie, pre-process and process (with signatures) include a few steps (not to be confused with above steps)
    1. choosing a sequence number for the transaction 
    2. leader broadcasts to the cluster **requesting** about a sequence number (preprocess) 
    3. each node broadcasts to every other node that they agree on the sequence number (process)

- btc works by hashing the block which includes a reference to the parent block's hash and then brodcasting it 
  - since the hash includes the parents hash this inherently has ordering and is the same as a sequence number 
    - ie, you dont need to request in step 2 of PBFT
  - and since the block is fully hashed they know it hasnt been tampered with, it comes from the leader (ie, is a valid POW block)
    - ie, you dont need signatures or step 3 in PBFT
  - much more communication efficient! 

## solana

- understanding how solanas consensus works can be easier when compared to PBFT
- solana does using an optimistic voting method 
  - a block at slot N is broadcast (with a reference to its parent for ordering) (this is the pre-prepare)
  - other nodes see the block, and generate vote txs on the block 
  - these vote txs are included in some block in the future at slot M (M > N) (this is the prepare)
    - 2/3 of nodes have seen the block and voted on it
  - this process is continued for future blocks 
  - when there are 2/3+ vote txs for the block in slot M then the block at slot N is confirmed 
    - 2/3 of nodes have seen the 2/3 votes for block N
