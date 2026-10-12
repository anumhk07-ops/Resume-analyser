# ✨ Markdown Resume Feature - Complete Guide

## What's New

You can now:
1. **Create resumes in Markdown format** - Easy to edit, readable text format
2. **Maintain professional formatting** - Markdown formatting is preserved in PDF/DOCX
3. **Download as PDF or DOCX** - With original format intact
4. **Keep the same layout** - Headers, bullets, bold text all rendered correctly

---

## Quick Start

### 1. Download Markdown Template

```bash
curl http://localhost:8000/resume-template
```

Or visit: `http://localhost:8000/resume-template`

### 2. Edit the Template

**Example Resume Template:**
```markdown
# John Doe
**Email:** john@example.com | **Phone:** +1 (555) 123-4567

---

## Professional Summary
Brief overview of your professional background and career objectives.

---

## Skills
- **Languages:** Python, JavaScript, Java
- **Frameworks:** React, Django, FastAPI
- **Databases:** PostgreSQL, MongoDB

---

## Experience

### Senior Developer | Tech Company
**Duration:** 2022 - Present
- Led development of scalable microservices
- Improved system performance by 40%

### Junior Developer | StartUp
**Duration:** 2020 - 2021
- Built web applications using React
- Implemented REST APIs

---

## Education
**B.S. Computer Science** | University Name | 2020

---

## Certifications
- AWS Certified Cloud Practitioner (2023)
- MongoDB Certified Developer (2022)
```

### 3. Features You Can Use

#### Headings
```markdown
# Main Title (Level 1)
## Section Header (Level 2)
### Subsection (Level 3)
```

#### Bold Text
```markdown
**This will be bold**
```

#### Bullet Points
```markdown
- Item 1
- Item 2
- Item 3
```

#### Horizontal Separator
```markdown
---
```

#### Contact/Meta Information
```markdown
**Email:** your@email.com | **Phone:** +1 (XXX) XXX-XXXX | **LinkedIn:** linkedin.com/profile
```

### 4. Convert to PDF or DOCX

**Option A: Using the Web Interface**
1. Open http://localhost:8000 in browser
2. Click "Markdown Editor" tab
3. Paste or edit your markdown
4. Click "Convert to PDF" or "Convert to DOCX"
5. Download automatically starts

**Option B: Using API**

```bash
# Create a markdown file
cat > resume.md << 'EOF'
# Your Name
**Email:** email@example.com

## Skills
- Python
- JavaScript

## Experience
- Worked at Company X
EOF

# Convert to DOCX
curl -X POST http://localhost:8000/convert-markdown \
  -F "markdown_content=@resume.md" \
  -F "format=docx" \
  -o resume.docx

# Convert to PDF
curl -X POST http://localhost:8000/convert-markdown \
  -F "markdown_content=@resume.md" \
  -F "format=pdf" \
  -o resume.pdf
```

---

## How Formatting is Preserved

✅ **Headers** → Appropriate font sizes and bold
```markdown
# Title (largest)
## Subheading (medium)
### Sub-subheading (smaller)
```

✅ **Bold Text** → Rendered as bold
```markdown
**Bold text** remains bold in PDF/DOCX
```

✅ **Lists** → Formatted as bullet points
```markdown
- Item 1
- Item 2
```

✅ **Separators** → Horizontal lines
```markdown
---
```

✅ **Line Breaks** → Preserved and formatted
```markdown
Paragraph 1

Paragraph 2 (with space between)
```

---

## Full Workflow Example

### Step 1: Get Template
```bash
curl http://localhost:8000/resume-template > my-resume.md
```

### Step 2: Edit in Your Favorite Editor
- VS Code (with markdown preview)
- Typora
- Notion
- Any text editor

### Step 3: Add Job-Specific Content

Use the "Upload & Analyze" tab to:
1. Upload your resume
2. Paste job description
3. Get AI-matched skills
4. Copy matched skills to markdown

### Step 4: Convert
```bash
curl -X POST http://localhost:8000/convert-markdown \
  -F "markdown_content=@my-resume.md" \
  -F "format=pdf" \
  -o final-resume.pdf
```

### Step 5: Download and Submit
- DOCX for editing in Word
- PDF for submission to ATS systems

---

## API Endpoints

### GET `/resume-template`
Download markdown template

**Response:**
```json
{
  "success": true,
  "template": "# Your Name\n**Email:** ..."
}
```

### POST `/convert-markdown`
Convert markdown to PDF or DOCX

**Parameters:**
- `markdown_content` (string): Your markdown content
- `format` (string): "pdf" or "docx"

**Response:**
```json
{
  "success": true,
  "data": {
    "file": "/generated/updated_resume.pdf",
    "format": "pdf"
  }
}
```

### GET `/download-resume`
Download generated file

**Parameters:**
- `format` (required): "pdf" or "docx"
- `filename` (optional): Custom download name

---

## Best Practices

✨ **Keep It Simple**
- Use basic markdown syntax
- Avoid complex nested structures
- Stick to text-based formatting

✨ **ATS-Friendly**
- No images or complex graphics
- Use simple formatting
- Plain text is best for parsing

✨ **Professional Format**
- Use consistent spacing
- Keep sections clearly separated
- Use bullets for lists

✨ **Content Tips**
- Include relevant keywords from job description
- Use the AI analyzer to find missing skills
- Quantify achievements with numbers

---

## Example: Before & After

### Markdown Input
```markdown
# Alice Johnson
**Email:** alice@example.com | **Phone:** (555) 123-4567

---

## Professional Summary
Full-stack developer with 5+ years experience building scalable web applications.

---

## Skills
- **Backend:** Python, FastAPI, Django, Node.js
- **Frontend:** React, Vue.js, JavaScript, HTML/CSS
- **Databases:** PostgreSQL, MongoDB, Redis

---

## Experience

### Senior Full-Stack Developer | TechCorp Inc.
**Duration:** Jan 2021 - Present
- Led team of 5 developers building microservices
- Improved API performance by 60% through optimization
- Architected real-time collaboration features

### Junior Developer | StartupXYZ
**Duration:** June 2019 - Dec 2020
- Developed React components for customer dashboard
- Built REST APIs using FastAPI
- Collaborated with designers on UI/UX

---

## Education
**B.S. Computer Science** | State University | 2019
```

### DOCX Output
- Professional formatting with proper headers
- Bold text for emphasis
- Bullet lists formatted correctly
- Proper spacing between sections
- Ready for Word editing

### PDF Output
- Professional appearance
- Print-ready
- ATS-compatible
- No formatting issues

---

## Troubleshooting

**Issue:** Formatting looks different than markdown
- **Solution:** Complex markdown may not render perfectly. Stick to basic syntax.

**Issue:** Special characters not showing
- **Solution:** Use UTF-8 encoding and avoid special symbols

**Issue:** Text is cut off in PDF
- **Solution:** PDF has limited width. Keep lines reasonably short.

**Issue:** Can't download file
- **Solution:** Check backend is running: `uvicorn main:app --reload`

---

## Next Steps

1. ✅ Download template from backend
2. ✅ Edit in your markdown editor
3. ✅ Use AI Resume Tailor to enhance skills
4. ✅ Convert to PDF/DOCX
5. ✅ Download and submit!

Enjoy creating professional, ATS-friendly resumes! 🎉
