from pymongo import MongoClient
MONGO_URI = "mongodb://localhost:27017"

client = MongoClient(MONGO_URI)

# Database dùng cho project
db = client["product_db"]
products_collection = db["products"]
users_collection = db["users"]
refresh_tokens_collection = db["refresh_tokens"]
blacklist_collection = db["blacklist"]