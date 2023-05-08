from solana.rpc.api import Client

client = Client("https://api.mainnet-beta.solana.com")

print(client.get_epoch_info())
# print(client.get_leader_schedule())

# {
#     "4Qkev8aNZcqFNSRhQzwyLMFSsi94jHqE8WNVTJzTP99F": [
#       0, 1, 2, 3, 4, 5, 6, 7, 8, 9, ... 
#     ],
#     "EkSnNWid2cvwEVnVx9aBqawnmiCNiDgp3gUdkDPTKN1N": [
#       10, 11, 12, 13, 14, 15, 16, 17, 18, 19, ... 
#     ],
#     ... 
# }
resp = client.get_leader_schedule()
