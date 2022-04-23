# A New Perspective on BTC's POW 

**TLDR;** To achieve consensus among multiple distributed machines you need to ensure a single node (the leader) can propogate state updates to the rest of the network and other nodes can all agree on that the data received was from the correct leader. BTC's POW uses its hash puzzel to elect a new leader for each block and all other nodes can confirm they recieved the txs from the leader bc they can confirm the hash is correct. 

--- 

Lets say you're on the IBM database team and, for the sake of your clients, **you want your database to have an uptime of 99.99%**. How could you do this? 

One 'simple' way to do this is to **duplicate your database across multiple servers across the world**. That way, if a tsunami strikes where one server is located or a server randomly crashes, you still got 99 other databases up and running which you can reroute to. 

But now the problem is **how do you keep all of these databases in sync? (i.e have a consistent network state)** If a client's request modifies one server's database, how are all the other databases updated? The last thing you want is for a client's request to return different values depending on what server the request is routed to. 

**This is actually one of the problems that bitcoin's proof-of-work (POW) aims to solve.** In bitcoin's case, the servers are nodes and the requests are transactions (txs) (e.g, transfer 10 BTC from ALICE to BOB). 

# Consensus Amongst the Servers

## What not to do 

It's easier to introduce the topic of consensus by considering what not to do. 

Consider if every node accepts all valid txs, updates their state, and sends the txs to all other nodes as soon as possible. Furthermore, they would recieve new txs from other nodes and update their state.  

Why wouldn't this work? Network problems can lead to dropped data mid transmittion, node hardware can crash mid transmition, and random bits can be flipped due to solar radiation. All these problems can lead to inconsistencies in the network state across nodes.

Our plan to understand the soln. will be to break consensus into two parts: 
1. sending a tx to the network
2. updating the network state 

## Sending a Tx to the network 

When a client sends a tx to the network, **how do we know which node should recieve the request?** There are two approaches: 

**(1) Send it to all the nodes:** **This is what BTC and ETH do: it's a gossip protocol** where one node broadcasts the txs it receives to every other node. 

**(2) Send it to a leader:** Another approach is to send the txs to a predefined 'leader'. **This would involve creating a schedule of what node is the leader across time.** For example, if we have nodes A, B, C, one possible leader schedule is **A (9am-10am) - B (10am-11am) - C (11am-12pm) - ...** . Then when a new tx comes it, it gets sent to the current leader, which then broadcasts it to every other node.   

We'll see later that **(1) and (2) are actually the same approach in BTC's case.**

*Note:* **The leader approach requires a consistent clock across the nodes**, to know when each node is the leader. In practice, this is not always easy to achieve. 

*Note:* The size of the intervals of the leader schedule (1 hour in the example above) directly affects the speed and the decentralization of the network:
- If the leader interval is small (e.g, 10 seconds), the network will be very decentralized, but the overhead from switching leaders can decrease TPS. 
- If the leader interval is too large (e.g, 1 year) then the network will be very centralized however, TPS can increase bc of the reduced overhead. 

*Note To Above Note:* This is a very similar argument to deciding the size of each block. If the size of each block is too large then a single node maintains control over more txs, and so the network is more centralized, but the TPS increases. The opposite also holds choosing a smaller block size, more decentralized but with a decrease in TPS. 

## Updating the network state 

Say we go with approach **(2) Send it to a leader**. Once we have a specified leader receiving updates, we then need to relay the updated state to the other nodes. But how do the nodes know the txs come from the leader? 

This is when we actually need all the nodes to know each other's public keys. Furthermore, **we need the leader to broadcast it's signature along with its confirmed txs. That way each node can confirm that the block they received comes from the leader node and can saftely update their state.**

# Bitcoin's Computer 

Operating this model in a decentralized setting is where some difficulties arise. **Ideally, we want anyone to setup a node without needing to share their publickey with the network, and without setting up a clock for the leader schedule.** This is where POW comes in. 

When a tx is send to the BTC network, at first glance, **BTC uses approach (1) Send it to all the nodes** where the txs are broadcasted to all the other nodes. 

The magic then comes when BTC's POW has each node try to find a hash corresponding with the block of txs, and once the hash is found, its propagated along with the txs to the rest of the network. This seems pretty arbitrary, but it actually can be connected to everything we talked about above.

**So how does this relate to approach (2)**?

**Understanding POW another way**, consider that **BTC actually uses** **(2) Send it to a leader, BUT the leader is determined by whoever finds the block hash**. When the node finds the hash they are elected the leader and they propagate their block to the network. **All of the other nodes can confirm that the block received was from the leader by confirming the hash is indeed correct (less than a specific threshold).** 

Thinking of it like this, BTC's POW is a special case of the leader schedule where the leader is determined randomly and submits a single block of txs. Since each BTC block takes ~10 minutes to mine, that means the leader schedule is split into ~10-minute increments.

The mind-boggling thing is that this means that **BTC's POW is a leader-schedule clock which doesn't require any coordination/agreement on time between any of the other nodes.**

## Proof of Stake (POS)

coming soon ... 

# Solana's Proof of History (POH)

coming soon ... 

## References 

[Blockchain Fundamentals -- Blockchain at Berkeley](https://www.youtube.com/playlist?list=PLZvgWu86XaWkpnQa6-OA7DG6ilM_RnxhW): Great online course. Probably the best place to start. 

[Foundations of Blockchains Lecture Notes](https://www.youtube.com/watch?v=KNJGPI0fuFA&list=PLEGCF-WLh2RLOHv_xUGLqRts_9JxrckiA): These introduce the distributed computer/state machine replication (SRM) problem and some solutions. Check out the lecture notes in the youtube description.

[Solana Proof of Stake + Proof of History Primer](https://www.shinobi-systems.com/primer.html): Good article on POH.

[Blockchain Proof-of-Work Is a Decentralized Clock](https://grisha.org/blog/2018/01/23/explaining-proof-of-work/): OG blog post on POW as a clock. 