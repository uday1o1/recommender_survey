from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pymongo import MongoClient
from supabase import create_client
from dotenv import load_dotenv
import certifi
import os
import json
import uuid
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

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

dbms_db = client["dbms_survey"]
dbms_collection = dbms_db["responses"]

supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))

ALLOWED_TYPES = [
    "application/pdf",
    "application/msword",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
]

        if matched:
            # Upload updated xlsx back to Supabase
            output = io.BytesIO()
            wb.save(output)
            output.seek(0)
            supabase.storage.from_(XLSX_BUCKET).update(
                XLSX_PATH,
                output.read(),
                {"content-type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"}
            )
        return matched
    except Exception as e:
        print(f"Student ID matching failed: {e}")
        return False


def send_notification(payload, resume_url, form_type="ai"):
    try:
        profile = payload.get("profile", {})
        skills = payload.get("skills", {})
        prefs = payload.get("preferences", {})
        exp = payload.get("experience", {})
        ctx = payload.get("context", {})

        resume_line = f'<p><strong>Resume:</strong> <a href="{resume_url}">View Resume</a></p>' if resume_url else '<p><strong>Resume:</strong> Not uploaded</p>'
        form_label = "DBMS & Data Engineering" if form_type == "dbms" else "AI/ML"

        html = f"""
        <html><body style="font-family:Arial,sans-serif;max-width:600px;margin:0 auto;padding:20px">
        <h2 style="color:#4f46e5">New {form_label} Survey Submission</h2>
        <p style="color:#6b7280">Submitted at: {payload.get("submitted_at","")}</p>

        <h3 style="color:#374151;border-bottom:1px solid #e5e7eb;padding-bottom:6px">Academic Profile</h3>
        <p><strong>Year:</strong> {profile.get("academic_year","")}</p>
        <p><strong>Degree:</strong> {profile.get("degree","")}</p>
        <p><strong>Major:</strong> {profile.get("major","")}</p>
        <p><strong>GPA:</strong> {profile.get("gpa","")}</p>
        <p><strong>Experience:</strong> {profile.get("research_experience") or profile.get("industry_experience","")}</p>
        <p><strong>Career Goal:</strong> {profile.get("career_goal","")}</p>
        <p><strong>Coursework:</strong> {", ".join(profile.get("coursework", []))}</p>

        <h3 style="color:#374151;border-bottom:1px solid #e5e7eb;padding-bottom:6px">Skills</h3>
        <p>{", ".join([f"{k} ({['','Beginner','Intermediate','Advanced','Expert'][v]})" for k,v in skills.items() if v > 0])}</p>

        <h3 style="color:#374151;border-bottom:1px solid #e5e7eb;padding-bottom:6px">Preferences</h3>
        <p><strong>Roles:</strong> {", ".join(prefs.get("roles", []))}</p>
        <p><strong>Companies:</strong> {", ".join(prefs.get("companies", []))}</p>
        <p><strong>Work Style:</strong> {", ".join(prefs.get("work_style", []))}</p>
        <p><strong>Duration:</strong> {", ".join(prefs.get("duration", []))}</p>
        <p><strong>Locations:</strong> {", ".join(prefs.get("locations", []))}</p>

        <h3 style="color:#374151;border-bottom:1px solid #e5e7eb;padding-bottom:6px">Experience</h3>
        <p><strong>Past Roles:</strong> {", ".join(exp.get("past_roles", []))}</p>
        <p><strong>Projects:</strong> {", ".join(exp.get("projects", []))}</p>
        <p><strong>Found opportunity via:</strong> {exp.get("opportunity_source","")}</p>

        <h3 style="color:#374151;border-bottom:1px solid #e5e7eb;padding-bottom:6px">Context</h3>
        <p><strong>Timeline:</strong> {ctx.get("timeline","")}</p>
        <p><strong>Biggest Barrier:</strong> {ctx.get("barrier","")}</p>
        <p><strong>Usefulness Rating:</strong> {ctx.get("usefulness","")}</p>
        <p><strong>Ideal Role:</strong> {ctx.get("ideal_role","")}</p>

        {resume_line}
        </body></html>
        """

        msg = MIMEMultipart("alternative")
        msg["Subject"] = f"New {form_label} Survey Submission"
        msg["From"] = os.getenv("GMAIL_USER")
        msg["To"] = os.getenv("PROF_EMAIL")
        msg.attach(MIMEText(html, "html"))

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(os.getenv("GMAIL_USER"), os.getenv("GMAIL_APP_PASSWORD"))
            server.sendmail(os.getenv("GMAIL_USER"), os.getenv("PROF_EMAIL"), msg.as_string())

    except Exception as e:
        print(f"Email notification failed: {e}")


@app.api_route("/health", methods=["GET", "HEAD"])
async def health():
    return {"status": "ok"}


@app.post("/submit")
async def submit(data: str = Form(...), resume: UploadFile = File(None)):
    try:
        payload = json.loads(data)
        email = payload.pop("email", None)
        resume_url = None

        if resume and resume.filename:
            if resume.content_type not in ALLOWED_TYPES:
                return {"status": "error", "message": "Only PDF or Word files are accepted."}
            file_bytes = await resume.read()
            if len(file_bytes) > 1 * 1024 * 1024:
                return {"status": "error", "message": "Resume too large, max 1MB."}
            filename = f"{uuid.uuid4()}_{resume.filename}"
            supabase.storage.from_(XLSX_BUCKET).upload(
                filename,
                file_bytes,
                {"content-type": resume.content_type}
            )
            resume_url = f"{os.getenv('SUPABASE_URL')}/storage/v1/object/public/resumes/{filename}"
            payload["resume_url"] = resume_url

        collection.insert_one(payload)

        if email:
            db["emails"].insert_one({
                "email": email,
                "submitted_at": payload.get("submitted_at")
            })

        send_notification(payload, resume_url, form_type="ai")
        return {"status": "success"}
    except Exception as e:
        print(e)
        return {"status": "error", "message": str(e)}


@app.post("/submit-dbms")
async def submit_dbms(data: str = Form(...), resume: UploadFile = File(None)):
    try:
        payload = json.loads(data)
        email = payload.pop("email", None)
        student_id = payload.pop("student_id", None)
        resume_url = None

        if resume and resume.filename:
            if resume.content_type not in ALLOWED_TYPES:
                return {"status": "error", "message": "Only PDF or Word files are accepted."}
            file_bytes = await resume.read()
            if len(file_bytes) > 1 * 1024 * 1024:
                return {"status": "error", "message": "Resume too large, max 1MB."}
            filename = f"dbms-resumes/{uuid.uuid4()}_{resume.filename}"
            supabase.storage.from_(XLSX_BUCKET).upload(
                filename,
                file_bytes,
                {"content-type": resume.content_type}
            )
            resume_url = f"{os.getenv('SUPABASE_URL')}/storage/v1/object/public/resumes/{filename}"
            payload["resume_url"] = resume_url

        dbms_collection.insert_one(payload)

        if email:
            dbms_db["emails"].insert_one({
                "email": email,
                "submitted_at": payload.get("submitted_at")
            })

        if student_id:
            dbms_db["student_ids"].insert_one({
                "student_id": str(student_id).strip(),
                "submitted_at": payload.get("submitted_at")
            })

        send_notification(payload, resume_url, form_type="dbms")
        return {"status": "success"}
    except Exception as e:
        print(e)
        return {"status": "error", "message": str(e)}
