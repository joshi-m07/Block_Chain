import hashlib
import json
from time import time
#blockchain
class Blockchain:
    def __init__(self):
        self.chain = []
        self.transactions = []
        self.create_block(proof=1, previous_hash='0')

    def create_block(self, proof, previous_hash):
        block = {
            'index': len(self.chain) + 1,
            'timestamp': time(),
            'transactions': self.transactions,
            'proof': proof,
            'previous_hash': previous_hash
        }
        self.transactions = []
        self.chain.append(block)
        return block

    def get_previous_block(self):
        return self.chain[-1]

    def proof_of_work(self, previous_proof):
        new_proof = 1
        while True:
            hash_op = hashlib.sha256(str(new_proof**2 - previous_proof**2).encode()).hexdigest()
            if hash_op[:4] == '0000':
                return new_proof
            new_proof += 1

    def hash(self, block):
        return hashlib.sha256(json.dumps(block, sort_keys=True).encode()).hexdigest()

    def is_chain_valid(self, chain):
        for i in range(1, len(chain)):
            prev = chain[i - 1]
            curr = chain[i]
            if curr['previous_hash'] != self.hash(prev):
                return False
            if not self.valid_proof(prev['proof'], curr['proof']):
                return False
        return True

    def valid_proof(self, prev_proof, new_proof):
        hash_val = hashlib.sha256(str(new_proof**2 - prev_proof**2).encode()).hexdigest()
        return hash_val[:4] == '0000'

    def add_transaction(self, sender, receiver, amount):
        self.transactions.append({
            'sender': sender,
            'receiver': receiver,
            'amount': amount
        })
        return self.get_previous_block()['index'] + 1
