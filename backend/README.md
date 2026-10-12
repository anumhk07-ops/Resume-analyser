# Backend

FastAPI backend for the AI Resume Tailor app.

## Setup

```powershell
cd resume-tailor-app\backend
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
```

## Run locally

```powershell
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Visit `http://localhost:8000/docs` for interactive API documentation.

## API Endpoints

### 1. POST `/upload-resume`
Upload and parse resume file.

**Request:**
- Form data with file upload (PDF, DOCX, or TXT)

**Response:**
```json
{
  "success": true,
  "data": {
    "sections": {
      "summary": "...",
      "skills": "...",
      "experience": "...",
      "education": "...",
      "certifications": "...",
      "projects": "..."
    },
    "skills": ["Python", "JavaScript", ...],
    "keywords": [...]
  }
}
```

---

### 2. POST `/analyze-job-description`
Analyze job description to extract required skills and keywords.

**Request:**
```json
{
  "job_description": "..."
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "required_skills": [...],
    "tools": [...],
    "responsibilities": [...],
    "soft_skills": [...],
    "top_keywords": [...]
  }
}
```

---

### 3. POST `/match-score`
Calculate ATS match score between resume and job description.

**Request:**
```json
{
  "resume_text": "...",
  "job_description": "...",
  "skills": ["Python", "JavaScript", ...]
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "match_score": 75,
    "matched_skills": [...],
    "missing_skills": [...],
    "missing_keywords": [...],
    "resume_tokens": [...],
    "job_description_tokens": [...]
  }
}
```

---

### 4. POST `/generate-resume`
Generate ATS-optimized resume with enhanced keywords.

**Request:**
```json
{
  "analysis": {
    "sections": {...},
    "skills": [...]
  },
  "match": {
    "matched_skills": [...]
  },
  "skills": ["Python", ...],
  "job_description": "..."
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "updated_resume": {
      "sections": {...}
    },
    "downloads": {
      "docx": "/generated/updated_resume.docx",
      "pdf": "/generated/updated_resume.pdf"
    }
  }
}
```

---

### 5. GET `/download-resume`
Download the generated resume file.

**Query Parameters:**
- `format` (required): `docx` or `pdf`
- `filename` (optional): Custom download filename

**Example:**
```
GET /download-resume?format=docx
GET /download-resume?format=pdf&filename=my-resume.pdf
```

---

## CORS Configuration

The backend is configured to accept requests from:
- `http://localhost:5173` (React dev server)
- `http://localhost:3000` (Alternative React port)

To add more origins, update the `allow_origins` list in `main.py`.

## File Storage

Generated resumes are stored in the `generated/` directory and served as static files at `/generated/`.

