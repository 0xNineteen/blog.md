# PEV: Protocol Extractable Value


**tldr;** validators can extract value from chains because they decide transaction orderings however, if protocols start to record requests and execute the requests in batches, then protocols can enable begin to extract MEV/PEV (Protocol Extractable Value) which can be given to the protocol's dao, treasury, or users. 

## Acknowledgements 

s/o to [bigz_Pubkey](https://twitter.com/bigz_Pubkey) for bringing up the key ideas of PEV and the great discussions on the topic.

## Introduction

Right now the key players in MEV are the validators and the searchers. 
Validators are the nodes of the network which produce blocks of multiple 
transactions (txs) and searchers are the users who find money-making opportunities which rely on a specific ordering of txs to realize a profit. To ensure the searcher realizes a profit they usually bribe the validators to use their ordering. Though these two entities are well known, a lesser known MEV player is the protocols themselves. 

<div align="center">
<img src="2022-07-30-19-06-56.png" width="450" height="300">
</div>

To gain a better understanding, it's helpful to understand how a protocol can emulate a validator based on implementation. For 
example, consider a protocol which collects N requests (eg, an example request for an AMM could be "swap 50 ETH for BTC") and then executes all the 
requests on the N+1th request. Similar to a validator producing blocks of txs, the protocol is producing protocol-level blocks: txs that only interact with the protocol. 

Now consider if the protocol allows for users to bid on 
a certain ordering of the requests and the ordering which corresponds with the highest bid is executed. This is "protocol extractable value" (PEV). An even more interesting ideal is to consider if the protocol itself can place a bid and decide the ordering that works best for it. 

Another way to think of it is since validators are paid to execute transactions in a specific ordering and transactions 
are just chunks of code, searchers are paying for a specific execution of code, and 
when all that code belongs to a single protocol, the searchers should be able to (with the correct implementation) pay the protocol for a specific ordering. This is because the protocol owns the lowest level of code execution, ie, the protocol **is** the code. 

## Winning PEV Orderings

Naturally, when we're talking about an auction (for code execution), we need to define
who wins the auction. While most blockchains require their payment in the chain's native token (SOL on solana, ETH on ethereum, etc) since the protocol is designing the auction code themselves, they can decide the auction winner based on a much more flexible criterion which best fits the protocol's needs: 
- payment in the *protocol's* native token
- payment in a stablecoin
- the amount of the protocol's native token that is *staked*
- based on metrics that the ordering of requests achieves (eg, the ordering which achieves the smallest average amount of slippage - cowswap)
- ... 

## Similarity to the Cosmos Chain

This is very similar to how the cosmos blockchain allows protocols to run their chain so that protocols can define their own validator logic. While in cosmos you lose
the ability to compose with other dapps built on the other chains (ie, going from ETH to cosmos you lose composability with all other ETH dapps). In this scenario, you get more of both worlds: extractable value while remaining composable with other dapps. 

## PEV Tax

Another interesting idea is for the protocol to tax specific PEV txs. For example, consider an AMM protocol that contains multiple pools of tokens and arbitrage opportunities exist sometimes. Since searchers will usually submit their arbitrage txs atomically (ie, a single tx including multiple instructions that swap between pools) the protocol should be able to detect such txs and if the arbitrage is successful (ie, the searcher ends with more balance than they started with) then the protocol can tax a certain percentage of the profit (eg, 5% of the profit goes to the treasury). 

Ideally, the tax will be as large as possible for the protocol to earn the most profit, while not so large that the searchers stop executing the arbitrage txs. For example, if the searchers will only execute their arbitrage strategy if they earn at least <span>$</span>1K per month due to energy/server fees, then the protocol should adjust their tax rate so that the searchers earn approx <span>$</span>100 per month. For example, if there is <span>$</span>100K of PEV per month on the protocol and the protocol notices 10 searchers are arbitraging, then they could set the tax rate to (100,000 - 10 * 100) / 100,000 = 99% (lol) and earn 99K in additional profit for their dao/users.  

## User Experience: More Value More Wait 

While recording and ordering txs in the code allows for protocols to extract additional value, one problem is that users need to wait longer for their transactions to confirm because not only does their tx need to be put in a chain-level block (which requires N txs), but also a protocol-level block (which requires N protocol txs). This is a trade-off that the protocol will need to decide if its worth it or not.

## What's Happening Now 

This means protocols are currently giving available MEV to the validators. If protocols 
begin to implement validator-like logic in their contracts this could enable protocols to capture more value which can go 
back to protocol's dao, treasury, or users. 

## POC: PEV AMM Swaps 

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