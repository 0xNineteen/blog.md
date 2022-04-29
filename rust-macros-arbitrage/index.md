# Rust Macros and Arbitrage Bots on Solana 

When starting to develop in rust, macros sounded like a magical beast: really cool but no clue how to use them in practice. While developing a solana arbitrage bot in rust, I naturally came across use cases where rust macros shined. In this post, we're gonna go over a more practicle example to understand them. 

## Arbitrage

In a nutshell, arbitrage on Solana is trading tokens across different exchanges (DEXs / AMMs) (all of which have different prices) in a way that at the end of the trade you have more of a token than when you started. 

For example, if market A's price of BTC is 40K and market B's price of BTC is 50K, you can buy 1BTC on A and sell it on market B for a 10K profit. The token trading would be 40K USD -A-> 1 BTC -B-> 50K USD: profit = 50K - 40K = 10K. 

## Atomic Transactions 

In Solana, the basic approach to develop an arbitrage bot is to have a transaction (tx) include a series of trade/swap instructions (ixs) and at the end, have an ix which reverts based on if you made a profit or not. If you didn't make a profit, the tx (and all previous ixs) are reverted. If you did make a profit, it does nothing. 

For example, the list of txs in the above example would be 

`[`
- `buy(market_A, 1BTC),`
- `sell(market_B, 1BTC),`
- `require(new_usd_balance > init_usd_balance)`

`]`

where `require` reverts the transaction if the condition isn't satisfied. 

## Accounting For Slippage 

One problem you need to account for is slippage. Slippage is when you get less of an asset than what you were originally quoted for because other trader's trades went through before your trade. 

For example, let's say the `buy(market_A, 1BTC)` order actually only gets `0.99BTC` bc of slippage, then `sell(market_B, 1BTC)` would fail because you're trying to sell 1BTC when you only have 0.99BTC. The same problem occurs when you get more of an asset than what you accounted for.

To account for this, we can record how much output we get per trade as `output = amount_post_swap - amount_pre_swap`. To implement this in Solana, since there is no global state, you actually need another account which will store this information across trades. So it's more like:

`[`
- `set swap_state = 40K`
- `buy(market_A, swap_state),`
- `sell(market_B, swap_state),`
- `require(init_usd_balance < new_usd_balance)`

`]`

where `buy(market_A, swap_state)` reads the state, swaps the amount which is read (e.g, `buy(market_A, 40K)`), and then updates the `swap_state` to be the output of the swap (`swap_state = 1BTC`) (which is then the input for the next swap). 

*Note:* this slippage / input-output amount / swap_state logic must all be on-chain, which requires us to create our own program. 

## Developing an On-Chain Program

To recap, we need something like this: 

```rust
fcn swap_market_A(accounts) {
    // compute: amount_in = swap_state
    // perform: swap on market A with amount_in
    // save: swap_state = amount_post_swap - amount_pre_swap
}
```

*Note:* Each exchange takes a different set of accounts so you need a different function for each exchange. 

For example, when building a bot with Anchor, to swap on the Orca AMM or the Saber AMM, you need two functions which take their own `Context` objects:

```rust 
pub fn orca_swap<'info>(ctx: Context<'_, '_, '_, 'info, OrcaSwap<'info>>) -> Result<()> {
    // prepare the swap -- compute amount_in
    ... 
    // swap it 
    _orca_swap(ctx, amount_in); 
    // end the swap -- record swap output amount 
    ... 
}
pub fn saber_swap<'info>(ctx: Context<'_, '_, '_, 'info, SaberSwap<'info>>) -> Result<()> {
    // prepare the swap 
    ... 
    // swap it 
    _saber_swap(ctx, amount_in); 
    // end the swap 
    ... 
}
```

where `_orca_swap` and `_saber_swap` are the functions which perform the swap for their exchange.

*Notice:* `OrcaSwap<'info>` and `SaberSwap<'info>` are different types. 

## A Single Strongly-Typed Function? 

Since they are both simple AMM pools, their `Context`s will follow a very similar structure (e.g., pool source, pool destination, user src ATA, user dst ATA, etc.), but they aren't the same. Ideally, to reduce the amount of code duplication, we want something like: 

```rust 
pub fn amm_swap(swap_fcn: F<**???**>, ctx: Context<**???**>) {
    // prepare swap -- amount in = output of previous swap 
    let amount_in = prepare_swap(&ctx.accounts.swap_state);
    let amount_pre_swap = ctx.accounts.user_dst.balance;

    // do the swap 
    swap_fcn(&ctx, amount_in);

    // end swap -- record the output of the swap 
    let swap_state = &mut ctx.accounts.swap_state;
    let amount_post_swap = ctx.accounts.user_dst.balance;
    end_swap(swap_state, amount_post_swap - amount_pre_swap);
}
```

but, we have no clue what type we should use for ctx. It should support both `OrcaSwap` and `SaberSwap` types, but you can't do that in rust, everything must be strongly typed. Similarly, how do we give a type to F ??? Fear not, macros will save the day. 

## The Solution: Rust Macros

The solution is to create a macro which will *write* a function given a context and function:

```rust 
#[macro_export]
macro_rules! basic_amm_swap {
    ($swap_fcn:expr, $typ:ident < $tipe:tt > ) => {{
        |ctx: Context<'_, '_, '_, 'info, $typ<$tipe>> | -> Result<()> {
            // prepare swap 
            let amount_in = prepare_swap(&ctx.accounts.swap_state).unwrap();

            // do swap 
            $swap_fcn(&ctx, amount_in).unwrap();

            // end swap 
            let swap_state = &mut ctx.accounts.swap_state;
            let user_dst = &mut ctx.accounts.user_dst;
            end_swap(swap_state, user_dst).unwrap();

            Ok(())
        }
    }};
}
```

Notice we are extracting the type of the `Context` object using `$typ:ident < $tipe:tt > ` and then using that to **create** a callable function `|ctx: Context<'_, '_, '_, 'info, $typ<$tipe>> |`.

Notice the macro also takes in an arbitrary function `$swap_fcn:expr` and calls it with `$swap_fcn(&ctx, ...)` to perform the swap.

This is the power of rust macros: code that writes code! In this case, code that writes a function. 

We can then call the macro:

```rust 
pub fn orca_swap<'info>(ctx: Context<'_, '_, '_, 'info, OrcaSwap<'info>>) -> Result<()> {
    basic_pool_swap!(_orca_swap, OrcaSwap<'info>)(ctx)
}

pub fn saber_swap<'info>(ctx: Context<'_, '_, '_, 'info, SaberSwap<'info>>) -> Result<()> {
    basic_pool_swap!(_saber_swap, SaberSwap<'info>)(ctx)
}
```

And it just works. Magical. 
