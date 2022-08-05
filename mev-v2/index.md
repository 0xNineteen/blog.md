# PEV: Protocol Extractable Value (/Protocol-level MEV)

**tldr;** if protocols record requests and then execute the requests in batches with a specific ordering (instead of immediately processing each instruction) based on an auction system (where the winner of the auction can be the highest bidder or the bidder with the largest amount of the protocol's token) then they can enable protocol-extractable value (PEV). This value is taken away from validators/nodes and given directly to the protocols which can go directly back to the protocol's dao, treasury, or users. 

--- 

## Introduction

Right now the key players in MEV are the validators and the searchers. 
Validators are the nodes of the network which produce blocks consisting of multiple 
transactions. And searchers are the users who find money-making opportunities which 
usually rely on a specific ordering of txs in a block to realize a profit, and 
so the searchers pay the validators a certain amount to use their ordering. However, a lesser talked-about MEV player is the protocols themselves. 

<div align="center">
<img src="2022-07-30-19-06-56.png" width="450" height="300">
</div>

To gain a better understanding, it's helpful to understand how a protocol can emulate a validator based on implementation. For 
example, consider a protocol which collects N requests (eg, an example request could be "swap 50 ETH for BTC") and then executes all the 
requests on the N+1th request. Similar to a validator producing blocks of txs, the protocol is producing protocol-level blocks: txs that only interact with the protocol. 

Now consider if the protocol allows for users to bid on 
a certain ordering of the requests and the ordering which corresponds with the highest bid is executed. This is protocol-level MEV which is less miner extractable value (MEV) but more protocol extractable value (PEV).

Another way to think of it is since validators are paid to execute transactions in a specific ordering and transactions 
are just chunks of code, searchers are paying for a specific execution of code, and 
when all that code belongs to a single protocol, the searchers should be able to (with the correct implementation) pay the protocol for a specific ordering. This is because the protocol owns the lowest level of code execution, ie, the protocol **is** the code. 

## Winning PEV Orderings

Naturally, when we're talking about an auction (for code execution), we need to define
who wins the auction. While most blockchains require their payment in the chain's native token (SOL on solana, ETH on ethereum, etc) since the protocol is designing the auction code themselves, they can decide the auction winner based on the criteria which best fits the protocol's needs: 
- payment in the *protocol's* native token
- payment in a stablecoin
- the amount of the protocol's native token that is *staked*
- based on metrics that the ordering of requests achieves (eg, the ordering which achieves the smallest average amount of slippage)
- ... 

## Similarity to the Cosmos Chain

This is very similar to how the cosmos blockchain allows protocols to run their chain so that protocols can define their own validator logic. While in cosmos you lose
the ability to compose with other dapps built on the other chains (ie, going from ETH to cosmos you lose composability with all other ETH dapps). In this scenario, you get the 
best of both worlds: extractable value while remaining composable with other dapps. 

## What's Happening Now 

This means protocols are currently giving their MEV to the validators. If protocols 
begin to implement validator-like logic in their contracts this could unlock more value 
to the protocol users, the value could go back to the community/dao, or just lead
to an increase in revenue. 

## AMM Swaps with PEV POC 

For example, consider a simple AMM which swaps tokens with the x*y=k formula. This
would consist of the following:
```python 
def swap(amount: int, direction: A2B | B2A): 
    # compute swap output based on xy=k 
    # decrement user input token amount
    # increment user output token amount 
    # update amm parameters x and y
```

However, we can enable PEV with the three following functions 
```python
def PEV_swap(amount: int, direction: A2B | B2A): 
    # if no auction: start a new ordering structure
    # record swap parameters (user, amount, direction)
    # if auction time is over: end_auction()

def end_auction():
    # compute the winning ordering 
    # bid_winner's balance -= bid_amount
    # protocol's balance += bid_amount
    # fufill the swaps in the order of the ordering 
    # for swap_params in winners_ordering: swap(**swap_params)

def place_ordering_bid(bid_amount: int, ordering: Ordering):
    # record bid amount and corresponding ordering
```

## Related Work: CowSwap

Similar to PEV but instead using a general auction-based ordering, [cowswap](https://cow.fi/) defends against toxic MEV
by allowing searchers to submit orderings which achieve the best price improvement for the users who want to swap
(based on some criteria) and the ordering which achieves the best price improvement earns a slice of the total fees. 