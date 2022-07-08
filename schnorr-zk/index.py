#%%
import rsa
import numpy as np 

#%%
(pub, priv) = rsa.newkeys(128)
e = pub.e
d = priv.d

#%%
n = pub.n
m = np.random.randint(0, 1e3)
m

#%%
# encrypt 
e_m = pow(m, e, n)

# decrypt 
_m = pow(e_m, d, n)

# verify 
_m == m 

#%%
# schnorr proof 

g = 19 # can be anything 
h = pow(g, d, n) # want to prove we know d 

# step 1: alice
r = np.random.randint(0, 1e3)
u = pow(g, r, n)

# step 2: bob 
c = np.random.randint(0, 1e3)

# step 3: alice 
z = r + d * c 

# step 4: bob 
left_side = pow(g, z, n)
right_side = (u * pow(h, c, n)) % n
left_side == right_side

#%%
#%%
#%%