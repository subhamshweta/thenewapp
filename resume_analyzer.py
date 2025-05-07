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
    # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
    # do not change this unless explicitly requested by the user
    
    prompt = f"""Analyze the following resume for the role of {job_role}. 
    Identify strengths and weaknesses in terms of relevant skills, experience, formatting, and content.
    Return your analysis as JSON with the following structure:
    {{
        "strengths": ["strength1", "strength2", ...],
        "weaknesses": ["weakness1", "weakness2", ...],
        "missing_skills": ["skill1", "skill2", ...],
        "improvement_areas": ["area1", "area2", ...],
        "job_match_score": 0.0 to 1.0
    }}
    
    Resume:
    {resume_text}
    """
    
    try:
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are an expert resume analyzer and career coach."},
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
            "improvement_areas": [],
            "job_match_score": 0.0
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
    
    prompt = f"""Based on the following resume analysis for a {job_role} position, 
    provide specific, actionable improvement tips. Each tip should be concrete and specific.
    
    Analysis results:
    {json.dumps(analysis_results, indent=2)}
    
    Return a list of 5-7 detailed improvement tips formatted as a JSON array.
    """
    
    try:
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are an expert resume coach who gives actionable advice."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"}
        )
        
        improvement_tips = json.loads(response.choices[0].message.content)
        return improvement_tips.get("tips", [])
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
    # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
    # do not change this unless explicitly requested by the user
    
    prompt = f"""Rewrite the following resume to optimize it for a {job_role} position. 
    Address the weaknesses identified in the analysis, improve bullet points to be more 
    impactful with quantifiable achievements, and ensure the content is well-structured.
    
    Original resume:
    {resume_text}
    
    Analysis results:
    {json.dumps(analysis_results, indent=2)}
    
    Return your response in the following JSON format:
    {{
        "summary": "rewritten professional summary",
        "skills": "rewritten skills section",
        "experience": "rewritten experience section",
        "education": "rewritten education section",
        "full_optimized_resume": "the complete rewritten resume"
    }}
    """
    
    try:
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are an expert resume writer who creates impactful, achievement-oriented content."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"}
        )
        
        rewritten_sections = json.loads(response.choices[0].message.content)
        return rewritten_sections
    except Exception as e:
        print(f"Error rewriting resume sections: {e}")
        return {
            "summary": "Error rewriting summary section",
            "skills": "Error rewriting skills section",
            "experience": "Error rewriting experience section",
            "education": "Error rewriting education section",
            "full_optimized_resume": resume_text
        }
