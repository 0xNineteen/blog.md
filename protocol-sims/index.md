# Building Robust Protocols With Simulations
- most protocols seem to rely on rust or js test to ensure everything works as expected
- this handles simple cases but cant handle more complex interactions 
  - eg, can handle 1 user opening a long but cant handle 100 users opening random positions 
- simulating larger interactions can lead to finding edge cases and complex interactions which can lead to discovering new bugs 
- large simulations cant test things which unit tests cant but how do we actually find the bugs? 
  - invariants 
- invariants are statements which should always hold true for your protocol 
  - for example, one invariant could be that the net user position = number of longs + number of shorts 
  - [validate.rs] in drift includes all the invaraints we check for in drift 
  - [open_position.rs] checks invariants on the market and user account after every interaction 
- throughout the simulations you simply check these invariants hold after each interaction and when errors are thrown, bugs can be found 
- these large simulations are similar to fuzz testing where random inputs are given to functions to discover bugs 

## Verifying Mainnets Saftey
- testing different states 
  - while large simulations can test random scenarios, sometimes its better to test against the state of mainnet 
    - eg, if everyone were to be closed out right now, would all the pnl add up? 
    - this leads to cloning the mainnet state, loading the state into a local validator, and then running a predeterminted list of interactions (everyone closes)
    - this can be run like a bot and when things dont add up - alarms can be set off to fix the problem before it becomes a problem 

## Reproducability 
- reproducability and simulation unit tests
  - allowing your simulations to be reproducable by loging the events can allow for unit-test like testing with simulations 
    - [events.csv] includes all the events to backtest the protocol on - these can be shared with other devs which can then reproduce and debug the simulation together 
    - these simulations can also be run after every new deployment 

## Improved Bug Detection 
- improved detection 
  - sometimes deriving invariants is difficult 
  - machine learning can be used to detect anomalies in the interactions and the changes of state 
  - a simple model would collect data such as (state, tx, state') and then learn a model when the new state isnt as the model expected 
  - or when the state is in a new state never seen before - which could 

## Optimal Protocol Parameter Studying 
- testing different parameters and their performance in different market scenarios can be achieved with simulations