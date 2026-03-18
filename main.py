from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pymongo import MongoClient
from supabase import create_client
from dotenv import load_dotenv
import certifi
import os
import json
import uuid

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

supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))

@app.post("/submit")
async def submit(data: str = Form(...), resume: UploadFile = File(None)):
    try:
        payload = json.loads(data)
        email = payload.pop("email", None)

        if resume:
            file_bytes = await resume.read()
            if len(file_bytes) > 1 * 1024 * 1024:
                return {"status": "error", "message": "Resume too large, max 1MB"}
            filename = f"{uuid.uuid4()}_{resume.filename}"
            supabase.storage.from_("resumes").upload(
                filename,
                file_bytes,
                {"content-type": resume.content_type}
            )
            payload["resume_url"] = f"{os.getenv('SUPABASE_URL')}/storage/v1/object/resumes/{filename}"

        collection.insert_one(payload)

        if email:
            db["emails"].insert_one({
                "email": email,
                "submitted_at": payload.get("submitted_at")
            })

        return {"status": "success"}
    except Exception as e:
        print(e)
        return {"status": "error", "message": str(e)}