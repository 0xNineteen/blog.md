- v1
  - state is a account dict which is fully cloned for each block 
  - merkle tree is constructed afterwards 

- v2 
  - state is a dict from state_root to children hashes (hashes lookup in db to find account data)
    - reduces full account data clone but we clone O(N) hashes
  - merkle tree is constructed afterwards 

- v3 
  - state is a tree of children hashes 
    - reduces hash cloning to O(log_b(N)) where b is the branching factor 
      - since we are using hex hashes b = 16

- v4 
  - state is a radix tree of children hashes 
    - reduces redundent searches 

... 