# PEV: Protocol Extractable Value (/Protocol-level MEV)

**tldr;** if protocols begin to track requests to their protocol and allow for an arbitrary ordering of execution of these requests based on an auction system (where the winner of the auction can be the highest bidder  or the bidder with the largest amount of the protocol's token staked) then they can enable protocol extractable value (PEV). This value is taken away from the validator and given to the protocols which can be given to the protocol's dao/treasury and reward the protocol users more instead of the value going to validators/node operators. 

--- 

## Introduction

Right now the key players in MEV are the validators and the searchers. 
Validators are the nodes of the network which produce blocks consisting of multiple 
transactions (txs). And searchers are the users who find money-making opportunities which 
usually rely on a specific ordering of txs in a block to realize a profit, and 
so the searchers pay the validators a certain amount to use their ordering (which leads
to PGAs). However, a lesser talked-about MEV player is the protocols themselves. 

<div align="center">
<img src="2022-07-30-19-06-56.png" width="450" height="300">
</div>

To gain a better understanding, it's helpful to consider protocols as a subset of validators. For 
example, consider a protocol which collects N requests (an example request could be "swap 50 ETH for BTC") and then executes all the 
requests on the N+1th request. Similar to a validator, this protocol is essentially producing
protocol-level blocks. Now consider if the protocol allows for users to bid on 
a certain ordering of the requests and the highest bid gets the correct ordering. Then 
you have protocol-level MEV which is less miner extractable value (MEV) but more protocol extractable value (PEV).

Since validators are paid to execute transactions in a specific ordering and transactions 
are just chunks of code, searchers are paying for a specific execution of code, and 
when all that code belongs to a single protocol, the searchers should be able to pay the protocol for a specific ordering of 
code execution since the protocol owns the lowest level of code execution / the protocol **is** the code. 

## Winning PEV Orderings

Naturally, when we're talking about an auction (for code execution), we need to define
who wins the auction. While normal blockchains require their payment in the chain's native token, since the protocol is designing the auction code themselves, they can decide the auction winner based on the criteria which best fits the protocol's needs: 
- payment in the protocol's native token
- payment in a stablecoin
- the amount of the *protocol's native token* that is *staked*
- based on metrics that the ordering of requests achieves (eg, the ordering which achieves the smallest amount of slippage across all swaps wins the auction)
- ... 

## Similarity to the Cosmos Chain

This is very similar to how the cosmos blockchain allows protocols to run their chain so that protocols can define their validator logic, however with cosmos you lose
the ability to compose with other dapps built on the other chains (ie, going from ETH to cosmos you lose composability with all ETH dapps). In this scenario, you get the 
best of both worlds extractable value while remaining composable with other dapps. 

## What's Happening Now 

This means protocols are currently giving their MEV value to the validators. If protocols 
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
def place_ordering_bid(bid_amount: int, ordering: Ordering):
    # record bid amount and corresponding ordering

def end_auction():
    # compute the winning ordering 
    # bid_winner's balance -= bid_amount
    # protocol's balance += bid_amount
    # fufill the swaps in the order of the ordering 
    # for swap_params in winners_ordering: swap(**swap_params)

def PEV_swap(amount: int, direction: A2B | B2A): 
    # if no auction: start a new ordering structure
    # record swap parameters (user, amount, direction)
    # if auction time is over: end_auction()
```

## Related Work: CowSwap

Similar to PEV but instead using a general auction-based ordering, [cowswap](https://cow.fi/) defends against toxic MEV
by allowing searcher's to submit orderings which achieve the best price improvement for the users who want to swap
(based on some criteria) and the ordering which achieves the best price improvement earns a slice of the total fees. 