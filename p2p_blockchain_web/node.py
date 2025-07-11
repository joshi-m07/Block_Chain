from flask import Flask, render_template, request, redirect, url_for, jsonify
from uuid import uuid4
from blockchain import Blockchain
import requests

app = Flask(__name__)
node_id = str(uuid4()).replace('-', '')
blockchain = Blockchain()
peers = set()

@app.route('/')
def home():
    return render_template('index.html', chain=blockchain.chain, peers=peers)

@app.route('/mine_block')
def mine_block():
    prev_block = blockchain.get_previous_block()
    proof = blockchain.proof_of_work(prev_block['proof'])
    prev_hash = blockchain.hash(prev_block)
    blockchain.add_transaction(sender='0', receiver=node_id, amount=1)
    blockchain.create_block(proof, prev_hash)

    # Notify all peers
    for peer in peers:
        try:
            requests.get(f'{peer}/replace_chain')
            print(f"[INFO] Broadcasted mined block to {peer}")
        except:
            print(f"[ERROR] Failed to contact {peer}")

    return redirect(url_for('home'))

@app.route('/add_transaction', methods=['POST'])
def add_transaction():
    sender = request.form['sender']
    receiver = request.form['receiver']
    amount = request.form['amount']
    blockchain.add_transaction(sender, receiver, int(amount))

    # Notify peers
    for peer in peers:
        try:
            requests.get(f'{peer}/replace_chain')
            print(f"[INFO] Broadcasted transaction to {peer}")
        except:
            print(f"[ERROR] Could not reach {peer}")

    return redirect(url_for('home'))

@app.route('/connect_node', methods=['POST'])
def connect_node():
    node_url = request.form['node']
    peers.add(node_url)
    return redirect(url_for('home'))

@app.route('/replace_chain')
def replace_chain():
    longest = blockchain.chain
    for node in peers:
        try:
            res = requests.get(f'{node}/get_chain').json()
            if res['length'] > len(longest) and blockchain.is_chain_valid(res['chain']):
                longest = res['chain']
        except:
            continue
    blockchain.chain = longest
    return redirect(url_for('home'))

@app.route('/get_chain')
def get_chain():
    return jsonify({'chain': blockchain.chain, 'length': len(blockchain.chain)})

if __name__ == '__main__':
    import sys
    port = 5000
    if len(sys.argv) > 1:
        port = int(sys.argv[1])
    app.run(host='0.0.0.0', port=port)
