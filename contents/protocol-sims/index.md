general gpt-3 prompts used to write post:

--- 
Bullet points to paragraphs

> Write a paragraph about how fuzzy testing can improve blockchain protocol's security using the following bullet points as the structure:
> - .... bullet points ...  

--- 
Title generation

> Generate a title from the following text:
> 
> ... full text ... 
> 
> Title: 

--- 
tldr generation

> Generate a short summary of the following text:
> 
> ... full text ... 
> 
> Summary: 
--- 

# Building Robust Protocols With Simulations
- smart contract security relies on tests
- simple unit tests are used
- this handles simple cases but cant handle more complex interactions 
  - eg, can handle 1 user opening a long but cant handle 100 users opening random positions 
- larger simulations = more complex interactions and edge cases to discovering new bugs 

## Large Scale Simulations
- large simulations cant test things which unit tests cant but how do we actually find the bugs? 
  - invariants 
- invariants are statements which should always hold true for your protocol 
  - for example, one invariant could be that the net user position = number of longs + number of shorts 
  - [validate.rs] in drift includes all the invaraints we check for in drift 
  - [open_position.rs] checks invariants on the market and user account after every interaction 
- throughout the simulations you simply check these invariants hold after each interaction and when errors are thrown, bugs can be found 
- these large simulations are similar to fuzz testing where random inputs are given to functions to discover bugs 

## Verifying Mainnets Saftey

- random interactions tests random states 
- good for finding edge cases 
- not always realistic states
- so sometimes its better to test against the current state on mainnet 
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