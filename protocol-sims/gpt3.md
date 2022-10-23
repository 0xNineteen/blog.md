## How Fuzzy Testing and Large-Scale Simulations Can Improve Blockchain Protocol Security

**tldr;** Fuzzy testing and large-scale simulations can help improve blockchain protocol security by discovering bugs and anomalies that simple unit tests cannot. Additionally, these simulations can be used to find the optimal parameters for a market—all leading to a more stable and secure protocol.

## Large-Scale Simulations

Smart contract security relies on tests to ensure that the code is functioning as intended. Simple unit tests are typically used to test individual functions or small pieces of code however, unit tests can only handle simple cases and cannot check for bugs within more complex interactions. For example, a unit test may be able to verify everything is ok when a single user opens a long position, but it's likely unable to check everything's ok with 100 users opening random positions. 

## Finding Bugs in Large Sims: Invariants

While large-scale simulations can test things that unit tests cannot, how can we find the bugs within them? One way is with invariants. Invariants are statements which should always hold for your protocol. For example, one invariant we use in Drift is that the net user's position equals the number of longs plus the number of shorts. Throughout the simulations, you simply check that these invariants still hold after each interaction. When these invariants are false, errors are thrown and bugs can be found--similar to fuzz testing where random inputs are given to functions to discover bugs.

Note: The [validation/market.rs](https://github.com/drift-labs/protocol-v2/blob/72090942f5d880179f037911c8688175b74cbdde/programs/clearing_house/src/validation/market.rs#L11) file in the Drift repository includes all the invariants we check for our Market struct in Drift. The [orders.rs](https://github.com/drift-labs/protocol-v2/blob/72090942f5d880179f037911c8688175b74cbdde/programs/clearing_house/src/controller/orders.rs#L661) file checks invariants on the market and user account whenever an order is fulfilled.

## Realistic Simulations: Mainnet's State

While random state simulations are good for finding edge cases, they are not always realistic--which is why sometimes it's better to test against the current state on mainnet. For example: we could test what would happen if everyone were to close out their positions at the same time--something we couldn't do in the real world without causing major financial damage; but can easily simulate by cloning the mainnet's state in a test environment. If something were to go wrong during the simulation--like invariants not holding (eg. the net user's position does not equal the number of longs plus the number of shorts)--we would know that there is a bug in the code; this can be run as a bot and when things don't add up, alarms can be set off before it becomes a real problem.

## Logging Events For Reproducibility 

If we want our simulations to be reproducible, we need to log the events. This way, when bugs are detected, other developers can take these events, run them through the simulation, reproduce the result, and be able to debug the results together. These events can also be used to re-run specific simulations after every new protocol deployment. This way, we can be confident that our code is functioning as intended and that any new changes have not introduced any new bugs.

Note: [events.csv](https://github.com/drift-labs/drift-sim/blob/d5ece09a206570714e1ac1c3b8a897d881c9cded/backtest/examples/tmp/events.csv) is an event script that we can backtest against the protocol.

## Improved Bug Detection: Machine Learning

While deriving invariants is difficult, machine learning can be used to detect anomalies in the interactions and the changes of state. By training a model on historical data, we can detect when something unusual is happening that could indicate a bug. For example: if the number of longs suddenly decreases by a large amount, this could indicate that users are closing their positions en masse which could lead to a price crash. By detecting these anomalies early, we can investigate if everything is ok in these unusual states which can prevent major financial damage.

## Sims++: Discovering Optimal Market Parameters

Another use case for simulations is to find the optimal parameters for your market. For example, you may want to find the best collateralization ratio or the best interest rate for your market. By running simulations with different parameters, you can see how these parameters affect the market in different scenarios. This can help you find the optimal parameters for your market, leading to a more stable and secure protocol.

## Conclusion

In conclusion, fuzzy testing and large-scale simulations can help improve blockchain protocol security by discovering bugs and anomalies that simple unit tests cannot. Additionally, these simulations can be used to find the optimal parameters for a market—all leading to a more stable and secure protocol.

# Extra: Large-Scale Simulations against Drift's Perps AMM DEX

If you want to test out Drift simulations in python, check out the drift-sim repo: [https://github.com/drift-labs/drift-sim](https://github.com/drift-labs/drift-sim). 

# Acknowledgements 

s/o to GPT-3 for co-authoring this post with me.
s/o to [bigz_Pubkey](https://twitter.com/bigz_Pubkey) for deriving most of the invariants and working with me on the simulations @ Drift.
