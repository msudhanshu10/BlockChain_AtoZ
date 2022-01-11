# -*- coding: utf-8 -*-
"""
Created on Fri Jan  7 11:51:06 2022

@author: msudh
"""

# Module 2- Create a Cryptocurrency
# Flask==0.12.2
# Postman HTTP client: https://www.getpostman.com/
# requests==2.18.4: pip install requests==2.18.4

#Importing the libraries
import datetime
import hashlib
import json
from flask import Flask,jsonify, request # to return messages
import requests
from uuid import uuid4
from urllib.parse import urlparse


#Part 1- Building a Blockchain
class Blockchain:
    def __init__(self):
        self.chain=[]
        self.transactions=[] #List containing transactions before they are added to the chain
        self.create_block(proof=1, previous_hash='0')
        self.nodes=set()
        
    def create_block(self, proof, previous_hash):
        block={'index':len(self.chain)+1,
               'timestamp':str(datetime.datetime.now()),
               'proof':proof,
               'previous_hash':previous_hash,
               'transactions':self.transactions}
        self.transactions=[]
        self.chain.append(block)
        return block
    
    def get_previous_block(self):
        return self.chain[-1] #gives the last block of the chain
    
    # PoW- hard to find but easy to verify
    def proof_of_work(self, previous_proof):
        new_proof=1 #at each iteration, increase this value by 1
        # Hit and trial method
        check_proof=False;
        while check_proof is False:
            #Defining the problem, miners need to solve
            #Four leading zeros
            hash_operation =hashlib.sha256(str(new_proof**2 - previous_proof**20).encode()).hexdigest() #Operation needs to be non-symmetrical
            if hash_operation[:4]=='0000': 
                check_proof=True
            else:
                new_proof=new_proof+1
        return new_proof
    def hash(self, block):
        encoded_block=json.dumps(block,sort_keys=True).encode()
        return hashlib.sha256(encoded_block).hexdigest()
    
    def is_chain_valid(self, chain):
        block_index = 1;
        previous_block = chain[0]
        while block_index < len(chain):
            block= chain[block_index]
            if(block['previous_hash'] != self.hash(previous_block)):
                return False
            previous_proof= previous_block['proof']
            proof = block['proof']
            hash_operation =hashlib.sha256(str(proof**2 - previous_proof**20).encode()).hexdigest()
            if(hash_operation[:4]!='0000'):
                return False
            previous_block=block
            block_index += 1
        return True
    
    def add_transaction(self, sender, receiver, amount):
        self.transactions.append({'sender':sender,
                                  'receiver':receiver,
                                  'amount':amount})
        previous_block= self.get_previous_block()
        return previous_block['index']+1 #return index of the block that will get these transactions
    
    def add_node(self, address):
        parsed_url=urlparse(address)
        self.nodes.add(parsed_url.netloc)
        
    #any chain which is shorter than the longer chain is replaced by the longer chain. We need to look at all the nodes.
    def replace_chain(self):
        network = self.nodes
        longest_chain = None
        max_length = len(self.chain)
        for node in network:
            response = requests.get(f'http://{node}/get_chain')
            if response.status_code == 200:
                length = response.json()['length']
                chain = response.json()['chain']
                if length > max_length and self.is_chain_valid(chain):
                    max_length = length
                    longest_chain = chain
        if longest_chain:
            self.chain= longest_chain
            return True
        return False
        
        
# Part 2- Mining out Blockchain

#Creating a Web App
app = Flask(__name__) #Instance of Flask class
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False

# Creating an address for the node on PORT 5000
node_address =  str(uuid4()).replace('-', '')

#Creating a Blockchain
blockchain = Blockchain() #instance of blockchain class

#Mining a new Block
@app.route('/mine_block', methods = ['GET'])
def mine_block():
    previous_block=blockchain.get_previous_block()
    previous_proof=previous_block['proof']
    proof= blockchain.proof_of_work(previous_proof)
    previous_hash= blockchain.hash(previous_block)
    blockchain.add_transaction(sender = node_address, receiver = 'Amit', amount = 10)
    block = blockchain.create_block(proof, previous_hash)
    response = {'message':'Congratulations, you just mined a block!',
                'index':block['index'],
                'timestamp': block['timestamp'],
                'proof' :block['proof'],
                'previous_hash' : block['previous_hash'],
                'transactions':block['transactions']
                }
    return jsonify(response), 200

@app.route('/get_chain', methods=['GET'])
def get_chain():
    response = {'chain':blockchain.chain,
                'length':len(blockchain.chain)}
    return jsonify(response), 200
 
#Checking if the blockchain is valid
@app.route('/is_valid', methods=['GET'])
def is_valid():
    is_valid = blockchain.is_chain_valid(blockchain.chain)
    if is_valid:
        response={'message':'All good, the blockchain is valid'}
    else:
        response={'message':'Houston, we have a problem. The blockchain is not valid'}
    return jsonify(response), 200

# Adding a new transaction to the Blockchain
@app.route('/add_transaction', methods = ['POST'])
def add_transaction():
    # We will create a json file in the postman and read transaction details from there.
    json = request.get_json()
    transaction_keys = ['sender' , 'receiver' , 'amount']
    if not all (key in json for key in transaction_keys):
        return 'Some elements of the transactions are missing', 400
    index = blockchain.add_transaction(json['sender'], json['receiver'], json['amount'])
    response = {'message': f'This transaction will be added to Block {index}'}
    return jsonify(response), 201
    
# Part 3: Decentralizing our Blockchain

# Connecting new nodes
@app.route('/connect_node', methods = ['POST'])
def connect_node():
    json = request.get_json()
    nodes = json.get('nodes') # containing the addresses of the nodes
    if nodes is None:
        return 'No Nodes', 400
    for node in nodes:
        blockchain.add_node(node)
    response = {'message': 'All the nodes are now connected. The sdcoin blockchain now contains the following nodes : ',
                'total_nodes':list(blockchain.nodes)}
    return jsonify(response) , 201

# Replacing the chain by the longest chain if needed
@app.route('/replace_chain', methods=['GET'])
def replace_chain():
    is_chain_replaced = blockchain.replace_chain()
    if is_chain_replaced:
        response={'message':'All good, The nodes had different chain, so chain was replaced by the longest chain. '}
    else:
        response={'message':'All good, The chain is the longest one.'}
    return jsonify(response), 200

#Running the app
app.run(host='0.0.0.0', port = 5003)



    
