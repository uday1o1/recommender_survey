from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pymongo import MongoClient
from dotenv import load_dotenv
import certifi
import os

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

client = MongoClient(os.getenv("MONGO_URI"), tlsCAFile=certifi.where())
db = client["skills_survey"]
collection = db["responses"]

@app.post("/submit")
async def submit(data: dict):
    try:
        email = data.pop("email", None)
        collection.insert_one(data)
        if email:
            db["emails"].insert_one({
                "email": email,
                "submitted_at": data.get("submitted_at")
            })
        return {"status": "success"}
    except Exception as e:
        print(e)
        return {"status": "error", "message": str(e)}