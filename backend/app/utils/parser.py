from typing import List, Dict
import re

KEYWORD_PATTERN = re.compile(r"\b[a-zA-Z][a-zA-Z0-9_\+\#\-]*\b")

# Common stopwords to exclude from skills
STOPWORDS = {
    'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'from',
    'as', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did',
    'will', 'would', 'should', 'could', 'can', 'may', 'might', 'must', 'that', 'this', 'these', 'those',
    'i', 'you', 'he', 'she', 'it', 'we', 'they', 'what', 'which', 'who', 'when', 'where', 'why', 'how',
    'all', 'each', 'every', 'both', 'few', 'more', 'most', 'other', 'some', 'such', 'no', 'nor', 'not',
    'only', 'own', 'same', 'so', 'than', 'too', 'very', 'just', 'also', 'about', 'above', 'after', 'again',
    'against', 'am', 'our', 'out', 'over', 'before', 'below', 'between', 'here', 'their', 'them', 'my',
    'me', 'him', 'her', 'us', 'up', 'if', 'while', 'through', 'during', 'including', 'within', 'without',
    'new', 'old', 'good', 'bad', 'best', 'better', 'well', 'many', 'any', 'your', 'its', 'his', 'hers',
    'ours', 'theirs', 'mine', 'yours', 'ones', 'yourself', 'herself', 'himself', 'themselves', 'myself',
    'ourselves', 'yourselves', 'being', 'having', 'does', 'does', 'been', 'then', 'now', 'here', 'there'
}

def is_valid_skill(word: str) -> bool:
    """Check if a word is a valid skill (not a stopword)."""
    return word.lower() not in STOPWORDS


def normalize_skills(skills_input: str) -> list:
    """
    Process raw user skill input and return clean normalized list.
    
    Handles:
    - Split by comma, semicolon, newline
    - Convert to lowercase
    - Trim whitespace
    - Remove duplicates
    - Remove empty strings
    """
    if not skills_input:
        return []
    
    # Split by multiple delimiters: comma, semicolon, newline
    raw_skills = re.split(r'[,;\n]+', skills_input)
    
    normalized = []
    seen = set()
    
    for skill in raw_skills:
        # Trim whitespace
        cleaned = skill.strip()
        
        # Skip empty strings
        if not cleaned:
            continue
        
        # Convert to lowercase for deduplication but preserve original case in output
        lower_skill = cleaned.lower()
        
        # Skip duplicates (case-insensitive)
        if lower_skill in seen:
            continue
        
        seen.add(lower_skill)
        # Store the original casing from user input (just trimmed)
        normalized.append(cleaned)
    
    return normalized


def parse_resume_text(text: str) -> Dict[str, any]:
    """
    Parse resume text while preserving structure and formatting.
    Returns sections with their original content + extracted skills.
    """
    lines = text.split('\n')
    
    sections = {}
    current_section = None
    current_content = []
    skills_list = []
    
    # Define section headers to recognize
    section_map = {
        r'(skills|technical skills|expertise)': 'skills',
        r'(experience|work experience|professional experience)': 'experience',
        r'(education|academic)': 'education',
        r'(certification|certifications)': 'certifications',
        r'(project|projects)': 'projects',
        r'(summary|objective|professional summary|profile)': 'summary',
    }
    
    # Pattern to detect ANY section header (uppercase words, possibly with colon, at start of line)
    section_header_pattern = re.compile(r'^[A-Z][A-Z\s]+:?\s*$')
    
    for line in lines:
        lower_line = line.lower().strip()
        
        # Check if this is a section header we recognize
        is_section_header = False
        for pattern, section_name in section_map.items():
            if re.match(pattern + r'\s*:?\s*$', lower_line):
                # Save previous section
                if current_section and current_content:
                    content_text = '\n'.join(current_content).strip()
                    sections[current_section] = content_text
                    # Extract skills if we were in skills section
                    if current_section == 'skills':
                        for content_line in current_content:
                            skill_items = re.split(r'[,\n•\-]', content_line)
                            for skill in skill_items:
                                skill = skill.strip()
                                if skill and len(skill) > 2 and re.match(r'^[a-zA-Z][a-zA-Z0-9_\+\#\-]*$', skill) and is_valid_skill(skill):
                                    skills_list.append(skill)
                
                current_section = section_name
                current_content = []
                is_section_header = True
                break
        
        # If not a recognized section, check if it's an unrecognized section header
        if not is_section_header and section_header_pattern.match(line.strip()) and line.strip():
            # This looks like a section header we don't recognize
            if current_section and current_content:
                content_text = '\n'.join(current_content).strip()
                sections[current_section] = content_text
                # Extract skills if we were in skills section
                if current_section == 'skills':
                    for content_line in current_content:
                        skill_items = re.split(r'[,\n•\-]', content_line)
                        for skill in skill_items:
                            skill = skill.strip()
                            if skill and len(skill) > 2 and re.match(r'^[a-zA-Z][a-zA-Z0-9_\+\#\-]*$', skill) and is_valid_skill(skill):
                                skills_list.append(skill)
            
            current_section = None
            current_content = []
            is_section_header = True
        
        if not is_section_header and current_section and line.strip():
            current_content.append(line)
    
    # Save last section
    if current_section and current_content:
        content_text = '\n'.join(current_content).strip()
        sections[current_section] = content_text
        # Extract skills if we were in skills section
        if current_section == 'skills':
            for content_line in current_content:
                skill_items = re.split(r'[,\n•\-]', content_line)
                for skill in skill_items:
                    skill = skill.strip()
                    if skill and len(skill) > 2 and re.match(r'^[a-zA-Z][a-zA-Z0-9_\+\#\-]*$', skill) and is_valid_skill(skill):
                        skills_list.append(skill)
    
    # Extract unique skills, excluding stopwords
    unique_skills = list(set(skills_list))
    
    keywords = KEYWORD_PATTERN.findall(text)
    
    return {
        "sections": sections,
        "skills": unique_skills,
        "keywords": list(dict.fromkeys(keywords))[:80],
    }


KNOWN_TOOLS = {
    'python', 'sql', 'aws', 'react', 'docker', 'git', 'kubernetes', 'jira', 'slack', 'azure',
    'gcp', 'tableau', 'powerbi', 'excel', 'nodejs', 'javascript', 'typescript', 'django',
    'flask', 'fastapi', 'pandas', 'numpy', 'tensorflow', 'pytorch', 'linux', 'spark',
    'hadoop', 'github', 'gitlab', 'jenkins', 'terraform', 'ansible', 'mongodb', 'postgresql',
    'mysql', 'redis'
}

SOFT_SKILLS = {
    'communication', 'teamwork', 'collaboration', 'leadership', 'problem-solving',
    'adaptability', 'creativity', 'time management', 'critical thinking', 'attention to detail',
    'organization', 'interpersonal', 'presentation', 'empathy', 'decision-making', 'initiative'
}

RESPONSIBILITY_KEYWORDS = {
    'responsible', 'manage', 'lead', 'oversee', 'coordinate', 'develop', 'design',
    'implement', 'execute', 'maintain', 'support', 'drive', 'deliver', 'optimize',
    'analyze', 'build'
}

SECTION_HEADING_KEYWORDS = {
    'skills': ['skills', 'required skills', 'technical skills', 'preferred skills', 'qualifications', 'requirements', 'must have', 'must-haves', 'you should have', 'you will have'],
    'responsibilities': ['responsibilities', 'role responsibilities', 'what you will do', 'what you\'ll do', 'your responsibilities', 'what we expect', 'responsible for'],
    'tools': ['tools', 'technologies', 'platforms', 'tech stack', 'software', 'systems'],
}


def normalize_heading(text: str) -> str:
    return re.sub(r'[^a-z0-9 ]+', '', text.lower()).strip()


def extract_section_lines(text: str) -> Dict[str, list]:
    lines = text.splitlines()
    sections = {}
    current_section = None
    for raw_line in lines:
        line = raw_line.strip()
        if not line:
            continue

        normalized = normalize_heading(line.rstrip(':'))
        found_section = None
        for section_name, variants in SECTION_HEADING_KEYWORDS.items():
            if normalized in [normalize_heading(variant) for variant in variants]:
                found_section = section_name
                break

        if found_section:
            current_section = found_section
            sections.setdefault(current_section, [])
            continue

        if current_section:
            sections[current_section].append(line)

    return sections


def extract_list_items(lines: list) -> list:
    items = []
    for line in lines:
        stripped = re.sub(r'^[\-\*\•\d\)\.\s]+', '', line).strip()
        if not stripped:
            continue
        if ',' in stripped and not re.match(r'^\d+\.', stripped):
            parts = [part.strip() for part in stripped.split(',') if part.strip()]
            items.extend(parts)
        else:
            items.append(stripped)
    return items


def filter_keywords(tokens: list, limit: int = 40) -> list:
    seen = set()
    filtered = []
    for token in tokens:
        if len(token) <= 2:
            continue
        lower = token.lower()
        if not is_valid_skill(lower):
            continue
        if lower in seen:
            continue
        seen.add(lower)
        filtered.append(token)
        if len(filtered) >= limit:
            break
    return filtered


def analyze_job_description(job_description: str) -> Dict[str, List[str]]:
    sections = extract_section_lines(job_description)
    tokens = KEYWORD_PATTERN.findall(job_description)
    keywords = filter_keywords(tokens, limit=40)

    skills = []
    tools = []
    responsibilities = []
    soft_skills = []

    if 'skills' in sections:
        skills = [item for item in extract_list_items(sections['skills']) if len(item) > 1]
    elif 'tools' in sections:
        skills = [item for item in extract_list_items(sections['tools']) if len(item) > 1]

    if 'tools' in sections:
        tools = [item for item in extract_list_items(sections['tools']) if len(item) > 1]
    if 'responsibilities' in sections:
        responsibilities = extract_list_items(sections['responsibilities'])

    if not skills:
        skills = [token for token in keywords if token.lower() not in KNOWN_TOOLS and token.lower() not in SOFT_SKILLS][:20]

    if not tools:
        tools = [token for token in keywords if token.lower() in KNOWN_TOOLS]

    if not responsibilities:
        sentence_pattern = re.compile(r'([A-Z][^\.\n]*\b(?:' + '|'.join(RESPONSIBILITY_KEYWORDS) + r')\b[^\.\n]*[\.\n])', re.IGNORECASE)
        responsibilities = [sentence.strip() for sentence in sentence_pattern.findall(job_description) if sentence.strip()]

    soft_skills = [token for token in keywords if token.lower() in SOFT_SKILLS]

    return {
        'keywords': keywords,
        'required_skills': list(dict.fromkeys(skills))[:20],
        'tools': list(dict.fromkeys(tools))[:20],
        'responsibilities': responsibilities[:15],
        'soft_skills': list(dict.fromkeys(soft_skills))[:15],
    }


def generate_improved_resume_text(resume_data: dict, match_data: dict, user_skills: List[str]) -> Dict[str, object]:
    """
    Generate improved resume text while maintaining truthfulness.
    
    Improvements:
    - Enhanced professional summary with metrics and action verbs
    - Stronger bullet points with action verbs
    - Suggested skills added naturally
    - ATS-friendly formatting
    
    Only adds skills from user_skills (user-confirmed).
    """
    sections = resume_data.get("sections", {})
    suggested_skills = match_data.get("suggested_skills", [])
    
    # ACTION VERBS for bullet point improvement
    ACTION_VERBS = [
        "Developed", "Implemented", "Designed", "Led", "Managed", "Optimized",
        "Achieved", "Delivered", "Built", "Created", "Improved", "Streamlined",
        "Enhanced", "Accelerated", "Pioneered", "Executed", "Established", "Launched"
    ]
    
    improved_sections = {}
    
    # Improve Summary
    summary = sections.get("summary", "").strip()
    if summary:
        # Keep original but enhance if weak
        words = summary.split()
        if len(words) < 20:
            # Summary is too brief, suggest enhancement
            improved_sections["summary"] = summary + "\n\n[Note: Consider expanding this summary with specific achievements and metrics]"
        elif any(verb in summary for verb in ACTION_VERBS):
            improved_sections["summary"] = summary
        else:
            # Try to add context about the role
            improved_sections["summary"] = f"{summary} with expertise in key technologies including {', '.join(user_skills[:3])}."
    else:
        improved_sections["summary"] = "[Add a professional summary highlighting your key achievements and expertise]"
    
    # Improve Experience bullets
    experience = sections.get("experience", "").strip()
    if experience:
        lines = experience.split('\n')
        improved_bullets = []
        for line in lines:
            stripped = line.strip()
            if stripped.startswith(('-', '•', '*')):
                # Extract bullet content
                content = re.sub(r'^[\-\•\*]\s*', '', stripped)
                
                # Check for weak language and improve
                if content.lower().startswith(('was ', 'were ', 'is ', 'are ', 'did ', 'do ', 'worked')):
                    # Replace with action verb
                    verb = next((v for v in ACTION_VERBS if v.lower() not in content.lower()), ACTION_VERBS[0])
                    # Remove weak starter and add action verb
                    content = re.sub(r'^(was|were|is|are|did|do|worked)\s+', '', content, flags=re.IGNORECASE)
                    content = f"{verb} {content}" if content else f"{verb} on projects"
                
                improved_bullets.append(f"• {content}")
            else:
                improved_bullets.append(line)
        
        improved_sections["experience"] = '\n'.join(improved_bullets)
    else:
        improved_sections["experience"] = sections.get("experience", "")
    
    # Improve Skills section with suggested skills
    skills_section = sections.get("skills", "").strip()
    all_skills = user_skills.copy()
    
    # Add suggested skills that aren't already in user_skills
    for skill in suggested_skills:
        if skill.lower() not in [s.lower() for s in all_skills]:
            all_skills.append(skill)
    
    if all_skills:
        improved_sections["skills"] = ", ".join(all_skills)
    else:
        improved_sections["skills"] = skills_section
    
    # Keep other sections unchanged
    for section_name in ["education", "certifications", "projects"]:
        improved_sections[section_name] = sections.get(section_name, "")
    
    # Build improved resume text
    improved_text = ""
    
    # Reconstruct with ATS-friendly formatting
    if improved_sections.get("summary"):
        improved_text += "## PROFESSIONAL SUMMARY\n"
        improved_text += improved_sections["summary"] + "\n\n"
    
    if improved_sections.get("skills"):
        improved_text += "## SKILLS\n"
        improved_text += improved_sections["skills"] + "\n\n"
    
    if improved_sections.get("experience"):
        improved_text += "## EXPERIENCE\n"
        improved_text += improved_sections["experience"] + "\n\n"
    
    if improved_sections.get("education"):
        improved_text += "## EDUCATION\n"
        improved_text += improved_sections["education"] + "\n\n"
    
    if improved_sections.get("projects"):
        improved_text += "## PROJECTS\n"
        improved_text += improved_sections["projects"] + "\n\n"
    
    if improved_sections.get("certifications"):
        improved_text += "## CERTIFICATIONS\n"
        improved_text += improved_sections["certifications"] + "\n\n"
    
    return {
        "original_resume": '\n'.join([f"{k.upper()}\n{v}" for k, v in sections.items() if v]),
        "improved_resume": improved_text.strip(),
        "skills_added": [s for s in suggested_skills if s.lower() not in [u.lower() for u in [sections.get("skills", "")]]],
        "improvements_made": [
            f"Added {len(suggested_skills)} recommended skills" if suggested_skills else "No additional skills recommended",
            "Enhanced summary with professional language" if improved_sections.get("summary") else "",
            "Improved experience bullets with stronger action verbs" if experience else "",
        ],
        "ats_friendly": True
    }


def generate_resume_improvements(resume_data: dict, match_data: dict, job_description: str) -> Dict[str, object]:
    """
    Generate actionable resume improvement suggestions.
    
    Analyzes:
    - Professional summary quality
    - Skills gaps (from suggested_skills only)
    - Bullet point effectiveness
    - Missing keywords
    - Weak sections
    
    Returns improvement suggestions without suggesting fake skills.
    """
    sections = resume_data.get("sections", {})
    suggested_skills = match_data.get("suggested_skills", [])
    missing_keywords = match_data.get("missing_from_resume", [])[:10]
    
    improvements = {
        "summary_suggestions": [],
        "skills_to_add": suggested_skills,
        "bullet_point_improvements": [],
        "missing_keywords": missing_keywords,
        "weak_sections": [],
        "action_items": []
    }
    
    # Analyze professional summary
    summary = sections.get("summary", "").strip()
    if summary:
        word_count = len(summary.split())
        if word_count < 20:
            improvements["summary_suggestions"].append("Summary is too brief. Aim for 50-100 words highlighting key achievements.")
        if word_count > 300:
            improvements["summary_suggestions"].append("Summary is too long. Consider condensing to 50-100 words.")
        if not any(word in summary.lower() for word in ["achieved", "led", "managed", "delivered", "improved"]):
            improvements["summary_suggestions"].append("Add action verbs like 'achieved', 'led', 'managed', 'delivered', 'improved' to strengthen your summary.")
        if not any(char.isdigit() for char in summary):
            improvements["summary_suggestions"].append("Include quantifiable achievements (e.g., '30% improvement', '500+ users') to make your summary more compelling.")
    else:
        improvements["summary_suggestions"].append("Add a professional summary or objective statement at the top of your resume.")
    
    # Analyze bullet points for weak language
    for section_name in ["experience", "projects"]:
        content = sections.get(section_name, "").strip()
        if content:
            lines = [line.strip() for line in content.split('\n') if line.strip().startswith(('-', '•', '*'))]
            weak_bullets = []
            for line in lines:
                cleaned = re.sub(r'^[\-\•\*]\s*', '', line)
                # Check for weak patterns
                if cleaned.lower().startswith(('was', 'were', 'is', 'are', 'did', 'do')):
                    weak_bullets.append(f"'{cleaned[:50]}...' - Rewrite to start with an action verb like 'Developed', 'Implemented', 'Designed'")
                if 'etc' in cleaned.lower() or '...' in cleaned:
                    weak_bullets.append(f"'{cleaned[:50]}...' - Avoid 'etc.' or trailing ellipsis; be specific.")
            
            if weak_bullets:
                improvements["bullet_point_improvements"].extend(weak_bullets[:3])
    
    # Identify weak sections
    min_content_length = 50  # Minimum acceptable content length
    for section_name in ["experience", "education", "projects"]:
        content = sections.get(section_name, "").strip()
        if content and len(content) < min_content_length:
            improvements["weak_sections"].append(f"{section_name.title()}: Consider adding more detail or examples.")
        elif not content and section_name in ["experience", "education"]:
            improvements["weak_sections"].append(f"{section_name.title()}: Section is empty or missing.")
    
    # Generate action items
    if suggested_skills:
        improvements["action_items"].append(f"Add {len(suggested_skills)} high-impact skills from the job description: {', '.join(suggested_skills[:5])}")
    
    if missing_keywords:
        improvements["action_items"].append(f"Incorporate these keywords to improve ATS match: {', '.join(missing_keywords[:5])}")
    
    if improvements["summary_suggestions"]:
        improvements["action_items"].append("Improve your professional summary with metrics and action verbs")
    
    if improvements["bullet_point_improvements"]:
        improvements["action_items"].append("Strengthen bullet points by using action verbs and removing weak language")
    
    return improvements


def compare_skills(resume_text: str, job_description: str, user_skills: List[str]) -> Dict[str, object]:
    """
    Compare resume keywords with job description and user skillset.
    
    Rules:
    - Only suggest adding skills that are in the user's provided skillset
    - Calculate match percentage based on JD keywords found in resume
    
    Returns:
    - match_percentage: % of JD keywords found in resume
    - matched_skills: Skills present in both resume and JD
    - missing_from_resume: JD keywords not in resume (from any source)
    - suggested_skills: Skills from user_skills that are in JD but not in resume (RECOMMENDATIONS)
    - jd_keywords_missing: Top JD keywords missing from resume
    """
    # Extract tokens from texts (case-insensitive matching)
    resume_tokens = {token.lower() for token in KEYWORD_PATTERN.findall(resume_text) if len(token) > 2}
    jd_tokens = {token.lower() for token in KEYWORD_PATTERN.findall(job_description) if len(token) > 2}
    user_skills_lower = {skill.lower(): skill for skill in user_skills}  # Keep original casing
    
    # Filter out stopwords
    resume_tokens = {t for t in resume_tokens if is_valid_skill(t)}
    jd_tokens = {t for t in jd_tokens if is_valid_skill(t)}
    
    # Calculate matched skills (present in both resume and JD)
    matched_tokens = resume_tokens & jd_tokens
    matched_skills = sorted([token for token in matched_tokens])
    
    # Calculate missing skills from JD not in resume
    missing_from_resume = sorted([token for token in jd_tokens if token not in resume_tokens])
    
    # Calculate suggested skills: from user_skills that are in JD but not in resume
    suggested_skills = []
    for user_skill_lower, user_skill_original in user_skills_lower.items():
        if user_skill_lower in jd_tokens and user_skill_lower not in resume_tokens:
            suggested_skills.append(user_skill_original)
    suggested_skills = sorted(list(set(suggested_skills)))
    
    # Calculate match percentage
    if len(jd_tokens) == 0:
        match_percentage = 0
    else:
        match_percentage = int(100 * len(matched_tokens) / len(jd_tokens))
    
    return {
        "match_percentage": match_percentage,
        "matched_skills": matched_skills[:30],
        "missing_from_resume": missing_from_resume[:30],
        "suggested_skills": suggested_skills[:20],  # These come from user_skills
        "jd_keywords_missing": missing_from_resume[:20],
        "resume_keywords": sorted(list(resume_tokens))[:50],
        "jd_keywords": sorted(list(jd_tokens))[:50],
    }
