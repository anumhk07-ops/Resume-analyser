from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Optional
from app.utils.parser import parse_resume_text, analyze_job_description, compare_skills, normalize_skills, generate_resume_improvements, generate_improved_resume_text
from app.utils.output import generate_docx, generate_pdf, generate_skills_files, generate_docx_from_improved_resume
import os
from pathlib import Path

app = FastAPI(
    title="AI Resume Tailor Backend",
    description="Backend API for resume parsing, JD analysis, ATS matching, and downloadable resume generation.",
    version="0.1.0",
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5174", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files for generated resumes
generated_dir = os.path.join(os.path.dirname(__file__), "generated")
os.makedirs(generated_dir, exist_ok=True)
app.mount("/generated", StaticFiles(directory=generated_dir), name="generated")

# Request models
class JobAnalysisRequest(BaseModel):
    resume_text: str
    job_description: str
    skills: List[str]

class GenerateResumeRequest(BaseModel):
    analysis: dict
    match: dict
    skills: List[str]
    job_description: str

# Health check
@app.get("/")
async def root():
    return {
        "status": "running",
        "message": "AI Resume Tailor backend is operational",
        "version": "0.1.0"
    }

# Endpoint 1: Upload and parse resume
@app.post("/upload-resume")
async def upload_resume(file: UploadFile = File(...)):
    """
    Upload a resume file (PDF or DOCX) and return extracted text as JSON.
    """
    try:
        content = await file.read()
        filename = (file.filename or "").lower()

        if not content:
            raise HTTPException(status_code=400, detail="Uploaded file is empty")

        if filename.endswith('.pdf'):
            from pypdf import PdfReader
            from io import BytesIO
            pdf = PdfReader(BytesIO(content))
            text_parts = []
            for page in pdf.pages:
                page_text = page.extract_text() or ""
                text_parts.append(page_text)
            text = "\n".join(text_parts).strip()
        elif filename.endswith('.docx'):
            from docx import Document
            from io import BytesIO
            doc = Document(BytesIO(content))
            text = "\n".join([para.text for para in doc.paragraphs]).strip()
        else:
            raise HTTPException(status_code=400, detail="Invalid file type. Only PDF and DOCX are supported.")

        if not text:
            raise HTTPException(status_code=400, detail="Unable to extract any text from the uploaded file")

        parsed = parse_resume_text(text)
        return {
            "success": True,
            "extracted_text": text,
            "data": parsed
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error parsing resume: {str(e)}")

# Endpoint 2: Analyze job description
@app.post("/analyze-job-description")
async def analyze_job(job_description: str = Form(...)):
    """
    Analyze job description to extract required skills, tools, and keywords.
    """
    try:
        analysis = analyze_job_description(job_description)
        return {
            "success": True,
            "data": analysis
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error analyzing job description: {str(e)}")

# Endpoint 2B: Process and normalize skills
@app.post("/process-skills")
async def process_skills(skills: str = Form(...)):
    """
    Process and normalize user-entered skills.
    
    Input: Raw skill string (comma, semicolon, or newline separated)
    Output: Clean normalized list with:
    - Duplicates removed (case-insensitive)
    - Whitespace trimmed
    - Lowercase applied
    
    Example input: "Python, SQL, excel , Streamlit, sql"
    Example output: ["Python", "SQL", "excel", "Streamlit"]
    """
    try:
        normalized = normalize_skills(skills)
        return {
            "success": True,
            "data": {
                "original_count": len(skills.split(',') if ',' in skills else skills.split('\n')),
                "normalized_count": len(normalized),
                "normalized_skills": normalized
            }
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error processing skills: {str(e)}")

# Endpoint 3: Match resume skills with job requirements
@app.post("/match-score")
async def match_skills(data: JobAnalysisRequest):
    """
    Compare resume skills with job description requirements.
    Returns match score, matched skills, and missing keywords.
    """
    try:
        result = compare_skills(data.resume_text, data.job_description, data.skills)
        return {
            "success": True,
            "data": result
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error matching skills: {str(e)}")

# Endpoint 3.5: Get resume improvement suggestions
@app.post("/resume-improvements")
async def get_improvements(data: JobAnalysisRequest):
    """
    Analyze resume and provide actionable improvement suggestions.
    
    Returns:
    - Summary improvements
    - Skills to add (only from user's skillset)
    - Bullet point improvements
    - Missing keywords
    - Weak sections
    - Priority action items
    """
    try:
        # First get the match data
        match_data = compare_skills(data.resume_text, data.job_description, data.skills)
        
        # Parse resume to get sections
        resume_data = parse_resume_text(data.resume_text)
        
        # Generate improvements
        improvements = generate_resume_improvements(resume_data, match_data, data.job_description)
        
        return {
            "success": True,
            "data": improvements
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error generating improvements: {str(e)}")

# Endpoint 3.7: Generate improved resume text
@app.post("/generate-resume-text")
async def generate_resume_text(data: JobAnalysisRequest):
    """
    Generate improved resume text based on job description and user skills.
    
    Improvements:
    - Enhanced professional summary
    - Stronger bullet points with action verbs
    - Suggested skills integrated
    - ATS-friendly formatting
    
    Returns improved resume text (not documents).
    """
    try:
        # Parse resume to get sections
        resume_data = parse_resume_text(data.resume_text)
        
        # Get match data for skill suggestions
        match_data = compare_skills(data.resume_text, data.job_description, data.skills)
        
        # Generate improved resume text
        improved = generate_improved_resume_text(resume_data, match_data, data.skills)
        
        return {
            "success": True,
            "data": improved
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error generating resume text: {str(e)}")

# Endpoint 3.8: Download improved resume as DOCX
@app.post("/download-improved-resume-docx")
async def download_improved_resume_docx(resume_text: str = Form(...)):
    """
    Convert improved resume text to downloadable DOCX file.
    
    Input: Improved resume text (from /generate-resume-text endpoint)
    Output: Download link to DOCX file in /generated folder
    
    Uses python-docx with:
    - ## Sections → Heading 2
    - • Bullets → Bullet points
    - Clean formatting
    """
    try:
        if not resume_text or resume_text.strip() == "":
            raise HTTPException(status_code=400, detail="Resume text cannot be empty")
        
        # Generate DOCX
        file_path = generate_docx_from_improved_resume(resume_text, "improved_resume.docx")
        
        return {
            "success": True,
            "data": {
                "file": f"/generated/{os.path.basename(file_path)}",
                "format": "docx",
                "download_url": f"/download-resume?filename={os.path.basename(file_path)}"
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error generating DOCX: {str(e)}")

# Endpoint 4: Generate ATS-optimized resume
@app.post("/generate-resume")
async def generate_resume(data: GenerateResumeRequest):
    """
    Generate an ATS-optimized resume by enhancing skills and keywords
    while preserving original structure and content.
    """
    try:
        # Use the parsed analysis as base
        base_resume = data.analysis
        
        # Get match data for enhancements
        match_data = data.match
        user_skills = data.skills
        
        # Enhance skills by adding suggested keywords (only from user's skillset)
        enhanced_skills = list(set(
            base_resume.get("skills", []) + 
            match_data.get("suggested_skills", [])
        ))
        
        # Skills to highlight: only the suggested ones
        added_skills = match_data.get("suggested_skills", [])
        
        # Keep all original sections
        updated_resume = {
            "sections": {
                "summary": base_resume.get("sections", {}).get("summary", ""),
                "skills": ", ".join(enhanced_skills),
                "experience": base_resume.get("sections", {}).get("experience", ""),
                "education": base_resume.get("sections", {}).get("education", ""),
                "certifications": base_resume.get("sections", {}).get("certifications", ""),
                "projects": base_resume.get("sections", {}).get("projects", ""),
            },
            "skills": enhanced_skills
        }
        
        # Generate DOCX and PDF
        docx_path = generate_docx(updated_resume, added_skills)
        pdf_path = generate_pdf(updated_resume, added_skills)
        
        # Get resume skills and job description keywords for text file generation
        resume_skills = base_resume.get("skills", [])
        jd_keywords = match_data.get("jd_keywords", [])
        
        # Generate skills text files
        resume_skills_path, jd_skills_path = generate_skills_files(resume_skills, jd_keywords)
        
        return {
            "success": True,
            "data": {
                "updated_resume": updated_resume,
                "downloads": {
                    "docx": f"/generated/{os.path.basename(docx_path)}",
                    "pdf": f"/generated/{os.path.basename(pdf_path)}",
                    "resume_skills": f"/generated/{os.path.basename(resume_skills_path)}",
                    "job_description_skills": f"/generated/{os.path.basename(jd_skills_path)}"
                }
            }
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error generating resume: {str(e)}")

# Endpoint 5: Download resume file
@app.get("/download-resume")
async def download_resume(format: str = "docx", filename: Optional[str] = None):
    """
    Download the generated resume in specified format (docx or pdf).
    """
    try:
        generated_dir_path = Path(generated_dir)
        
        if filename:
            file_path = generated_dir_path / filename
            if file_path.suffix not in {".docx", ".pdf"}:
                raise HTTPException(status_code=400, detail="Filename must be a .docx or .pdf file")
        else:
            if format == "docx":
                file_path = generated_dir_path / "updated_resume.docx"
            elif format == "pdf":
                file_path = generated_dir_path / "updated_resume.pdf"
            else:
                raise HTTPException(status_code=400, detail="Format must be 'docx' or 'pdf'")
        
        file_path = file_path.resolve()
        if generated_dir_path.resolve() not in file_path.parents and file_path != generated_dir_path.resolve():
            raise HTTPException(status_code=400, detail="Invalid filename")

        if not file_path.exists():
            raise HTTPException(status_code=404, detail=f"Resume file not found: {file_path.name}")
        
        download_name = filename or f"resume.{file_path.suffix.lstrip('.') }"
        return FileResponse(
            path=str(file_path),
            filename=download_name,
            media_type="application/octet-stream"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error downloading resume: {str(e)}")

# Endpoint 5B: Download skills text files
@app.get("/download-skills")
async def download_skills(type: str = "resume"):
    """
    Download skills text files.
    type: 'resume' for resume skills, 'job' for job description skills
    """
    try:
        generated_dir_path = Path(generated_dir)
        
        if type == "resume":
            file_path = generated_dir_path / "resume_skills.txt"
            download_name = "resume_skills.txt"
        elif type == "job":
            file_path = generated_dir_path / "job_description_skills.txt"
            download_name = "job_description_skills.txt"
        else:
            raise HTTPException(status_code=400, detail="Type must be 'resume' or 'job'")
        
        if not file_path.exists():
            raise HTTPException(status_code=404, detail=f"Skills file not found: {type}")
        
        return FileResponse(
            path=str(file_path),
            filename=download_name,
            media_type="text/plain"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error downloading skills file: {str(e)}")

# API Documentation endpoint
@app.get("/docs/endpoints")
async def list_endpoints():
    """List all available API endpoints."""
    return {
        "endpoints": [
            {
                "method": "POST",
                "path": "/upload-resume",
                "description": "Upload and parse resume file (PDF or DOCX)"
            },
            {
                "method": "POST",
                "path": "/analyze-job-description",
                "description": "Analyze job description for skills and keywords"
            },
            {
                "method": "POST",
                "path": "/process-skills",
                "description": "Normalize and deduplicate user-entered skills"
            },
            {
                "method": "POST",
                "path": "/match-score",
                "description": "Calculate ATS match score between resume and job"
            },
            {
                "method": "POST",
                "path": "/resume-improvements",
                "description": "Get actionable resume improvement suggestions"
            },
            {
                "method": "POST",
                "path": "/generate-resume-text",
                "description": "Generate improved resume text with enhanced summary and bullets"
            },
            {
                "method": "POST",
                "path": "/download-improved-resume-docx",
                "description": "Convert improved resume text to downloadable DOCX file"
            },
            {
                "method": "POST",
                "path": "/generate-resume",
                "description": "Generate ATS-optimized resume with enhanced keywords"
            },
            {
                "method": "GET",
                "path": "/download-resume",
                "description": "Download generated resume (format: docx or pdf)"
            }
        ]
    }

# Additional endpoint: Get markdown template
@app.get("/resume-template")
async def get_resume_template():
    """Get markdown resume template for editing."""
    try:
        template_path = Path(__file__).parent / "templates" / "resume_template.md"
        if not template_path.exists():
            raise HTTPException(status_code=404, detail="Template not found")
        
        with open(template_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        return {
            "success": True,
            "template": content
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving template: {str(e)}")

# Additional endpoint: Convert markdown to DOCX/PDF
@app.post("/convert-markdown")
async def convert_markdown(
    markdown_content: str = Form(...), 
    format: str = Form("docx"),
    enhanced_skills: Optional[str] = Form(None)
):
    """Convert markdown content directly to DOCX or PDF."""
    try:
        # Parse enhanced skills if provided
        skills_list = []
        if enhanced_skills:
            skills_list = [skill.strip() for skill in enhanced_skills.split(',') if skill.strip()]
        
        resume_data = {
            "markdown_content": markdown_content,
            "sections": {},
            "skills": skills_list
        }
        
        if format == "docx":
            file_path = generate_docx(resume_data, skills_list)
        elif format == "pdf":
            file_path = generate_pdf(resume_data, skills_list)
        else:
            raise HTTPException(status_code=400, detail="Format must be 'docx' or 'pdf'")
        
        return {
            "success": True,
            "data": {
                "file": f"/generated/{os.path.basename(file_path)}",
                "format": format
            }
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error converting markdown: {str(e)}")
