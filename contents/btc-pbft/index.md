## BTC vs PBFT: Ordering Blocks 

- pbft orders blocks by agreeing on a sequence number 
  - ie, pre-process and process (with signatures) are 
    1. choosing a sequence number for the transaction 
    2. leader broadcasts to the cluster **requesting** about a sequence number (preprocess) 
    3. each node broadcasts to every other node that they agree on the sequence number (process)

- btc works by hashing the block which includes a reference to the parent block's hash and then brodcasting it 
  - since the hash includes the parents hash this inherently has ordering and is the same as a sequence number 
    - ie, you dont need to request in step 2 of PBFT
  - and since the block is fully hashed they know it hasnt been tampered with, comes from the leader (ie, is a valid POW block), and everyone else recieved the same one 
    - ie, you dont need signatures or step 3 in PBFT
  - much more communication efficient! 
