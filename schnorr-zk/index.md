# ZK 101: Schnorr's Protocol 

If you use crypto and own the latest shitcoins, then you own a wallet consisting of a public and private key. 

**Lets say you want to prove to your friends that you own your public key (and all the shitcoins belonging to it).** One way to do so would be to show your friend your private key. From the private key they can derive the corresponding public key and complete the verification. However,  that would be bad because they could sign any transaction using your private key and steal all your shitcoins. 

<div align="center">
<img src="2022-07-07-21-47-04.png" width="450" height="300">
</div>

Ideally, you want to prove to your friend you own a private key corresponding to your public key without revealing any information about your private key. 

**In this post we'll cover how to prove you know your private key without revealing it using a zero-knowledge (ZK) proof and implement it in python.** (You could also use [signature schemes](https://cryptobook.nakov.com/digital-signatures/rsa-signatures) but thats not as fun)

## Schnorr’s Identification Protocol 

We first define some things: 
- $x$: is our private key 
- $g$: is some value/message (can be anything)
- $h$: is g encrypted with our private key ($h = g^x$)
- $q$: is our modulus value (its the same as $n$ in the last [RSA post](https://github.com/0xNineteen/blog.md/blob/master/rsa-encryption/index.md))

<div align="center">
<img src="2022-07-07-21-12-12.png" width="700" height="500">
</div>

**figure 1** from [here](https://www.zkdocs.com/docs/zkdocs/zero-knowledge-protocols/schnorr/)

To understand whats going on, we'll implement the protocol step by step in python.

First, we can setup our public and private key, along with a random message $g$ and it's encryption $h$:

```python 
import rsa
import numpy as np 

## generate the public and private keys 
(pub, priv) = rsa.newkeys(128)
q = pub.n # mod value 
x = priv.d # private key -- we want to prove we know x

g = 19 # can be anything 
h = pow(g, x, q) # encrypted message (g^x mod q)
```

We'll then share the values for $q$ (our mod value), $g$ (some message), and $h$ (the message encrypted) with our friend.  

---

The first step of the protocol is to generate a random value $r$ and encrypt $g$ with it ($g^r$) to derive $u$. We'd then send $u$ to our friend. 

```python 
r = np.random.randint(0, 1e3)
u = pow(g, r, q)
```

The friend computes a new random value $c$ and sends it back to us. 

```python 
c = np.random.randint(0, 1e3)
```

We then compute $z = r + x * c$ and send $z$ to our friend. 

```python 
z = r + x * c 
```

They can then check if the following equality holds:

$$
\begin{equation}
g^z \stackrel{?}{=} u * h^c 
\end{equation}
$$

```python 
left_side = pow(g, z, q)
right_side = (u * pow(h, c, q)) % q

assert left_side == right_side # True 
```

To know why this works we can expand the variables and simplify 

$$
g^z \stackrel{?}{=} u * h^c 
$$ 

*Equation (1)*

$$
g^{r + x * c} \stackrel{?}{=} g^r * (g^x)^c
$$

$$
g^{r + x * c} \equiv g^{r + x * c} 
$$

*Note:* The heart of the ZK proof utilizes the math theorem $x^a * x^b = x^{a + b}$

*Footnote:* You can also checkout *homomorphic hiding* which is a way to operate on encrypted data.

Notice how in (1) our friend has no information on our private key ($x$) since they only know $z$, $u$, $h$, and $c$. Furthermore, we would only be able to give them a $z$ which makes (1) true if we know the private key $x$. So overall, we proved that we know our private key without revealing our private key. Thats ZK baby, woo! 
