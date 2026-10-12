# AI Resume Tailor

A full-stack prototype for an ATS-focused resume tailoring app.

## Structure

- `backend/` – FastAPI backend, resume parsing, and document generation helpers
- `frontend/` – React + Tailwind UI for uploads, analysis, and score display

## Quick start

1. Backend
   - `cd resume-tailor-app/backend`
   - `python -m venv .venv`
   - `.\.venv\Scripts\activate`
   - `pip install -r requirements.txt`
   - `uvicorn main:app --reload --host 0.0.0.0 --port 8000`

2. Frontend
   - `cd resume-tailor-app/frontend`
   - `npm install`
   - `npm run dev`

## Notes

- The backend uses FastAPI and includes placeholder parsing and document generation services.
- The frontend is bootstrapped with Vite, React, and Tailwind CSS.
- This scaffolding is designed to be extended with AI resume tailoring logic.
