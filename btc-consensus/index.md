# A New Perspective on BTC's POW 

Lets say you're on the IBM database team and, for the sake of your clients, you want your database to have an uptime of 99.99%. How could you do this? 

One 'simple' way to do this is to duplicate your database across multiple servers across the world. That way, if a tsunami strikes where one server is located or a server randomly crashes, you still got 99 other databases up and running which you can reroute to. 

But now the problem is how do you keep all of these databases in sync? If a client's request modifies one server's database, how are all the other databases updated? The last thing you want is for a client's request to return different values depending on what server the request is routed to. 

This is one of the problems that bitcoin aims to solve. More specifically, this problem is what proof-of-work (POW) solves. In bitcoin's case, the servers are 'nodes' and the requests are transactions (txs). 

# Consensus Amongst the Servers

## What not to do 

- everyone sending requests to all the servers and each server sending their updates to everyone else is chaos 
- network drops, system hardware crashes, random bit flips due to solar radiation, and malicious nodes can cause problems which leads to in consistencies across the network  

## Sending the Tx to the network 

When a client sends a tx to the nodes, how do we know which node should recieve the request? 

**(1) Send it to everyone:** One approach is to send the requests to every server. This is what BTC and ETH do: it's a gossip protocol where one node relays the txs it receives to every other node. 

**(2) Send it to a leader:** Another approach is to send the txs to a predefined 'leader'. This would involve creating a schedule of what server is the leader across time. For example, if we have servers A, B, C, one possible leader schedule is A (9am-10am) - B (10am-11am) - C (11am-12pm) - ... .  

We'll see later that (1) and (2) are actually the same approach in BTC's case.

*Note:* The leader approach requires a consistent clock across the servers, to know when each server is the leader. In practice, this is not always easy to achieve. 

*Note:* The size of the intervals of the leader schedule (1 hour in the example above) directly affects the speed and the decentralization of the network:
- If the leader interval is small (e.g, 10 seconds), the network will be very decentralized, but the overhead from switching leaders can decrease TPS. 
- If the leader interval is too large (e.g, 1 year) then the network will be very centralized however, TPS can increase bc of the reduced overhead. 

*Note To Above Note:* This is a very similar argument to deciding the size of each block. If the size of each block is too large then a single node maintains control over more txs, and so the network is more centralized, but the TPS increases. The opposite also holds choosing a smaller block size, more decentralized but with a decrease in TPS. 

## Broadcasting Updates

Say we go with approach **(2)**, once we have a specified leader receiving updates, we then need to relay the updated state to the other nodes. 

To do this, we have the leader broadcast its confirmed txs to all of the other nodes along with its signature. If all nodes know each other's public keys, then each node can confirm that the block they received is signed by the leader node. Then all nodes will add the block to their chain and everyone's states will be consistent. 

# Bitcoin's Computer 

Operating this model in a decentralized setting is where some difficulties arise. Each miner is now a unique server, with no association with the others. How do the miners communicate and work together for consensus? This is where POW comes in. 

At first glance, BTC uses approach **(1)** where the users send their txs to the entire network. To confirm blocks each node tries to find a hash, once the hash is found, its propagated along with the txs to the rest of the network. So how does this relate to approach **(2)**?

Understanding this another way, consider that BTC actually uses a leader schedule approach (2) and that the leader is determined by whoever finds the hash first. When the node finds the hash they are elected the leader and they propagate their block to the network. All of the other nodes can confirm that the block received was from the leader by confirming the hash is indeed correct (less than a specific threshold). 

Thinking of it like this, BTC's POW is a special case of the leader schedule where the leader is determined randomly and submits a single block of txs. Since each BTC block takes ~10 minutes to mine, that means the leader schedule is split into ~10-minute increments.

The mind-boggling thing is that this means that BTC's POW is a leader-schedule clock which doesn't require any coordination/agreement on time between any of the other nodes. 

## Proof of Stake (POS)

coming soon ... 

# Solana's Proof of History (POH)

coming soon ... 

## References 

[Blockchain Fundamentals -- Blockchain at Berkeley](https://www.youtube.com/playlist?list=PLZvgWu86XaWkpnQa6-OA7DG6ilM_RnxhW): Great online course. Probably the best place to start. 

[Foundations of Blockchains Lecture Notes](https://www.youtube.com/watch?v=KNJGPI0fuFA&list=PLEGCF-WLh2RLOHv_xUGLqRts_9JxrckiA): These introduce the distributed computer/state machine replication (SRM) problem and some solutions. Check out the lecture notes in the youtube description.

[Solana Proof of Stake + Proof of History Primer](https://www.shinobi-systems.com/primer.html): Good article on POH.

[Blockchain Proof-of-Work Is a Decentralized Clock](https://grisha.org/blog/2018/01/23/explaining-proof-of-work/): OG blog post on POW as a clock. 