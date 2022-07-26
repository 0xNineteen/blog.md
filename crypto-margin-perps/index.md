# The Evolution of Margin in Crypto: The Birth of Perps

TLDR; perps give you access to margin trading without taking on borrow/loan fees for the additional assets. There are two main perps settings: (1) a PvP setting where you settle your PnL over time (eg, every hour) directly with another trader and (2) a PvE setting / a marketplace of perps where you pay a funding rate so that the market's price matches the ground-truth price. With enough 'price informed volume' you shouldn't need funding rates -- in this case, funding rates act as a dynamic bribe for more volume. 

## Centralized Margin Accounts 

Before we talk about decentralized margin, it can be helpful to understand how centralized margin accounts work: 

Let's say you deposit 100<span>$</span> into your bank (100<span>$</span> of collateral), and you want to buy 2 shares of a 100<span>$</span> stock (this would be a 2x long). The bank/broker uses their capital to buy the two shares and holds your 100<span>$</span> collateral.

While the price fluctuates, the bank watches your position and the price of the stock. If the stock drops to <span>$</span>50, you've lost (2 shares * -\$50) = -<span>$</span>100, i.e, you've lost all the collateral the bank has, and so the bank would sell the 2 shares and collect your collateral for themselves (you got liquidated). They would also likely charge you a fee for the liquidation. 

Notice how much work the bank is doing throughout the process: 
- using their $$ buy additional shares for leverage 
- watching all the accounts for potential liquidations
- liquidating accounts and selling assets 

## Simple Decentralized Margin 

How can we make margin more decentralized? 

One way is to use borrowing/lending protocols like Solend or Compound.

For example, you can deposit 100\$ of ETH into a borrowing protocol and take out a 20\$  loan. You can then use the 20\$ loan to buy 20\$ more ETH. Then you would have a 120\$ position in ETH with only 100\$ in collateral (ie, a 1.2x long position).

Interestingly enough, the margin can be further increased by re-depositing the 20\$ loan of ETH as collateral and then taking out a second loan, which can be used to buy even more ETH.

However, since every \$ borrowed, is a \$ lent by someone else, you have to pay fees based on how much you borrowed and how long you borrowed it for (which comes directly out of your collateral). If this fee didn't exist, there would be no incentive to lend your \$ to the protocol. And if there are no lenders, there can't be any borrowers. 

## Perpetual Futures  

This leads us to perpetual futures which are better known as perps. 

For some background: Futures are financial contracts that agree to give you some number of shares sometime in the future (also known as an expiry date). Perpetual means forever / something with no expiry. Combining these two definitions, we get that perpetual futures are an agreement to give you some number of shares with no expiration date.

imo, there are two key ways to understand perps:
1. in a PvP setting (Player VS Player)
2. in a PvE setting (Player VS Everyone)

These two ways naturally build on top of each other.

## PvP Perps 

In a PvP setting, you have to find another trader to take the opposite side of the trade with you. For example, if you want to go long 10x on BTC then you need to find a trader who wants to go short 10x on BTC. You will also agree on what price the trade will start at (eg, the current price of BTC on coingecko).

Once you find a trader, agree on the start-price of BTC, as time passes, how do you settle your PnL? 

Let's say you're 10x long 1 ETH through a PvP perp and ETH goes up 10<span>$</span>. Then your PnL is now +100<span>$</span> (+10<span>$</span> x 10). To get your profits in the PvP perp, you have the other trader pay you X\% of the total PnL per hour. For example, if you and the trader agree to X\% = 10\%, then you will get paid [10\% of +100<span>$</span> PnL] per hour = [10<span>$</span>] per hour. In this case, after 10 hours, you will have your full PnL of +100<span>$</span> from your 10x long. 

*Note:* If ETH went down 10<span>$</span> you would pay the other trader 10<span>$</span> per hour. 

*Note:* The choice of the funding rate \% (10\%) and funding rate period (1 hour) can be chosen arbitrarily. 

Notice how there are no fees in this example compared to the previous section. 

## PvE Perps 

Now consider a marketplace example of the above. You now have many traders placing their long and short offers at different start prices with a list of bids & asks. In this setting, it starts off to work similar to the PvP perps, you pair up with another trader and you agree on a start-price. However, it begins to differ from here on out. 

First, instead of settling the PnL between traders using the difference between the start-price of the trade and the current price, the traders pay a funding rate which is equal to the difference between the marketplace's current price and the asset's ground-truth price. More specifically, the market defines 
- `mark price`: the price of the asset in the marketplace
- `oracle price`: the ground-truth price of the asset given by some oracle (i.e, the price on coingecko)

Furthermore, the market defines the `funding rate = mark price - oracle price` and defines the following rules:

- if **mark > oracle (funding rate = positive)**: **the longs pay the shorts** a % of their open position each hour -- (this creates **selling pressure** because you get paid to be short)
- if **mark < oracle**: **shorts pay the longs** a % of their open position each hour -- (this creates **buying pressure** because you get paid to be long)

These rules ensure that the market price is in line with the asset's price. Doing so can ensure that traders can enter and exit their positions at the correct prices, and therefore settle their PnL.

*Note:* The exact \% paid per hour (or another amount of time) for the funding rate is arbitrary and is decided by the marketplace.

## Funding Rates as Volume Bribes

If you assume all traders are informed of the current price -- say BTC is at 40K -- if a trader wants to go long, they should open a bid somewhere close to (or below) 40K -- similarily shorts should open an ask somewhere close to (or above) 40K. Placing bids too low, or asks too high won't lead to fills, so informed traders are naturally incentivized to place their orders around the ground-truth price. 

If there is enough of this trading/volume on the exchange, this 'price informed' trader volume would naturally lead to the market price reflecting the ground-truth price. In this case, there doesn't need to be a funding rate. If you remove the funding rates, you get decentralized leveraged trading that just works.  

However, in practice, I assume it's not always easy or safe to assume you will have enough volume to have the mark price match the oracle price. In this case, the funding rate acts as a bribe for more informed volume.  

Furthermore, note that the funding rate bribes are dynamic. When you have enough informed volume that the mark price matches the oracle price, the funding rate will be small, and so you are bribing less. The opposite is also true, when you don't have enough volume that the mark price diverges from the oracle price, then the funding rates increase, and you are offering a larger bribe for more volume. 

## Illiquid Cross-Exchange Perp Positions 

In normal token swap exchanges, this lack of volume / mark-oracle price difference problem is usually solved by arbitragers. When the decentralized exchange's price (mark price) is different from a centralized exchange's price (oracle price), an arbitrage opportunity for profit exists by trading across the dex and cex. 

However, since a perp position on one dex can't be swapped to another exchange (due to implementation details/complexities), swapping across perp exchanges can't be done. 

Arbitrage opportunities to keep the prices in line still exist though. Specifically, there is funding rate arbitrage. More on this maybe later... 

## Other
- Orderbook Perps: Mango 
- Virtual AMM Perps (vAMMs): Drift [maybe more soon...]
- Funding-rate arbitrage across different perp exchanges
