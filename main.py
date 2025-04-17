from fastapi import FastAPI
from pydantic import BaseModel
from pymongo import MongoClient 
from bson import ObjectId
from blockchain import Blockchain
from pymongo.errors import ConnectionFailure

from pymongo import MongoClient
from pymongo.errors import ConnectionFailure

# MongoDB connection
MONGO_URI = "mongodb://mohamed:mohamed123@cluster0-shard-00-00.ayzka.mongodb.net:27017,cluster0-shard-00-01.ayzka.mongodb.net:27017,cluster0-shard-00-02.ayzka.mongodb.net:27017/?replicaSet=atlas-5qge6b-shard-0&ssl=true&authSource=admin&retryWrites=true&w=majority&appName=Cluster0"

try:
    client = MongoClient(
        MONGO_URI,
        tls=True,
        tlsAllowInvalidCertificates=True  # <== only for local testing
    )
    print("MongoDB connected successfully.")
except ConnectionFailure as e:
    print(f"Failed to connect to MongoDB: {e}")

db = client["blockchain"] #Mongodb database

# Initialize Blockchain
blockchain = Blockchain()
app = FastAPI()


# Model for mining a block
class Transaction(BaseModel):
    sender: str
    receiver: str
    amount: float
    price: float


# Utility function to convert MongoDB ObjectId to string
def convert_objectid_to_str(obj):
    """Convert MongoDB ObjectId to string recursively."""
    if isinstance(obj, dict):
        return {key: convert_objectid_to_str(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [convert_objectid_to_str(item) for item in obj]
    elif isinstance(obj, ObjectId):
        return str(obj)
    return obj


@app.get("/")
def home():
    return {"message": "Welcome to the Blockchain API!"}


@app.get("/blockchain")
def get_blockchain():
    """Fetch the entire blockchain from memory."""
    return {"chain": blockchain.get_chain(), "length": len(blockchain.get_chain())}


@app.post("/mine")
def mine_block(tx: Transaction):
    """Mine a new block and store it in the database."""
    block = blockchain.mine_block(tx.sender, tx.receiver, tx.amount, tx.price)

    # Convert any ObjectId in the block to string
    block_serialized = convert_objectid_to_str(block)

    try:
        db.transactions.insert_one(block_serialized)
    except Exception as e:
        print("DB Insert Error:", e)
        return {"error": str(e)}

    return {"message": "New block mined!", "block": block}


@app.get("/blocks")
def get_blocks():
    """Retrieve all blocks stored in MongoDB."""
    try:
        blocks = list(db.transactions.find({}, {"_id": 0}))  # Exclude MongoDB's `_id` field
        blocks = convert_objectid_to_str(blocks)
        return {"blocks": blocks}
    except Exception as e:
        print("DB Read Error:", e)
        return {"error": str(e)}
