import os
import json
from openai import OpenAI

# Initialize OpenAI client
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
openai = OpenAI(api_key=OPENAI_API_KEY)

def analyze_resume(resume_text, job_role):
    """
    Analyze a resume against a target job role to identify strengths and weaknesses.
    
    Args:
        resume_text (str): The text content of the resume
        job_role (str): The target job role
        
    Returns:
        dict: Analysis results including strengths and weaknesses
    """
    prompt = f"""Analyze the following resume for the role of {job_role}. 
    Perform a comprehensive analysis focusing on:
    1. Content Quality:
       - Impact and specificity of achievements
       - Use of action verbs and power words
       - Quantification of results
       - Relevance to target role
       
    2. Structure and Formatting:
       - Section organization and flow
       - Consistency in formatting
       - Professional presentation
       - ATS compatibility
       
    3. Skills and Keywords:
       - Industry-specific terminology
       - Technical and soft skills alignment
       - Missing critical skills
       - Skill presentation and grouping
       
    4. Experience and Achievements:
       - STAR method implementation
       - Impact demonstration
       - Career progression
       - Role-specific accomplishments
    
    Return your analysis as JSON with the following structure:
    {{
        "strengths": ["strength1", "strength2", ...],
        "weaknesses": ["weakness1", "weakness2", ...],
        "missing_skills": ["skill1", "skill2", ...],
        "weak_phrases": [
            {{
                "phrase": "original weak phrase",
                "suggestion": "improved version",
                "reason": "why it needs improvement",
                "impact": "how this improvement will help"
            }},
            ...
        ],
        "missing_keywords": [
            {{
                "keyword": "missing keyword",
                "importance": "high/medium/low",
                "suggestion": "how to incorporate it",
                "context": "where to add it"
            }},
            ...
        ],
        "improvement_areas": [
            {{
                "area": "area name",
                "current_state": "current description",
                "suggestion": "improvement suggestion",
                "priority": "high/medium/low"
            }},
            ...
        ],
        "job_match_score": 0.0 to 1.0,
        "quantification_opportunities": [
            {{
                "current_text": "current description",
                "suggestion": "quantified version",
                "reason": "why quantification would help",
                "impact": "expected impact of quantification"
            }},
            ...
        ],
        "formatting_issues": [
            {{
                "issue": "formatting issue",
                "location": "where it occurs",
                "suggestion": "how to fix it"
            }},
            ...
        ],
        "career_progression": {{
            "current_level": "current career level",
            "target_level": "target career level",
            "gaps": ["gap1", "gap2", ...],
            "suggestions": ["suggestion1", "suggestion2", ...]
        }}
    }}
    
    Resume:
    {resume_text}
    """
    
    try:
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are an expert resume analyzer and career coach with deep knowledge of industry standards, ATS optimization, and modern resume best practices. You provide detailed, actionable feedback."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"}
        )
        
        analysis_results = json.loads(response.choices[0].message.content)
        return analysis_results
    except Exception as e:
        print(f"Error analyzing resume: {e}")
        return {
            "strengths": ["Could not analyze strengths due to an error."],
            "weaknesses": ["Could not analyze weaknesses due to an error."],
            "missing_skills": [],
            "weak_phrases": [],
            "missing_keywords": [],
            "improvement_areas": [],
            "job_match_score": 0.0,
            "quantification_opportunities": [],
            "formatting_issues": [],
            "career_progression": {
                "current_level": "Unknown",
                "target_level": "Unknown",
                "gaps": [],
                "suggestions": []
            }
        }

def generate_improvement_tips(analysis_results, job_role):
    """
    Generate specific improvement tips based on the resume analysis and target job.
    
    Args:
        analysis_results (dict): The analysis results from analyze_resume
        job_role (str): The target job role
        
    Returns:
        list: List of improvement tips
    """
    # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
    # do not change this unless explicitly requested by the user
    
    prompt = f"""Based on the following detailed resume analysis for a {job_role} position, 
    provide specific, actionable improvement tips. Each tip should be concrete and specific.
    Focus on:
    1. Addressing weak phrases and vague descriptions
    2. Incorporating missing keywords and skills
    3. Adding quantifiable achievements
    4. Improving content structure and formatting
    
    Analysis results:
    {json.dumps(analysis_results, indent=2)}
    
    Return a list of 5-7 detailed improvement tips formatted as a JSON array.
    Each tip should include:
    - The specific issue to address
    - A concrete suggestion for improvement
    - Why this improvement matters for the target role
    """
    
    try:
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are an expert resume coach who gives actionable advice focused on specific improvements."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"}
        )
        
        improvement_tips = json.loads(response.choices[0].message.content)
        tips = improvement_tips.get("tips", [])
        if not tips and isinstance(improvement_tips, list):
            # If the API returns a direct list instead of the expected object
            tips = improvement_tips
        return tips if tips else [
            "Focus on quantifiable achievements rather than just listing responsibilities.",
            "Tailor your resume to specifically highlight skills relevant to the target position.",
            "Ensure your resume is properly formatted and easy to scan."
        ]
    except Exception as e:
        print(f"Error generating improvement tips: {e}")
        return [
            "Focus on quantifiable achievements rather than just listing responsibilities.",
            "Tailor your resume to specifically highlight skills relevant to the target position.",
            "Ensure your resume is properly formatted and easy to scan."
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
    prompt = f"""Rewrite the following resume to optimize it for a {job_role} position. Use the following strict markdown template for your output. Each section must be present, even if you have to infer or improve content. Use clear section headers as shown, and use bullet points for lists. Do not merge unrelated content. Do not include personal details in the wrong section. 

# NAME
Full Name Here

# CONTACT
Email: ... | Phone: ... | LinkedIn: ...

# PROFESSIONAL SUMMARY
A concise, impactful summary tailored to the target job.

# SKILLS
- Skill 1
- Skill 2
- Skill 3

# PROFESSIONAL EXPERIENCE
## Job Title, Company (Dates)
- Achievement or responsibility 1
- Achievement or responsibility 2

# EDUCATION
- Degree, School, Year

# CERTIFICATIONS (if any)
- Certification Name, Year

# PROJECTS (if any)
- Project Name: Short description

# HOBBIES & INTERESTS
- Hobby 1
- Hobby 2

Original resume:
{resume_text}

Analysis results:
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
                {"role": "system", "content": "You are an expert resume writer who creates impactful, achievement-oriented content optimized for both ATS and human readers. You always use the provided markdown template strictly."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"}
        )
        
        rewritten_sections = json.loads(response.choices[0].message.content)
        return rewritten_sections
    except Exception as e:
        print(f"Error rewriting resume sections: {e}")
        return {
            "full_optimized_resume": resume_text,
            "improvements_made": []
        }
