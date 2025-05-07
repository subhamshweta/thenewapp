import os
import json
from openai import OpenAI

# Initialize OpenAI client
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
openai = OpenAI(api_key=OPENAI_API_KEY)

def generate_optimized_resume(resume_text, job_role, analysis_results, rewritten_sections):
    """
    Generate an optimized resume text based on the original, analysis, and rewritten sections.
    
    Args:
        resume_text (str): Original resume text
        job_role (str): Target job role
        analysis_results (dict): Analysis results from analyze_resume
        rewritten_sections (dict): Rewritten sections from rewrite_resume_sections
        
    Returns:
        str: The full optimized resume text
    """
    # If we already have a full optimized resume from rewritten_sections, return it
    if rewritten_sections and 'full_optimized_resume' in rewritten_sections:
        return rewritten_sections['full_optimized_resume']
    
    # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
    # do not change this unless explicitly requested by the user
    
    # If not, generate it separately
    prompt = f"""Generate a complete, optimized resume for a {job_role} position based on the following:
    
    Original resume:
    {resume_text}
    
    Analysis results:
    {json.dumps(analysis_results, indent=2)}
    
    Rewritten sections:
    {json.dumps(rewritten_sections, indent=2)}
    
    Create a professional, ATS-friendly resume that is well-formatted and emphasizes 
    the candidate's strengths while addressing the weaknesses identified in the analysis.
    Focus on quantifiable achievements and skills relevant to the {job_role} position.
    """
    
    try:
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are an expert resume writer who creates professional, ATS-friendly resumes."},
                {"role": "user", "content": prompt}
            ]
        )
        
        optimized_resume = response.choices[0].message.content
        return optimized_resume
    except Exception as e:
        print(f"Error generating optimized resume: {e}")
        
        # If there's an error, use the original text as fallback
        return resume_text
