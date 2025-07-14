from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
from dotenv import load_dotenv
import os

# Load env variables
load_dotenv()
app = Flask(__name__)
CORS(app)

# Connect to MongoDB Atlas
MONGO_URI = os.getenv("MONGO_URI")
API_KEY = os.getenv("API_KEY")
client = MongoClient(MONGO_URI)
db = client["plantDB"]
collection = db["plants"]

# Simple API key check
def check_api_key():
    key = request.headers.get("x-api-key")
    print("Received API key:", key)
    return key == API_KEY

@app.route("/")
def home():
    return jsonify({"message": "🌿 Plant API is live!"})

@app.route("/api/plants", methods=["GET"])
def get_all_plants():
    if not check_api_key():
        return jsonify({"error": "Unauthorized"}), 401
    plants = list(collection.find({}, {"_id": 0}))
    return jsonify(plants)

@app.route("/api/plant", methods=["GET"])
def get_plant_by_name():
    if not check_api_key():
        return jsonify({"error": "Unauthorized"}), 401
    name = request.args.get("name", "").lower()
    plant = collection.find_one({
        "$or": [
            {"common_name": {"$regex": f"^{name}$", "$options": "i"}},
            {"botanical_name": {"$regex": f"^{name}$", "$options": "i"}}
        ]
    }, {"_id": 0})
    if plant:
        return jsonify(plant)
    return jsonify({"error": "Plant not found"}), 404

if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))

