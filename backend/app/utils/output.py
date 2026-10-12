from pathlib import Path
from docx import Document
from docx.shared import Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_COLOR_INDEX
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
import textwrap
import re
from app.utils.parser import STOPWORDS

OUTPUT_DIR = Path(__file__).resolve().parent.parent.parent / "generated"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def generate_docx_from_improved_resume(improved_resume_text: str, filename: str = "improved_resume.docx") -> str:
    """
    Generate DOCX from improved resume text.
    
    Input: Improved resume text with ## section headers and • bullet points
    Output: Formatted DOCX file saved to /generated folder
    
    Formatting:
    - ## Sections → Heading 2
    - • Bullets → Bullet points
    - Regular text → Paragraph
    """
    document = Document()
    
    lines = improved_resume_text.split('\n')
    current_bullets = []
    
    for line in lines:
        stripped = line.strip()
        
        # Skip empty lines
        if not stripped:
            # Flush any pending bullets
            if current_bullets:
                for bullet in current_bullets:
                    document.add_paragraph(bullet, style='List Bullet')
                current_bullets = []
            continue
        
        # Check for section heading
        if stripped.startswith('## '):
            # Flush any pending bullets
            if current_bullets:
                for bullet in current_bullets:
                    document.add_paragraph(bullet, style='List Bullet')
                current_bullets = []
            
            # Add heading
            heading_text = stripped[3:].strip()
            document.add_heading(heading_text, level=2)
        
        # Check for bullet points
        elif stripped.startswith('• '):
            current_bullets.append(stripped[2:].strip())
        
        # Regular text
        else:
            # Flush any pending bullets first
            if current_bullets:
                for bullet in current_bullets:
                    document.add_paragraph(bullet, style='List Bullet')
                current_bullets = []
            
            # Add as paragraph
            if stripped:
                document.add_paragraph(stripped)
    
    # Flush any remaining bullets
    if current_bullets:
        for bullet in current_bullets:
            document.add_paragraph(bullet, style='List Bullet')
    
    # Save file
    file_path = OUTPUT_DIR / filename
    document.save(str(file_path))
    
    return str(file_path)


def parse_markdown_content(content: str):
    """Parse markdown content into structured sections."""
    lines = content.split('\n')
    sections = []
    current_section = {'type': 'text', 'content': []}
    
    for line in lines:
        if line.startswith('# ') and not line.startswith('# '):
            if current_section['content']:
                sections.append(current_section)
            current_section = {'type': 'heading1', 'content': line[2:].strip()}
            sections.append(current_section)
            current_section = {'type': 'text', 'content': []}
        elif line.startswith('## '):
            if current_section['content']:
                sections.append(current_section)
            current_section = {'type': 'heading2', 'content': line[3:].strip()}
            sections.append(current_section)
            current_section = {'type': 'text', 'content': []}
        elif line.startswith('### '):
            if current_section['content']:
                sections.append(current_section)
            current_section = {'type': 'heading3', 'content': line[4:].strip()}
            sections.append(current_section)
            current_section = {'type': 'text', 'content': []}
        elif line.startswith('- '):
            current_section['type'] = 'bullet'
            current_section['content'].append(line[2:].strip())
        elif line.strip() == '---':
            if current_section['content']:
                sections.append(current_section)
            sections.append({'type': 'separator', 'content': ''})
            current_section = {'type': 'text', 'content': []}
        elif '|' in line and len(line.split('|')) > 2:
            # This looks like a table row
            if current_section['content']:
                sections.append(current_section)
            current_section = {'type': 'table', 'content': [line.strip()]}
            sections.append(current_section)
            current_section = {'type': 'text', 'content': []}
        elif line.strip():
            if current_section['type'] == 'text':
                current_section['content'].append(line.strip())
            elif current_section['type'] == 'bullet':
                # Keep as bullet
                pass
    
    if current_section['content']:
        sections.append(current_section)
    
    return sections


def generate_docx(resume_data: dict, enhanced_skills: list = None) -> str:
    """Generate DOCX preserving markdown formatting with skill highlighting."""
    document = Document()
    
    # Extract markdown content if available
    if 'markdown_content' in resume_data:
        content = resume_data['markdown_content']
    else:
        # Build from sections
        content = build_markdown_from_sections(resume_data)
    
    sections = parse_markdown_content(content)
    
    for section in sections:
        if section['type'] == 'heading1':
            heading = document.add_heading(section['content'], level=1)
            heading.alignment = WD_ALIGN_PARAGRAPH.CENTER
        elif section['type'] == 'heading2':
            document.add_heading(section['content'], level=2)
        elif section['type'] == 'heading3':
            document.add_heading(section['content'], level=3)
        elif section['type'] == 'bullet':
            for bullet in section['content']:
                document.add_paragraph(bullet, style='List Bullet')
        elif section['type'] == 'separator':
            document.add_paragraph('_' * 80)
        elif section['type'] == 'table':
            # Handle table content
            add_table_to_docx(document, section['content'])
        elif section['type'] == 'text':
            for text in section['content']:
                if text:
                    # Handle bold text and skill highlighting
                    paragraph = document.add_paragraph()
                    add_formatted_text(paragraph, text, enhanced_skills or [])
    
    path = OUTPUT_DIR / 'updated_resume.docx'
    document.save(path)
    return str(path)


def add_table_to_docx(document, table_lines):
    """Add table content to DOCX document."""
    if not table_lines:
        return
    
    # Create table from pipe-separated content
    table = document.add_table(rows=1, cols=1)
    table.style = 'Table Grid'
    
    for line in table_lines:
        if '|' in line:
            cells = [cell.strip() for cell in line.split('|') if cell.strip()]
            if cells:
                # Add row to table
                row_cells = table.add_row().cells
                for i, cell_content in enumerate(cells):
                    if i < len(row_cells):
                        row_cells[i].text = cell_content
                    else:
                        # Extend table if needed
                        table.add_column()
                        row_cells = table.rows[-1].cells
                        row_cells[i].text = cell_content


def add_formatted_text(paragraph, text, enhanced_skills=None):
    """Add text with markdown formatting and skill highlighting to a paragraph."""
    if enhanced_skills is None:
        enhanced_skills = []
    
    # Filter out stopwords from skills to highlight
    enhanced_skills = [skill for skill in enhanced_skills if skill.lower() not in STOPWORDS]
    
    # Check if this looks like a table (contains pipes and multiple columns)
    if '|' in text and len(text.split('|')) > 2:
        # This might be a table row, handle it differently
        return
    
    # Split text by bold markers (**)
    parts = re.split(r'\*\*(.*?)\*\*', text)
    
    for i, part in enumerate(parts):
        if i % 2 == 0:
            # Regular text - check for enhanced skills
            if part:
                # Split by enhanced skills and highlight them
                remaining = part
                while remaining:
                    found_skill = False
                    for skill in enhanced_skills:
                        skill_lower = skill.lower()
                        remaining_lower = remaining.lower()
                        if skill_lower in remaining_lower:
                            # Find the exact case match
                            start_idx = remaining_lower.find(skill_lower)
                            before = remaining[:start_idx]
                            matched = remaining[start_idx:start_idx + len(skill)]
                            after = remaining[start_idx + len(skill):]
                            
                            # Add text before skill
                            if before:
                                paragraph.add_run(before)
                            
                            # Add highlighted skill
                            run = paragraph.add_run(matched)
                            run.font.highlight_color = WD_COLOR_INDEX.PINK
                            
                            # Continue with remaining text
                            remaining = after
                            found_skill = True
                            break
                    
                    if not found_skill:
                        # No more skills found, add remaining text
                        paragraph.add_run(remaining)
                        break
        else:
            # Bold text
            run = paragraph.add_run(part)
            run.bold = True


def build_markdown_from_sections(resume_data: dict) -> str:
    """Build markdown from resume sections."""
    markdown = ""
    sections = resume_data.get('sections', {})
    
    for section_name, content in sections.items():
        if content:
            heading = section_name.replace('_', ' ').title()
            markdown += f"\n## {heading}\n\n{content}\n\n"
    
    return markdown


def generate_pdf(resume_data: dict, enhanced_skills: list = None) -> str:
    """Generate PDF preserving markdown formatting with skill highlighting."""
    path = OUTPUT_DIR / 'updated_resume.pdf'
    c = canvas.Canvas(str(path), pagesize=letter)
    width, height = letter
    y = height - 50
    
    # Extract markdown content if available
    if 'markdown_content' in resume_data:
        content = resume_data['markdown_content']
    else:
        content = build_markdown_from_sections(resume_data)
    
    sections = parse_markdown_content(content)
    
    def check_space(needed=20):
        nonlocal y
        if y < 50 + needed:
            c.showPage()
            y = height - 50
    
    for section in sections:
        check_space()
        
        if section['type'] == 'heading1':
            c.setFont('Helvetica-Bold', 18)
            c.drawString(72, y, section['content'])
            y -= 24
        elif section['type'] == 'heading2':
            c.setFont('Helvetica-Bold', 14)
            c.drawString(72, y, section['content'])
            y -= 18
        elif section['type'] == 'heading3':
            c.setFont('Helvetica-Bold', 12)
            c.drawString(84, y, section['content'])
            y -= 14
        elif section['type'] == 'bullet':
            c.setFont('Helvetica', 10)
            for bullet in section['content']:
                check_space()
                c.drawString(90, y, f"• {bullet}")
                y -= 14
        elif section['type'] == 'separator':
            check_space(5)
            c.setLineWidth(0.5)
            c.line(72, y, width - 72, y)
            y -= 10
        elif section['type'] == 'table':
            # Handle table content for PDF
            for table_line in section['content']:
                check_space()
                c.setFont('Helvetica', 10)
                c.drawString(72, y, table_line)
                y -= 14
        elif section['type'] == 'text':
            c.setFont('Helvetica', 10)
            # Filter out stopwords from skills to highlight
            filtered_skills = [skill for skill in enhanced_skills if skill.lower() not in STOPWORDS]
            for text in section['content']:
                if text:
                    # Handle skill highlighting in PDF
                    if filtered_skills:
                        # Split text and highlight skills
                        remaining = text
                        x_pos = 72
                        while remaining:
                            found_skill = False
                            for skill in filtered_skills:
                                skill_lower = skill.lower()
                                remaining_lower = remaining.lower()
                                if skill_lower in remaining_lower:
                                    # Find the exact case match
                                    start_idx = remaining_lower.find(skill_lower)
                                    before = remaining[:start_idx]
                                    matched = remaining[start_idx:start_idx + len(skill)]
                                    after = remaining[start_idx + len(skill):]
                                    
                                    # Draw text before skill
                                    if before:
                                        c.drawString(x_pos, y, before)
                                        x_pos += c.stringWidth(before, 'Helvetica', 10)
                                    
                                    # Draw highlighted skill (using background color)
                                    c.setFillColor(colors.pink)
                                    c.drawString(x_pos, y, matched)
                                    x_pos += c.stringWidth(matched, 'Helvetica', 10)
                                    c.setFillColor(colors.black)
                                    
                                    # Continue with remaining text
                                    remaining = after
                                    found_skill = True
                                    break
                            
                            if not found_skill:
                                # No more skills found, draw remaining text
                                c.drawString(x_pos, y, remaining)
                                break
                    else:
                        # Wrap text
                        wrapper = textwrap.TextWrapper(width=100)
                        for line in wrapper.wrap(text):
                            check_space()
                            c.drawString(72, y, line)
                            y -= 12
                    y -= 12
    
    c.save()
    return str(path)


def generate_skills_files(resume_skills: list, job_description_skills: list) -> tuple:
    """
    Generate two text files:
    1. resume_skills.txt - Skills from the resume
    2. job_description_skills.txt - Skills from the job description
    Returns tuple of (resume_skills_path, job_description_skills_path)
    """
    # Remove duplicates and sort
    resume_skills = sorted(list(set([s.strip() for s in resume_skills if s.strip()])))
    job_description_skills = sorted(list(set([s.strip() for s in job_description_skills if s.strip()])))
    
    # Generate resume skills file
    resume_file_path = OUTPUT_DIR / 'resume_skills.txt'
    with open(resume_file_path, 'w') as f:
        f.write("SKILLS FROM RESUME\n")
        f.write("=" * 50 + "\n\n")
        for skill in resume_skills:
            f.write(f"• {skill}\n")
        f.write(f"\n\nTotal: {len(resume_skills)} skills")
    
    # Generate job description skills file
    jd_file_path = OUTPUT_DIR / 'job_description_skills.txt'
    with open(jd_file_path, 'w') as f:
        f.write("SKILLS FROM JOB DESCRIPTION\n")
        f.write("=" * 50 + "\n\n")
        for skill in job_description_skills:
            f.write(f"• {skill}\n")
        f.write(f"\n\nTotal: {len(job_description_skills)} skills")
    
    return str(resume_file_path), str(jd_file_path)
