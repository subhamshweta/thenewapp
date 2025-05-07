from fpdf import FPDF
import io

def create_sample_resume():
    """
    Create a sample resume PDF for testing purposes.
    
    Returns:
        bytes: PDF file as bytes
    """
    # Initialize PDF object
    pdf = FPDF(orientation='P', unit='mm', format='A4')
    pdf.add_page()
    
    # Set font
    pdf.set_font("Arial", 'B', 16)
    
    # Add name and contact information
    pdf.cell(0, 10, "JOHN SMITH", ln=True, align='C')
    pdf.set_font("Arial", size=10)
    pdf.cell(0, 5, "123 Main Street, Anytown, CA 12345", ln=True, align='C')
    pdf.cell(0, 5, "Phone: (555) 123-4567 | Email: johnsmith@email.com", ln=True, align='C')
    pdf.cell(0, 5, "LinkedIn: linkedin.com/in/johnsmith", ln=True, align='C')
    pdf.ln(5)
    
    # Professional Summary
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, "PROFESSIONAL SUMMARY", ln=True)
    pdf.set_font("Arial", size=10)
    pdf.multi_cell(0, 5, "Results-driven professional with 5 years of experience in software development. Skilled in problem-solving and team collaboration. Looking to leverage my skills to contribute to a dynamic organization.")
    pdf.ln(5)
    
    # Skills
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, "SKILLS", ln=True)
    pdf.set_font("Arial", size=10)
    pdf.multi_cell(0, 5, "Programming Languages: Java, Python, JavaScript\nFrameworks: React, Spring Boot\nTools: Git, Docker, Jenkins\nSoft Skills: Communication, Teamwork, Problem-solving")
    pdf.ln(5)
    
    # Work Experience
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, "WORK EXPERIENCE", ln=True)
    
    # Job 1
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(0, 5, "Software Developer | ABC Company | Jan 2020 - Present", ln=True)
    pdf.set_font("Arial", size=10)
    pdf.multi_cell(0, 5, "- Developed and maintained web applications using React and Spring Boot\n- Collaborated with cross-functional teams to deliver high-quality software\n- Implemented unit tests to ensure code quality and reliability\n- Participated in code reviews and provided constructive feedback")
    pdf.ln(3)
    
    # Job 2
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(0, 5, "Junior Developer | XYZ Tech | Jun 2018 - Dec 2019", ln=True)
    pdf.set_font("Arial", size=10)
    pdf.multi_cell(0, 5, "- Assisted in the development of internal tools using Java and Python\n- Fixed bugs and improved application performance\n- Documented code and created user guides\n- Participated in daily stand-up meetings and sprint planning")
    pdf.ln(5)
    
    # Education
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, "EDUCATION", ln=True)
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(0, 5, "Bachelor of Science in Computer Science | State University | 2018", ln=True)
    pdf.set_font("Arial", size=10)
    pdf.multi_cell(0, 5, "- GPA: 3.6/4.0\n- Relevant Coursework: Data Structures, Algorithms, Web Development, Database Management\n- Senior Project: Developed a mobile application for campus navigation")
    pdf.ln(5)
    
    # Projects
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, "PROJECTS", ln=True)
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(0, 5, "Personal Portfolio Website", ln=True)
    pdf.set_font("Arial", size=10)
    pdf.multi_cell(0, 5, "- Designed and developed a personal portfolio website using HTML, CSS, and JavaScript\n- Implemented responsive design for mobile compatibility\n- Integrated contact form functionality using PHP")
    
    # Get PDF as bytes
    pdf_output = pdf.output(dest='S')
    if isinstance(pdf_output, str):
        pdf_bytes = pdf_output.encode('latin-1')
    else:
        pdf_bytes = pdf_output
    return pdf_bytes

if __name__ == "__main__":
    # Create the sample resume
    sample_resume = create_sample_resume()
    
    # Save it to a file
    with open("sample_resume.pdf", "wb") as f:
        f.write(sample_resume)
    
    print("Sample resume created successfully!")