from fastapi import FastAPI, Body
from pydantic import BaseModel
from pymongo import MongoClient
from bson import ObjectId
from blockchain import Blockchain
from pymongo.errors import ConnectionFailure
from fastapi import Form

# MongoDB connection for local setup
MONGO_URI = "mongodb://localhost:27017/"  # Local MongoDB URI

try:
    client = MongoClient(MONGO_URI)
    print("MongoDB connected successfully.")
except ConnectionFailure as e:
    print(f"Failed to connect to MongoDB: {e}")

db = client["transactions"]  # Use the 'transactions' database
collection = db["transactions"]  # Use the 'transactions' collection

# Initialize Blockchain
blockchain = Blockchain()
app = FastAPI()

# Model for mining a block (Swagger will generate fields for these attributes)
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
def mine_block(tx: Transaction = Body(...)):
    """Mine a new block and store it in the database."""
    block = blockchain.mine_block(tx.sender, tx.receiver, tx.amount, tx.price)

    # Convert any ObjectId in the block to string
    block_serialized = convert_objectid_to_str(block)

    try:
        collection.insert_one(block_serialized)  # Insert into 'transactions' collection
    except Exception as e:
        print("DB Insert Error:", e)
        return {"error": str(e)}

    return {"message": "New block mined!", "block": block}

@app.get("/blocks")
def get_blocks():
    """Retrieve all blocks stored in MongoDB."""
    try:
        blocks = list(collection.find({}, {"_id": 0}))  # Exclude MongoDB's `_id` field
        blocks = convert_objectid_to_str(blocks)
        return {"blocks": blocks}
    except Exception as e:
        print("DB Read Error:", e)
        return {"error": str(e)}

@app.post("/mine-form")
def mine_block_form(
    sender: str = Form(...),
    receiver: str = Form(...),
    amount: float = Form(...),
    price: float = Form(...)
):
    block = blockchain.mine_block(sender, receiver, amount, price)

    # Convert and insert into DB
    block_serialized = convert_objectid_to_str(block)
    try:
        collection.insert_one(block_serialized)
    except Exception as e:
        return {"error": str(e)}

    return {"message": "Block mined via form!", "block": block}