# blog.md

- [Sig Progress Update on AccountsDB, RPC, Gossip](https://blog.syndica.io/sig-engineering-part-2-accountsdb-more/): a lot of Zig content including fast hashmap implementations, preallocating memory, and more (the accounts-db section was me).

- [How Solana's Gossip Protocol Works](https://blog.syndica.io/sig-engineering-1-gossip-protocol/): technical explainer on Solana's gossip protocol and how its implemented.

- [Sig: Solana's 3rd Validator](https://blog.syndica.io/introducing-sig-by-syndica-an-rps-focused-solana-validator-client-written-in-zig/): were building a Solana node in Zig from scratch! also includes why and how were gonna build it.

- [Building Blocks in the Solana-Labs Validator](https://github.com/0xNineteen/blog.md/blob/master/contents/sol-blocks/index.md): how blocks are built in the solana-labs validator client.

- [Solana's Transaction Validating Unit (TVU)](https://github.com/0xNineteen/blog.md/blob/master/contents/sol-tvu/index.md): how Solana's TVU verifies, processes, and votes on new blocks from the network.

- [Sending Transactions and Open-Source RPC Projects on Solana](https://github.com/0xNineteen/blog.md/blob/master/contents/sol-rpcs/index.md): how sending a tx to a RPC on solana works, and two interesting open source RPC projects.

- [ETH State Managment: Trees, Treis, Tries](https://github.com/0xNineteen/blog.md/blob/master/contents/eth-state/index.md): iteratively implements blockchain state storage, ultimately explaining how ETH does it.

- [Zero-fee, Zero-slippage, Revenue Generating, Perps Dex](https://github.com/0xNineteen/blog.md/blob/master/contents/zero-fee-dexs/index.md): how we can build a zero-fee, zero-slippage, perps dex that still earns $$.

- [LPs for Token and Perp AMMs: Uniswap-v2 and Drift-v2](https://github.com/0xNineteen/blog.md/blob/master/contents/lps-v2/index.md): implementation overview of liquidity providers for Uniswap-v2 and Drift-v2. 

- [Consensus 101: The Dolev-Strong Protocol](https://github.com/0xNineteen/blog.md/blob/master/contents/blockchain-01/dolev.ipynb): python implementation of the Dolev-Strong Protocol which works even with 99% evil nodes.  

- [Fuzzy Testing and Large-Scale Simulations For Improved Protocols](https://github.com/0xNineteen/blog.md/blob/master/contents/protocol-sims/gpt3.md): how fuzzy testing and large-scale simulations can help improve blockchain protocol security by discovering bugs and anomalies that simple unit tests cannot.

- [Drift V2: DAMM JIT](https://twitter.com/0xNineteen/status/1571926865681711104?s=20&t=NoH3aXLAh7DRgxh46T8j-w): new feature that allows the AMM to take a slice of maker orders so its long/short imbalance is always guaranteed to improve; the protocol essentially frontruns maker orders (PEV example irl). 

- [PEV: Protocol Extractable Value](https://github.com/0xNineteen/blog.md/blob/master/contents/mev-v2/index.md): how protocols are in the position to extract value (which is currently being extracted by validators) that can generate more revenue for the protocol's dao, treasury, or users. 

- [ZK 101: Schnorr's Protocol](https://github.com/0xNineteen/blog.md/blob/master/contents/schnorr-zk/index.md): one of the simplest ZK proofs in the book: proving you own a private key without revealing it (python code included).

- [RSA Public-Key Cryptography](https://github.com/0xNineteen/blog.md/blob/master/contents/rsa-encryption/index.md): proof that RSA public-key cryptography encryption and decryption works. 

- [The Evolution of Margin in Crypto: The Birth of Perps](https://github.com/0xNineteen/blog.md/blob/master/contents/crypto-margin-perps/index.md): brief overview about understanding the pros of perps and how they work in a PvP and PvE setting.  

- [Rust Macros and Arbitrage Bots on Solana](https://github.com/0xNineteen/blog.md/blob/master/contents/rust-macros-arbitrage/index.md): practical example of how to use rust macros. The example includes writing an arbitrage bot for Solana.

- [A New Perspective on BTC's POW](https://github.com/0xNineteen/blog.md/blob/master/contents/btc-consensus/index.md): short post on how BTC's POW is a decentralized clock which doesn't require any coordination/agreement on time.

--- 

- [More Solana Rust Client Diagrams](https://github.com/0xNineteen/blog.md/blob/master/contents/diagram-dump/index.md): rando diagrams which never made it into a blogpost but still
could be useful.

- [braindump: PBFT and blockchain consensus](https://github.com/0xNineteen/blog.md/blob/master/contents/btc-pbft/index.md): brain dump on some thoughts of PBFT and blockchain consensus algos (btc, tendermint, solana).

- [Random Gists](https://gist.github.com/0xNineteen): rando code snippets 

- [Random Thoughts: Zero Knowledge to BulletProofs](https://github.com/0xNineteen/blog.md/blob/master/contents/reflecting-0k2bp/index.md): random thoughts of mine while learning how bulletproofs/vector-commitments/range-proofs/ring-sigs work.
