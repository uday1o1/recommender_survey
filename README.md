# AI/ML Tech Skills Survey

A full-stack survey application for collecting student skill profiles and job preferences to build a recommender systems research dataset.

---

## Overview

This project collects structured data from students and professionals in AI/ML to power a career opportunity recommender system. Responses form a *person × skill × opportunity* tripartite graph enabling novel recommender systems research.

The survey covers:
- Academic profile and background
- Self-rated AI skill map across 8 categories
- Job role and company preferences
- Past experience and projects
- Career goals and context signals
- Optional resume upload

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
├── main.py           # FastAPI backend
├── requirements.txt  # Python dependencies
├── Procfile          # Render deployment config
├── index.html        # Survey frontend
└── .env              # Environment variables (not committed)
```

---

## Environment Variables

Create a `.env` file in the root with the following:

```
MONGO_URI=your_mongodb_connection_string
SUPABASE_URL=your_supabase_project_url
SUPABASE_KEY=your_supabase_secret_key
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

Then open `index.html` in your browser. The form will submit to the live Render backend by default. To test against local backend, change the fetch URL in `index.html` to `http://localhost:8000/submit`.

---

## Data Storage

- **Survey responses** are stored in MongoDB Atlas under `skills_survey.responses`
- **Emails** (optional, for research updates) are stored separately in `skills_survey.emails` with no link to survey responses
- **Resumes** (optional) are uploaded to Supabase Storage and only the file URL is saved in MongoDB

---

## Deployment

**Backend (Render):**
- Connects to GitHub repo and auto-deploys on push
- Set environment variables in Render dashboard under Environment tab

**Frontend (Netlify):**
- Connected to GitHub repo, auto-deploys on push to main
- `index.html` at repo root serves as the entry point

---

## Research Context

This dataset is being built as part of a Recommender Systems research project. The collected data enables multiple RS techniques including collaborative filtering, content-based filtering, graph neural networks, LLM-based ranking, context-aware models, and hybrid approaches.
