# Markdown Resume Guide

## Overview

The AI Resume Tailor now supports editing resumes in **Markdown format** with automatic formatting preservation when converting to PDF and DOCX.

## How It Works

### 1. Download the Template

Get the markdown resume template:
```
GET http://localhost:8000/resume-template
```

This returns a markdown-formatted resume with standard sections.

### 2. Edit the Markdown

Open the template in any text editor:
- VS Code
- Markdown editors like Typora, iA Writer
- Google Docs (with markdown support)
- Even plain Notepad

### 3. Convert to PDF/DOCX

Use the conversion endpoint:

**API Endpoint:**
```
POST http://localhost:8000/convert-markdown
```

**Request (Form Data):**
- `markdown_content` - Your edited markdown text
- `format` - "docx" or "pdf"

**cURL Example:**
```bash
curl -X POST http://localhost:8000/convert-markdown \
  -F "markdown_content=@your_resume.md" \
  -F "format=docx"
```

**Response:**
```json
{
  "success": true,
  "data": {
    "file": "/generated/updated_resume.docx",
    "format": "docx"
  }
}
```

### 4. Download

Download the generated file:
```
GET http://localhost:8000/download-resume?format=docx
GET http://localhost:8000/download-resume?format=pdf
```

## Markdown Formatting

### Headers
```markdown
# Main Title (Your Name)
## Section Header (e.g., Skills, Experience)
### Subsection (e.g., Company Name)
```

### Bold Text
```markdown
**Bold Text** → renders as bold
```

### Bullet Points
```markdown
- Bullet point 1
- Bullet point 2
- Bullet point 3
```

### Separators
```markdown
---
```

### Example Structure
```markdown
# John Doe
**Email:** john@example.com | **Phone:** +1 (555) 123-4567

---

## Professional Summary
Brief summary paragraph...

---

## Skills
- **Languages:** Python, JavaScript
- **Tools:** Git, Docker, AWS

---

## Experience

### Senior Developer | Tech Company
**Duration:** 2021 - Present
- Achievement 1
- Achievement 2

---

## Education
**B.S. Computer Science** | University Name | 2020
```

## Formatting is Preserved

When converting to PDF/DOCX:
- ✅ Headers are formatted with appropriate sizes
- ✅ Bold text stays bold
- ✅ Bullet points are formatted as lists
- ✅ Separators appear as horizontal lines
- ✅ Spacing and layout are maintained
- ✅ Line wrapping is automatic

## Features

✨ **Format Preservation** - Markdown formatting is accurately converted to both PDF and DOCX

✨ **ATS-Friendly** - Generated documents follow ATS best practices

✨ **Easy Editing** - Edit in any markdown editor, then convert instantly

✨ **Multiple Formats** - Download as DOCX, PDF, or Markdown

## Example Workflow

1. **Get Template**
   ```
   curl http://localhost:8000/resume-template
   ```

2. **Save as `my-resume.md`**
   ```markdown
   # Jane Smith
   **Email:** jane@example.com
   
   ## Skills
   - Python, JavaScript, SQL
   - React, Django, FastAPI
   ```

3. **Convert to DOCX**
   ```
   POST /convert-markdown
   Form Data:
   - markdown_content: [file content]
   - format: docx
   ```

4. **Download**
   ```
   GET /download-resume?format=docx
   ```

## Tips

- **Keep it Simple** - Use basic markdown; complex markdown may not render perfectly
- **Test Locally** - Use a markdown preview to see how it looks before converting
- **Update Skills** - Use the AI Resume Tailor to analyze job descriptions and suggest skills to add
- **Professional Format** - Keep formatting clean and consistent throughout
- **ATS Optimization** - Avoid images and complex tables; stick to text and bullet points

## Integration with AI Resume Tailor

You can combine markdown editing with the ATS matching:

1. Start with markdown template
2. Edit and customize
3. Use `/analyze-job-description` to find relevant keywords
4. Manually update markdown with matched keywords
5. Convert to PDF/DOCX with preserved formatting

This gives you full control while maintaining professional formatting!
