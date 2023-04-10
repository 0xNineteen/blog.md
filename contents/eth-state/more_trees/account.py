from dataclasses import dataclass
from json import loads, dumps
import hashlib

@dataclass
class Account: 
    amount: int
    address: str 

    def digest16(self): 
        m = hashlib.sha256()
        data = bytes(self.serialize(), 'utf-8')
        m.update(data)
        digest = m.hexdigest()[:16]
        return digest

    def serialize(self):
        return dumps({"amount": self.amount, "address": self.address})

    @staticmethod
    def deserialize(data): 
        d = loads(data)
        account = Account(d['amount'], d['address'])
        return account

acc = Account(100, 'ball')
d = acc.serialize()
print(Account.deserialize(d))
print(acc.digest16())
