# resume_analyzer.py
import os
import json
from openai import OpenAI
import re
import logging
import difflib

# Set up logging
logging.basicConfig(filename='resume_enhancer.log', level=logging.DEBUG, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Initialize OpenAI client
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
openai = OpenAI(api_key=OPENAI_API_KEY)

def extract_resume_details(resume_text):
    """
    Extract key details from the original resume text using heuristics.
    
    Args:
        resume_text (str): The original resume text
        
    Returns:
        dict: Extracted details (name, contact, experience, etc.)
    """
    details = {
        "name": "Unknown Name",
        "contact": "Email: unknown@example.com | Phone: Unknown | LinkedIn: Unknown",
        "summary": "",
        "skills": [],
        "experience": [],
        "education": [],
        "certifications": [],
        "projects": [],
        "hobbies": []
    }

    lines = resume_text.split('\n')
    current_section = None

    # Regex patterns for common resume elements
    email_pattern = r'[\w\.-]+@[\w\.-]+\.\w+'
    phone_pattern = r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
    linkedin_pattern = r'linkedin\.com/in/[\w-]+'

    for line in lines:
        line = line.strip()
        if not line:
            continue

        # Detect name (first non-empty line, often at the top)
        if not details["name"] and re.match(r'^[A-Z][a-z]+ [A-Z][a-z]+$', line, re.IGNORECASE):
            details["name"] = line
            continue

        # Detect sections
        if re.match(r'^(contact|personal information|info):?$', line, re.IGNORECASE):
            current_section = "contact"
            continue
        elif re.match(r'^(summary|objective|professional summary):?$', line, re.IGNORECASE):
            current_section = "summary"
            continue
        elif re.match(r'^(skills|key skills|technical skills):?$', line, re.IGNORECASE):
            current_section = "skills"
            continue
        elif re.match(r'^(experience|work experience|professional experience):?$', line, re.IGNORECASE):
            current_section = "experience"
            continue
        elif re.match(r'^(education|academic background):?$', line, re.IGNORECASE):
            current_section = "education"
            continue
        elif re.match(r'^(certifications|certificates):?$', line, re.IGNORECASE):
            current_section = "certifications"
            continue
        elif re.match(r'^(projects|portfolio):?$', line, re.IGNORECASE):
            current_section = "projects"
            continue
        elif re.match(r'^(hobbies|interests|hobbies & interests):?$', line, re.IGNORECASE):
            current_section = "hobbies"
            continue

        # Process content under sections
        if current_section == "contact":
            contact_parts = []
            email = re.search(email_pattern, line)
            phone = re.search(phone_pattern, line)
            linkedin = re.search(linkedin_pattern, line)
            if email:
                contact_parts.append(f"Email: {email.group()}")
            if phone:
                contact_parts.append(f"Phone: {phone.group()}")
            if linkedin:
                contact_parts.append(f"LinkedIn: {linkedin.group()}")
            if contact_parts:
                details["contact"] = " | ".join(contact_parts)
        elif current_section == "summary":
            if not details["summary"]:
                details["summary"] = line
        elif current_section == "skills" and (line.startswith('-') or re.match(r'^\w+', line)):
            skill = line.lstrip('- ').strip()
            if skill:
                details["skills"].append(skill)
        elif current_section == "experience" and line:
            details["experience"].append(line)
        elif current_section == "education" and line:
            details["education"].append(line)
        elif current_section == "certifications" and line:
            details["certifications"].append(line)
        elif current_section == "projects" and line:
            details["projects"].append(line)
        elif current_section == "hobbies" and line:
            details["hobbies"].append(line)

    logging.debug(f"Extracted resume details: {json.dumps(details, indent=2)}")
    return details

def analyze_resume(resume_text, job_role):
    """
    Analyze the resume for strengths, weaknesses, and job match score.
    
    Args:
        resume_text (str): The original resume text
        job_role (str): The target job role
        
    Returns:
        dict: Analysis results including strengths, weaknesses, and job match
    """
    prompt = f"""Analyze the following resume for a {job_role} position. Evaluate its strengths, weaknesses, and overall job match score (0 to 1 scale). Identify specific areas for improvement, such as weak phrases, missing keywords, and opportunities for better quantification. Provide detailed feedback in the following JSON format:

{{
    "job_match_score": 0.8,
    "strengths": ["Strong technical skills listed", "Relevant work experience"],
    "weaknesses": ["Lacks specific achievements", "Missing key industry keywords"],
    "weak_phrases": [
        {{"phrase": "Responsible for managing a team", "suggestion": "Led a team of 5 engineers to deliver projects on time", "reason": "Too vague, lacks impact and specificity"}}
    ],
    "missing_keywords": [
        {{"keyword": "Agile", "importance": "high", "suggestion": "Mention experience with Agile methodologies in the experience section", "context": "Agile is a critical methodology in software development roles"}}
    ],
    "quantification_opportunities": [
        {{"current_text": "Improved system performance", "suggestion": "Enhanced system performance by 30% through optimization", "reason": "Quantifying the improvement adds credibility and impact"}}
    ]
}}

Resume:
{resume_text}
"""
    
    try:
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are an expert resume reviewer specializing in optimizing resumes for specific job roles. You provide detailed, actionable feedback to improve resumes for both ATS and human readers."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"}
        )
        analysis_results = json.loads(response.choices[0].message.content)
        logging.debug(f"Analysis results: {json.dumps(analysis_results, indent=2)}")
        return analysis_results
    except Exception as e:
        logging.error(f"Error analyzing resume: {e}")
        return {
            "job_match_score": 0.5,
            "strengths": [],
            "weaknesses": ["Unable to analyze resume due to processing error"],
            "weak_phrases": [],
            "missing_keywords": [],
            "quantification_opportunities": []
        }

def generate_improvement_tips(analysis_results, job_role):
    """
    Generate specific improvement tips based on analysis results.
    
    Args:
        analysis_results (dict): Analysis results from analyze_resume
        job_role (str): The target job role
        
    Returns:
        list: List of improvement tips
    """
    try:
        prompt = f"""Based on the following resume analysis for a {job_role} position, provide a list of concise, actionable improvement tips (each 1-2 sentences long) to enhance the resume. Focus on addressing weaknesses, weak phrases, missing keywords, and quantification opportunities. Return the tips as a JSON array of strings.

Analysis:
{json.dumps(analysis_results, indent=2)}

Example output:
[
    "Quantify achievements in the experience section, such as 'increased sales by 20%' instead of 'improved sales'.",
    "Incorporate missing keywords like 'Agile' in the skills or experience section to improve ATS compatibility."
]
"""
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are an expert resume advisor providing concise, actionable tips to improve resumes for specific job roles."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"}
        )
        tips = json.loads(response.choices[0].message.content)
        logging.debug(f"Improvement tips: {tips}")
        return tips if isinstance(tips, list) else []
    except Exception as e:
        logging.error(f"Error generating improvement tips: {e}")
        return [
            "Quantify achievements to demonstrate impact.",
            "Ensure all relevant keywords for the job role are included."
        ]

def rewrite_resume_sections(resume_text, analysis_results, job_role):
    """
    Rewrite resume sections to be more impactful and aligned with the target job.
    
    Args:
        resume_text (str): The original resume text
        analysis_results (dict): Analysis results from analyze_resume
        job_role (str): The target job role
        
    Returns:
        dict: Rewritten sections and full optimized resume
    """
    # Extract details from the original resume
    extracted_details = extract_resume_details(resume_text)

    prompt = f"""Rewrite the following resume to optimize it for a {job_role} position. Use the strict markdown template below for your output. Each section MUST be present, even if you need to infer or improve content. Use exactly one '#' for top-level headers, followed by a space, and the exact section names shown below (no colons, no variations). Use bullet points ('-') for lists under SKILLS, PROFESSIONAL EXPERIENCE, EDUCATION, CERTIFICATIONS, PROJECTS, and HOBBIES & INTERESTS. Use '##' for subheaders under PROFESSIONAL EXPERIENCE (e.g., job titles). Ensure all sections are populated with relevant, impactful content tailored to the job role. Incorporate missing keywords and quantify achievements where possible based on the analysis results. Avoid generic phrases like 'Relevant Skill 1' or 'Unknown Role'. If specific details are missing, infer plausible details based on the job role and extracted information.

**Extracted Details from Original Resume:**
- Name: {extracted_details['name']}
- Contact: {extracted_details['contact']}
- Summary: {extracted_details['summary']}
- Skills: {', '.join(extracted_details['skills']) if extracted_details['skills'] else 'None'}
- Experience: {', '.join(extracted_details['experience']) if extracted_details['experience'] else 'None'}
- Education: {', '.join(extracted_details['education']) if extracted_details['education'] else 'None'}
- Certifications: {', '.join(extracted_details['certifications']) if extracted_details['certifications'] else 'None'}
- Projects: {', '.join(extracted_details['projects']) if extracted_details['projects'] else 'None'}
- Hobbies & Interests: {', '.join(extracted_details['hobbies']) if extracted_details['hobbies'] else 'None'}

**Template (follow exactly):**

# NAME
Full Name Here

# CONTACT
Email: email@example.com | Phone: (123) 456-7890 | LinkedIn: linkedin.com/in/username

# PROFESSIONAL SUMMARY
A concise, impactful summary (2-3 sentences) tailored to the target job.

# SKILLS
- Skill 1
- Skill 2
- Skill 3

# PROFESSIONAL EXPERIENCE
## Job Title, Company (Dates)
- Achievement or responsibility 1
- Achievement or responsibility 2

## Job Title, Company (Dates)
- Achievement or responsibility 1
- Achievement or responsibility 2

# EDUCATION
- Degree, School, Year
- Degree, School, Year

# CERTIFICATIONS
- Certification Name, Year
- Certification Name, Year

# PROJECTS
- Project Name: Short description
- Project Name: Short description

# HOBBIES & INTERESTS
- Hobby 1
- Hobby 2

**Example Output for a Digital Marketing Role:**

# NAME
Jane Doe

# CONTACT
Email: jane.doe@example.com | Phone: (987) 654-3210 | LinkedIn: linkedin.com/in/janedoe

# PROFESSIONAL SUMMARY
Dynamic Digital Marketing Specialist with over 5 years of experience in SEO, content strategy, and social media management. Increased online engagement by 40% through targeted campaigns for e-commerce brands. Passionate about leveraging data-driven strategies to drive growth in a {job_role} role.

# SKILLS
- SEO
- Social Media Marketing
- Google Analytics

# PROFESSIONAL EXPERIENCE
## Digital Marketing Manager, E-Commerce Co (2020-Present)
- Boosted website traffic by 50% through SEO and content marketing strategies.
- Managed a $100K annual ad budget, improving ROI by 30% with targeted campaigns.

## Marketing Associate, Startup Inc (2018-2020)
- Grew Instagram following by 10K followers in 6 months through organic content.
- Analyzed campaign performance using Google Analytics, optimizing for a 20% increase in conversions.

# EDUCATION
- B.A. Marketing, University of Example, 2018

# CERTIFICATIONS
- Google Analytics Certified, 2021

# PROJECTS
- E-Commerce Campaign: Launched a holiday campaign that increased sales by 25%.

# HOBBIES & INTERESTS
- Digital photography
- Traveling

**Original Resume:**
{resume_text}

**Analysis Results:**
{json.dumps(analysis_results, indent=2)}

Return your response in the following JSON format:
{{
    "full_optimized_resume": "the complete rewritten resume in the above markdown template",
    "improvements_made": [
        {{
            "section": "section name",
            "original": "original text",
            "improved": "improved text",
            "reason": "why this improvement was made",
            "impact": "how this improves the resume"
        }},
        ...
    ]
}}
"""
    
    try:
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are an expert resume writer who creates impactful, achievement-oriented content optimized for both ATS and human readers. You strictly follow the provided markdown template, using exact header names and formats. You ensure all sections are present and populated with relevant, job-specific content, avoiding generic phrases like 'Relevant Skill 1' or 'Unknown Role'. You infer plausible details if specific information is missing, based on the job role and extracted details."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"}
        )
        
        rewritten_sections = json.loads(response.choices[0].message.content)
        full_resume = rewritten_sections.get('full_optimized_resume', '')

        # Post-process to ensure all sections are present
        lines = full_resume.split('\n')
        fixed_lines = []
        current_section = None
        required_sections = ['# NAME', '# CONTACT', '# PROFESSIONAL SUMMARY', '# SKILLS', 
                            '# PROFESSIONAL EXPERIENCE', '# EDUCATION', '# CERTIFICATIONS', 
                            '# PROJECTS', '# HOBBIES & INTERESTS']
        section_content = {header: [] for header in required_sections}

        for line in lines:
            line = line.strip()
            matched_header = None
            for header in required_sections:
                if re.match(rf'^{header}$', line, re.IGNORECASE):
                    matched_header = header
                    break
            if matched_header:
                current_section = matched_header
                fixed_lines.append(matched_header)
            elif line:
                if current_section:
                    section_content[current_section].append(line)
                fixed_lines.append(line)

        # Ensure all required sections are present, using extracted details as fallback
        for header in required_sections:
            if not section_content[header]:
                if header == '# NAME':
                    section_content[header] = [extracted_details['name']]
                elif header == '# CONTACT':
                    section_content[header] = [extracted_details['contact']]
                elif header == '# PROFESSIONAL SUMMARY':
                    section_content[header] = [f"Professional with experience relevant to {job_role}." if not extracted_details['summary'] else extracted_details['summary']]
                elif header == '# SKILLS':
                    section_content[header] = [f"- {skill}" for skill in extracted_details['skills']] or [f"- {job_role}-specific skill"]
                elif header == '# PROFESSIONAL EXPERIENCE':
                    section_content[header] = extracted_details['experience'] or [f"## {job_role}-related Role, Company (Recent)", f"- Contributed to {job_role} initiatives."]
                elif header == '# EDUCATION':
                    section_content[header] = extracted_details['education'] or ["- Relevant Degree, University, Year"]
                elif header == '# CERTIFICATIONS':
                    section_content[header] = extracted_details['certifications'] or ["- None"]
                elif header == '# PROJECTS':
                    section_content[header] = extracted_details['projects'] or ["- None"]
                elif header == '# HOBBIES & INTERESTS':
                    section_content[header] = extracted_details['hobbies'] or ["- None"]
                logging.warning(f"Section {header} missing in OpenAI output, using fallback content")

        # Reconstruct the full resume
        fixed_resume = []
        for header in required_sections:
            fixed_resume.append(header)
            fixed_resume.extend(section_content[header])
            fixed_resume.append('')

        rewritten_sections['full_optimized_resume'] = '\n'.join(fixed_resume)

        # Log differences to confirm changes
        diff = list(difflib.ndiff(resume_text.splitlines(), rewritten_sections['full_optimized_resume'].splitlines()))
        logging.debug(f"Diff between original and rewritten resume:\n{diff}")

        logging.debug(f"Rewritten resume:\n{rewritten_sections['full_optimized_resume']}")
        return rewritten_sections
    except Exception as e:
        logging.error(f"Error rewriting resume sections: {e}")
        # Construct a resume using extracted details instead of generic fallback
        full_resume = [
            "# NAME",
            extracted_details['name'],
            "",
            "# CONTACT",
            extracted_details['contact'],
            "",
            "# PROFESSIONAL SUMMARY",
            extracted_details['summary'] or f"Professional with experience relevant to {job_role}.",
            "",
            "# SKILLS"
        ]
        full_resume.extend([f"- {skill}" for skill in extracted_details['skills']] or [f"- {job_role}-specific skill"])
        full_resume.extend(["", "# PROFESSIONAL EXPERIENCE"])
        full_resume.extend(extracted_details['experience'] or [f"## {job_role}-related Role, Company (Recent)", f"- Contributed to {job_role} initiatives."])
        full_resume.extend(["", "# EDUCATION"])
        full_resume.extend(extracted_details['education'] or ["- Relevant Degree, University, Year"])
        full_resume.extend(["", "# CERTIFICATIONS"])
        full_resume.extend(extracted_details['certifications'] or ["- None"])
        full_resume.extend(["", "# PROJECTS"])
        full_resume.extend(extracted_details['projects'] or ["- None"])
        full_resume.extend(["", "# HOBBIES & INTERESTS"])
        full_resume.extend(extracted_details['hobbies'] or ["- None"])

        return {
            "full_optimized_resume": "\n".join(full_resume),
            "improvements_made": [{"section": "all", "original": resume_text, "improved": "extracted details", "reason": "Error occurred during OpenAI call", "impact": "Uses original details to ensure a valid resume"}]
        }
