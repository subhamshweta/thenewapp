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
    prompt = f"""Rewrite the following resume to optimize it for a {job_role} position. Use the strict markdown template below for your output. Each section MUST be present, even if you need to infer or improve content. Use exactly one '#' for top-level headers, followed by a space, and the exact section names shown below (no colons, no variations). Use bullet points ('-') for lists under SKILLS, PROFESSIONAL EXPERIENCE, EDUCATION, CERTIFICATIONS, PROJECTS, and HOBBIES & INTERESTS. Use '##' for subheaders under PROFESSIONAL EXPERIENCE (e.g., job titles). Ensure all sections are populated with relevant, impactful content tailored to the job role, even if minimal. Incorporate missing keywords and quantify achievements where possible based on the analysis results.

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

**Example Output:**

# NAME
John Smith

# CONTACT
Email: john@example.com | Phone: (123) 456-7890 | LinkedIn: linkedin.com/in/johnsmith

# PROFESSIONAL SUMMARY
Results-driven Software Engineer with over 5 years of experience in developing scalable applications, specializing in Python and cloud technologies. Proven track record of improving system performance by 30% through optimized code. Passionate about delivering innovative solutions for a {job_role} role.

# SKILLS
- Python
- AWS
- Agile Methodologies

# PROFESSIONAL EXPERIENCE
## Software Engineer, ABC Corp (2020-Present)
- Developed and deployed 10+ microservices using Python, improving system scalability by 40%.
- Led a team of 5 engineers in adopting Agile practices, reducing project delivery time by 20%.

## Junior Developer, XYZ Inc (2018-2020)
- Built a customer-facing web application, increasing user engagement by 25%.
- Automated testing processes, saving 15 hours of manual testing per week.

# EDUCATION
- B.S. Computer Science, University of Example, 2018

# CERTIFICATIONS
- AWS Certified Solutions Architect, 2021

# PROJECTS
- Inventory Management System: Developed a web app to streamline inventory tracking, reducing errors by 15%.

# HOBBIES & INTERESTS
- Competitive programming
- Hiking

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
                {"role": "system", "content": "You are an expert resume writer who creates impactful, achievement-oriented content optimized for both ATS and human readers. You strictly follow the provided markdown template, using exact header names and formats. You ensure all sections are present and populated with relevant content."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"}
        )
        
        rewritten_sections = json.loads(response.choices[0].message.content)
        full_resume = rewritten_sections.get('full_optimized_resume', '')

        # Post-process to fix common markdown issues
        lines = full_resume.split('\n')
        fixed_lines = []
        current_section = None
        required_sections = ['# NAME', '# CONTACT', '# PROFESSIONAL SUMMARY', '# SKILLS', 
                            '# PROFESSIONAL EXPERIENCE', '# EDUCATION', '# CERTIFICATIONS', 
                            '# PROJECTS', '# HOBBIES & INTERESTS']
        section_content = {header: [] for header in required_sections}

        for line in lines:
            line = line.strip()
            # Normalize headers
            matched_header = None
            for header in required_sections:
                if re.match(rf'^(#+)?\s*{header[2:]}[\s:]*$', line, re.IGNORECASE):
                    matched_header = header
                    break
            if matched_header:
                current_section = matched_header
                fixed_lines.append(matched_header)
            elif line:
                if current_section:
                    section_content[current_section].append(line)
                fixed_lines.append(line)

        # Ensure all required sections are present
        for header in required_sections:
            if not section_content[header]:
                section_content[header] = [f"[No {header[2:].capitalize()} Provided]"]
                logging.warning(f"Section {header} missing or empty in OpenAI output")

        # Reconstruct the full resume
        fixed_resume = []
        for header in required_sections:
            fixed_resume.append(header)
            fixed_resume.extend(section_content[header])
            fixed_resume.append('')  # Add blank line between sections

        rewritten_sections['full_optimized_resume'] = '\n'.join(fixed_resume)

        # Log differences to confirm changes
        diff = list(difflib.ndiff(resume_text.splitlines(), rewritten_sections['full_optimized_resume'].splitlines()))
        logging.debug(f"Diff between original and rewritten resume:\n{diff}")

        logging.debug(f"Rewritten resume:\n{rewritten_sections['full_optimized_resume']}")
        return rewritten_sections
    except Exception as e:
        logging.error(f"Error rewriting resume sections: {e}")
        return {
            "full_optimized_resume": f"""# NAME
Unknown Name

# CONTACT
Email: unknown@example.com | Phone: Unknown | LinkedIn: Unknown

# PROFESSIONAL SUMMARY
Optimized resume for {job_role}.

# SKILLS
- Relevant Skill 1
- Relevant Skill 2

# PROFESSIONAL EXPERIENCE
## Unknown Role, Unknown Company (Unknown Dates)
- Performed relevant duties for {job_role}.

# EDUCATION
- Unknown Degree, Unknown School, Unknown Year

# CERTIFICATIONS
- None

# PROJECTS
- None

# HOBBIES & INTERESTS
- None
""",
            "improvements_made": [{"section": "all", "original": resume_text, "improved": "basic template", "reason": "Error occurred during rewriting", "impact": "Ensures a valid resume structure"}]
        }
