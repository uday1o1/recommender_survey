# AI/ML & DBMS Skills Survey

A full-stack survey application for collecting student skill profiles and job preferences to build recommender systems research datasets. Currently supports two surveys — one for AI/ML careers and one for DBMS & Data Engineering careers.

---

## Overview

This project collects structured data from students and professionals to power career opportunity recommender systems. Responses form a *person × skill × opportunity* tripartite graph enabling novel recommender systems research.

**AI/ML Survey covers:**
- Academic profile and background
- Self-rated AI skill map across 8 categories
- Job role and company preferences
- Past experience and projects
- Career goals and context signals
- Optional resume upload

**DBMS Survey covers:**
- Academic profile and background
- Self-rated DBMS & Data Engineering skill map
- Job role and company preferences
- Past experience and certifications
- Career goals and context signals
- Optional resume upload
- Optional SJSU Student ID for bonus points tracking

---

## Tech Stack

| Layer | Technology | Tier |
|---|---|---|
| Frontend | HTML/CSS/JS | Hosted on Netlify (free) |
| Backend | Python FastAPI | Deployed on Render (free) |
| Database | MongoDB Atlas | Free tier |
| File Storage | Supabase Storage | Free tier |

---

## Project Structure

```
survey-backend/
├── main.py           # FastAPI backend (handles both surveys)
├── requirements.txt  # Python dependencies
├── Procfile          # Render deployment config
├── index.html        # AI/ML survey frontend
├── dbms.html         # DBMS survey frontend
└── .env              # Environment variables (not committed)
```

---

## Environment Variables

Create a `.env` file in the root with the following:

```
MONGO_URI=your_mongodb_connection_string
SUPABASE_URL=your_supabase_project_url
SUPABASE_KEY=your_supabase_secret_key
GMAIL_USER=your_gmail_address
GMAIL_APP_PASSWORD=your_gmail_app_password
PROF_EMAIL=professor_email_address
```

On Render, add these same variables under the Environment tab in your service settings.

---

## Running Locally

```bash
# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # Mac/Linux
.venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Start the backend
uvicorn main:app --reload
```

Then open `index.html` or `dbms.html` in your browser.

---

## API Endpoints

- `GET /health` — Health check, used to keep server warm
- `POST /submit` — AI/ML survey submission
- `POST /submit-dbms` — DBMS survey submission with student ID matching

---

## Data Storage

**AI/ML Survey (`skills_survey` database):**
- `responses` — survey answers
- `emails` — optional emails stored separately
- Resumes stored in Supabase under `resumes/` folder

**DBMS Survey (`dbms_survey` database):**
- `responses` — survey answers
- `emails` — optional emails stored separately
- `student_ids` — SJSU student IDs stored separately for bonus points
- Resumes stored in Supabase under `resumes/dbms-resumes/` folder
- Class roster xlsx stored in Supabase under `resumes/dbms_class/` and auto-updated when a student ID is matched

---

## Deployment

**Backend (Render):**
- Connects to GitHub repo and auto-deploys on push
- Set environment variables in Render dashboard under Environment tab
- UptimeRobot pings `/health` every 10 minutes to keep server warm

**Frontend (Netlify):**
- Connected to GitHub repo, auto-deploys on push to main

---

## Research Context

This dataset is being built as part of a Recommender Systems research project. The collected data enables multiple RS techniques including collaborative filtering, content-based filtering, graph neural networks, LLM-based ranking, context-aware models, and hybrid approaches.
