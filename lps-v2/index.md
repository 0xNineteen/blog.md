
# Implementing Liquidity Providing: Uniswap and Drift-v2

<div align="center">
<img src="2022-11-21-10-40-52.png" width="450" height="300">
</div>

Uniswap was the first implementations of liquidity providing (lp-ing) which allowed 
traders to earn a slice of the protocol fees for providing their assets in swaps. Before 
we explain how Drift-v2 implements liquidity providing, its helpful to understand how 
uniswap implements liquidity providing. 

## Uniswap LPs

Uniswap operates over reserve values, x and y which are the amount of asset X and asset Y in the pool. 
For example, X = btc and Y = usdc. The pools work by maintaining the constant produce x * y = k where k is how much 
liquidity is available to trade. A larger k value means less slippage per trade. 

### Adding + Removing Liquidity 

When a user adds liquidity/mints lp tokens to the pool they first define how much assets to deposit x' and y'. Depositing 
x' and y' amounts leads to new reserve values (x + x'), (y + y') and an increased k value. This also 
results in minting new lp tokens, giving them to the user, and updating the total number of lp tokens minted. 

When a user removes liquidity/burns lp tokens they get the reserve amounts relative to how many lp tokens 
theyre burning and the total number of lp tokens minted. 
Then the reserve amounts are decreased (x - x'), (y - y'), k is decreased, 
and the total number of lp tokens is also decreased.

For example, if the reserves are x, y = 100, 100 with 100 lp tokens minted in total and an lp adds x', y' = 50, 50
then 50 lp tokens are minted as the user is providing (50/150 = 33%) of the liquidity to the pool. The reserves are then
updated to be x, y = 150, 150, k is updated to be 150 * 150, and 150 lp tokens minted in total is tracked. 
When an lp removes they burn 50 lp tokens, so they get (reserves * n_tokens / total_tokens) 150 * 50/150 = 50 of x and y reserves, 
the reserves are decreased to x,y = 100, 100, k is decreased, and total lp tokens is updated to be 100. 

### Earning Fees

How do the lps earn fees? Say the fee percentage is 1% and a user swaps 100 of X for some token Y. Then the swap is perfomed with 99 X tokens
and the 1 token X remains in the reserves; the reserves will be equal to x, y = 101, 100 before the swap of 99 X tokens.
When the lps burn their tokens they will recieve a larger amount from when they minted because of the increase in reserves.

## Drift Perpetual Future LPs 

Perpetual future DEXs are different from Uniswap DEXs because all the liquidity is virtual. Furthermore, since Drift's AMM 
is highly dynamic, it allows anyone to leverage the power of the DAMM just by minting lp tokens. If lps are taking on positions,
we need to be able to track things like pnl and leverage easily to know when to liquidate lps.

So, how did we do it in Drift? Most of the code can be read [here](https://github.com/drift-labs/protocol-v2/blob/master/programs/drift/src/controller/lp.rs).

### Adding Liquidity 

When an lp adds liquidity, they choose how many lp tokens to mint, if they choose Z tokens to mint then sqrt_k is increased 
by Z (sqrt_k' = sqrt_k + Z) which leads to an increase in x and y. Next, we track the amm's values of amm.base_amount_per_lp and 
amm.quote_amount_per_lp (base refers to the asset being traded, ie SOL, and quote refers to USDC) with the lp's .last_ values. 

```rust 
// track amm's metrics
position.last_net_base_asset_amount_per_lp = amm.base_asset_amount_per_lp.cast()?;
position.last_net_quote_asset_amount_per_lp = amm.quote_asset_amount_per_lp.cast()?;

// ... 

// increase k 
let new_sqrt_k = sqrt_k.safe_add(n_shares.cast()?)?;
let update_k_result = get_update_k_result(market, new_sqrt_k_u192, true)?;
update_k(market, &update_k_result)?;
```

As traders trade against the amm, amm's per_lp variables change to take on the opposite side of the trade. For example, 
if a user goes long 100 SOL for 100 usdc (+100 base, -100 quote) and theres one lp with 100 lp tokens (ignoring the AMM), 
then the amm.base_per_lp += 1 (100 base / 100 lp tokens) and amm.quote_per_lp += -1 (-100 quote / 100 lp tokens) + slice of fee paid.

Note: the amm gets some of the oppposite side too (since sqrt_k is its number of lp tokens). 

```rust 
let per_lp_delta_base = get_proportion_i128(
    delta.base_asset_amount.cast()?,
    AMM_RESERVE_PRECISION,
    market.amm.sqrt_k,
)?;

let per_lp_delta_quote = get_proportion_i128(
    delta.quote_asset_amount.cast()?,
    AMM_RESERVE_PRECISION,
    market.amm.sqrt_k,
)?;

market.amm.base_asset_amount_per_lp = market
    .amm
    .base_asset_amount_per_lp
    .safe_add(-per_lp_delta_base)?;

market.amm.quote_asset_amount_per_lp = market
    .amm
    .quote_asset_amount_per_lp
    .safe_add(-per_lp_delta_quote + fee)?;
```
[ref](https://github.com/drift-labs/protocol-v2/blob/2e44f98f6e49e1325bdc80d129037aeab2891e41/programs/drift/src/controller/position.rs#L372)

### Removing Liquidity 

When an lp burns their lp tokens, we take the difference between the amm's current per_lp values and their .last_ values, multiplied by 
the number of lp tokens. 

```rust 
// give them slice of the damm market position
let amm_net_base_asset_amount_per_lp = amm
  .base_asset_amount_per_lp
  .safe_sub(position.last_net_base_asset_amount_per_lp.cast()?)?;

let base_asset_amount = amm_net_base_asset_amount_per_lp
  .cast::<i128>()?
  .safe_mul(n_shares_i128)?
  .safe_div(AMM_RESERVE_PRECISION_I128)?;

let amm_net_quote_asset_amount_per_lp = amm
  .quote_asset_amount_per_lp
  .safe_sub(position.last_net_quote_asset_amount_per_lp.cast()?)?;

let quote_asset_amount = amm_net_quote_asset_amount_per_lp
  .cast::<i128>()?
  .safe_mul(n_shares_i128)?
  .safe_div(AMM_RESERVE_PRECISION_I128)?;

Ok((base_asset_amount, quote_asset_amount))
```
[ref](https://github.com/drift-labs/protocol-v2/blob/2e44f98f6e49e1325bdc80d129037aeab2891e41/programs/drift/src/math/lp.rs#L23)

### Settling LPs

We also have another operation called Settle_LP which gives the lp an actual position and updates their .last_ variables to be equal to 
the amm's per_lp values. This allows for the lp position to settle their positive/negative pnl like a normal position. I'll leave why we need
'settled' pnl for another post. 

### LP Script for the DAMM

Alpha: If you're interested in adding liquidity to Drift's perp market and leverage the power of the DAMM for your own trading you can use the 
python script below [here](https://github.com/drift-labs/driftpy/blob/master/examples/start_lp.py) (the UI is still in the works):
```python 
python start_lp.py 
--keypath ./x19.json # keypair path
--env mainnet 
--amount 30  # 30 lp tokens
--market 0 # SOL index
```

<!-- 
- perps dex style 
  - perps are different because all liquidity is virtual 
    - if lps are taking on positions we need to be able to track things like pnl and leverage easily to know when to liquidate lps
  - how we do it in drift v2 ... 
  - when lps mints lp tokens, they increase the amount of liquidity in the market by increasing sqrt_k
    - if they mint 100 lp tokens, amm's sqrt_k is now + 100 
    - larger sqrt_k values mean less slippage for traders 
  - next we track the current values of amm.baa_per_lp and amm.qaa_per_lp in the .last_ variables of the perp position
    - as traders trade, the amm's variables for these will change, taking on the opposite side of the trade
    - notes these values are 'per-lp-token': 
      - in the case when a user goes long 100 SOL for 100 usdc (+100baa, -100qaa):
        - theres one lp with 100 lp tokens and then the lp variables will change to (-1 baa, +1 qaa + lp's slice of fee)
      - ie, 
        - ** code here ** 
        - note: the amm gets some of the oppposite side too (sqrt_k is its number of lp tokens)
    - when an lp burns their lp tokens we take the difference between their .last_ variables and the .amm's variables and scale it by the number of tokens 
      - ie, 
        - base_amount = (lp.last_baa - amm.baa_per_lp) * n_tokens
        - quote_amount = (lp.last_qaa - amm.qaa_per_lp) * n_tokens
  - becuase of how pnl works when an lp is settled their position is taken on and their negative/positive pnl can then be settled like a normal position 
    - why we need 'settled' pnl is for another blog post but you can read about it at (drift website on pnl)

- uniswap was first for liquidity providing (lp-ing)
  - x * y = k where x and y are the asset reserves for asset x and asset y (eg, asset x = BTC, asset y = USDC)
- when a user adds lp: 
  - get amount of lp tokens relative to input amount and the current reserve amount 
  - increase both reserves and k and increase total amount minted 
- when a user removes lp: 
  - get reserve amount relative to burn amount and total minted 
  - decrease reserve amount and total amount minted
- eg. 
  - reserves = 100, 100 with 100 lp tokens already minted
    - lp adds
        - user adds 50, 50 (50% of liquidity added -- 50 lp tokens minted)
        - reserves' = 150, 150 with 150 lp tokens removed 
    - lp removes 
      - user burns 50 lp tokens (150 * 50 / 150) = 50 
      - give back 50 of reserves, decrease total minted lp tokens by 50  
- how do the lps earn fees 
  - on user swap 100 A -> amount of token B 
    - if fee is 1% 
    - perform swap with 99% of input amount and put the extra input amount back into the pool 
        - ie, increase A reserves to 101, 100 and perform swap with 99 A
    - assuming someone swaps back to the normal reserves (trades 100 B after A trade)
        - new reserves will be 101, 101
        - when lps burn they will recieve a larger slice of A and B  -->
