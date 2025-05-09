import PyPDF2
import io
from fpdf import FPDF
import tempfile
import textwrap
from docx import Document
import os
import re

def extract_text_from_document(file):
    """
    Extract text content from a PDF or DOCX file.
    
    Args:
        file: File object of the PDF or DOCX
        
    Returns:
        str: Extracted text from the document
    """
    try:
        # Get file extension
        file_extension = os.path.splitext(file.name)[1].lower()
        
        if file_extension == '.pdf':
            return extract_text_from_pdf(file)
        elif file_extension == '.docx':
            return extract_text_from_docx(file)
        else:
            raise ValueError(f"Unsupported file format: {file_extension}")
            
    except Exception as e:
        print(f"Error extracting text from document: {e}")
        return "Error extracting text from document"

def extract_text_from_pdf(pdf_file):
    """
    Extract text content from a PDF file.
    
    Args:
        pdf_file: File object of the PDF
        
    Returns:
        str: Extracted text from the PDF
    """
    try:
        # Create a PDF reader object
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        
        # Extract text from each page
        text = ""
        for page_num in range(len(pdf_reader.pages)):
            page = pdf_reader.pages[page_num]
            text += page.extract_text()
        
        return text
    except Exception as e:
        print(f"Error extracting text from PDF: {e}")
        return "Error extracting text from PDF"

def extract_text_from_docx(docx_file):
    """
    Extract text content from a DOCX file.
    
    Args:
        docx_file: File object of the DOCX
        
    Returns:
        str: Extracted text from the DOCX
    """
    try:
        # Create a Document object
        doc = Document(docx_file)
        
        # Extract text from paragraphs
        text = ""
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
            
        # Extract text from tables
        for table in doc.tables:
            for row in table.rows:
                for cell in row.cells:
                    text += cell.text + "\n"
        
        return text
    except Exception as e:
        print(f"Error extracting text from DOCX: {e}")
        return "Error extracting text from DOCX"

def create_document(resume_text, output_format='pdf'):
    """
    Create a PDF or DOCX document from the optimized resume text.
    
    Args:
        resume_text (str): The optimized resume text
        output_format (str): 'pdf' or 'docx'
        
    Returns:
        bytes: Document file as bytes
    """
    if output_format.lower() == 'pdf':
        return create_pdf(resume_text)
    elif output_format.lower() == 'docx':
        return create_docx(resume_text)
    else:
        raise ValueError(f"Unsupported output format: {output_format}")

def create_pdf(resume_text):
    """
    Create a professionally formatted PDF document from the optimized resume text.
    
    Args:
        resume_text (str): The optimized resume text
        
    Returns:
        bytes: PDF file as bytes
    """
    try:
        # Initialize PDF object with A4 format
        pdf = FPDF(orientation='P', unit='mm', format='A4')
        pdf.add_page()
        
        # Set margins (1 inch = 25.4 mm)
        margin = 25.4
        pdf.set_margins(margin, margin, margin)
        
        # Set default font
        pdf.set_font("Arial", size=11)
        
        # Process sections
        sections = parse_markdown_resume(resume_text)
        
        # Add name and contact information
        if 'name' in sections:
            pdf.set_font("Arial", 'B', 16)
            pdf.cell(0, 10, sections['name'].upper(), ln=True, align='C')
            pdf.set_font("Arial", size=10)
            
            # Add contact information
            if 'contact' in sections:
                contact_info = sections['contact']
                for line in contact_info.split('\n'):
                    if line.strip():
                        pdf.cell(0, 5, line.strip(), ln=True, align='C')
            pdf.ln(5)
        
        # Add professional summary
        if 'summary' in sections:
            pdf.set_font("Arial", 'B', 12)
            pdf.cell(0, 10, "PROFESSIONAL SUMMARY", ln=True)
            pdf.set_font("Arial", size=10)
            pdf.multi_cell(0, 5, sections['summary'])
            pdf.ln(5)
        
        # Add skills section
        if 'skills' in sections:
            pdf.set_font("Arial", 'B', 12)
            pdf.cell(0, 10, "SKILLS", ln=True)
            pdf.set_font("Arial", size=10)
            
            # Process skills into categories if they exist
            skills_text = sections['skills']
            if ':' in skills_text:  # If skills are categorized
                categories = skills_text.split('\n')
                for category in categories:
                    if category.strip():
                        pdf.set_font("Arial", 'B', 10)
                        category_name = category.split(':')[0].strip()
                        pdf.cell(0, 5, f"{category_name}:", ln=True)
                        pdf.set_font("Arial", size=10)
                        skills = category.split(':')[1].strip()
                        pdf.multi_cell(0, 5, skills)
            else:
                pdf.multi_cell(0, 5, skills_text)
            pdf.ln(5)
        
        # Add experience section
        if 'experience' in sections:
            pdf.set_font("Arial", 'B', 12)
            pdf.cell(0, 10, "PROFESSIONAL EXPERIENCE", ln=True)
            
            # Process each job entry
            jobs = sections['experience'].split('\n\n')
            for job in jobs:
                if job.strip():
                    # Split job into header and details
                    job_parts = job.split('\n', 1)
                    if len(job_parts) > 1:
                        # Add job header
                        pdf.set_font("Arial", 'B', 10)
                        pdf.cell(0, 5, job_parts[0].strip(), ln=True)
                        
                        # Add job details
                        pdf.set_font("Arial", size=10)
                        details = job_parts[1].strip()
                        for line in details.split('\n'):
                            if line.strip():
                                # Check if line starts with bullet point
                                if line.strip().startswith('•'):
                                    pdf.multi_cell(0, 5, line.strip())
                                else:
                                    pdf.multi_cell(0, 5, line.strip())
                    pdf.ln(3)
        
        # Add education section
        if 'education' in sections:
            pdf.set_font("Arial", 'B', 12)
            pdf.cell(0, 10, "EDUCATION", ln=True)
            
            # Process each education entry
            edu_entries = sections['education'].split('\n\n')
            for entry in edu_entries:
                if entry.strip():
                    # Split entry into header and details
                    entry_parts = entry.split('\n', 1)
                    if len(entry_parts) > 1:
                        # Add education header
                        pdf.set_font("Arial", 'B', 10)
                        pdf.cell(0, 5, entry_parts[0].strip(), ln=True)
                        
                        # Add education details
                        pdf.set_font("Arial", size=10)
                        details = entry_parts[1].strip()
                        for line in details.split('\n'):
                            if line.strip():
                                pdf.multi_cell(0, 5, line.strip())
                    pdf.ln(3)
        
        # Add additional sections (certifications, projects, etc.)
        for section_name in ['certifications', 'projects', 'awards', 'publications']:
            if section_name in sections:
                pdf.set_font("Arial", 'B', 12)
                pdf.cell(0, 10, section_name.upper(), ln=True)
                pdf.set_font("Arial", size=10)
                pdf.multi_cell(0, 5, sections[section_name])
                pdf.ln(5)
        
        # Get PDF as bytes
        pdf_output = pdf.output(dest='S')
        if isinstance(pdf_output, str):
            pdf_bytes = pdf_output.encode('latin-1')
        else:
            pdf_bytes = pdf_output
        return pdf_bytes
    except Exception as e:
        print(f"Error creating PDF: {e}")
        return None

def parse_markdown_resume(markdown_text):
    """
    Parse a markdown-formatted resume into sections based on strict headers.
    Args:
        markdown_text (str): The markdown-formatted resume
    Returns:
        dict: Dictionary of sections
    """
    sections = {}
    current_section = None
    current_content = []
    lines = markdown_text.split('\n')
    for line in lines:
        line = line.strip()
        if re.match(r'^#\s+NAME', line, re.IGNORECASE):
            if current_section:
                sections[current_section] = '\n'.join(current_content).strip()
            current_section = 'name'
            current_content = []
        elif re.match(r'^#\s+CONTACT', line, re.IGNORECASE):
            if current_section:
                sections[current_section] = '\n'.join(current_content).strip()
            current_section = 'contact'
            current_content = []
        elif re.match(r'^#\s+PROFESSIONAL SUMMARY', line, re.IGNORECASE):
            if current_section:
                sections[current_section] = '\n'.join(current_content).strip()
            current_section = 'summary'
            current_content = []
        elif re.match(r'^#\s+SKILLS', line, re.IGNORECASE):
            if current_section:
                sections[current_section] = '\n'.join(current_content).strip()
            current_section = 'skills'
            current_content = []
        elif re.match(r'^#\s+PROFESSIONAL EXPERIENCE', line, re.IGNORECASE):
            if current_section:
                sections[current_section] = '\n'.join(current_content).strip()
            current_section = 'experience'
            current_content = []
        elif re.match(r'^#\s+EDUCATION', line, re.IGNORECASE):
            if current_section:
                sections[current_section] = '\n'.join(current_content).strip()
            current_section = 'education'
            current_content = []
        elif re.match(r'^#\s+CERTIFICATIONS', line, re.IGNORECASE):
            if current_section:
                sections[current_section] = '\n'.join(current_content).strip()
            current_section = 'certifications'
            current_content = []
        elif re.match(r'^#\s+PROJECTS', line, re.IGNORECASE):
            if current_section:
                sections[current_section] = '\n'.join(current_content).strip()
            current_section = 'projects'
            current_content = []
        elif re.match(r'^#\s+HOBBIES\s*&\s*INTERESTS', line, re.IGNORECASE):
            if current_section:
                sections[current_section] = '\n'.join(current_content).strip()
            current_section = 'hobbies_interests'
            current_content = []
        elif re.match(r'^##\s+', line):
            # Subsection (e.g., job title in experience)
            current_content.append(line)
        else:
            current_content.append(line)
    if current_section:
        sections[current_section] = '\n'.join(current_content).strip()
    return sections

def process_experience_section(pdf, content):
    """Process experience section with proper formatting."""
    entries = content.split('\n\n')
    for entry in entries:
        lines = entry.split('\n')
        if not lines:
            continue
            
        # First line is usually the title/company
        pdf.set_font("Arial", 'B', 11)
        pdf.cell(0, 6, lines[0], ln=True)
        
        # Second line is usually the date/location
        if len(lines) > 1:
            pdf.set_font("Arial", 'I', 10)
            pdf.cell(0, 5, lines[1], ln=True)
        
        # Remaining lines are bullet points
        pdf.set_font("Arial", size=10)
        for line in lines[2:]:
            if line.strip():
                # Handle bullet points
                if line.strip().startswith('•') or line.strip().startswith('-'):
                    line = line.strip()[1:].strip()
                wrapped_lines = textwrap.wrap(line, width=80)
                for i, wrapped_line in enumerate(wrapped_lines):
                    if i == 0:
                        pdf.cell(5, 5, '•', ln=0)
                        pdf.cell(0, 5, wrapped_line, ln=True)
                    else:
                        pdf.cell(10, 5, wrapped_line, ln=True)
        
        pdf.ln(3)

def process_education_section(pdf, content):
    """Process education section with proper formatting."""
    entries = content.split('\n\n')
    for entry in entries:
        lines = entry.split('\n')
        if not lines:
            continue
            
        # First line is usually the degree/school
        pdf.set_font("Arial", 'B', 11)
        pdf.cell(0, 6, lines[0], ln=True)
        
        # Second line is usually the date/location
        if len(lines) > 1:
            pdf.set_font("Arial", 'I', 10)
            pdf.cell(0, 5, lines[1], ln=True)
        
        # Remaining lines are details
        pdf.set_font("Arial", size=10)
        for line in lines[2:]:
            if line.strip():
                wrapped_lines = textwrap.wrap(line, width=80)
                for wrapped_line in wrapped_lines:
                    pdf.cell(0, 5, wrapped_line, ln=True)
        
        pdf.ln(3)

def process_skills_section(pdf, content):
    """Process skills section with proper formatting."""
    # Split skills into categories if they exist
    categories = content.split('\n\n')
    for category in categories:
        lines = category.split('\n')
        if not lines:
            continue
            
        # First line might be a category header
        if len(lines) > 1 and ':' in lines[0]:
            pdf.set_font("Arial", 'B', 11)
            pdf.cell(0, 6, lines[0], ln=True)
            skills = lines[1:]
        else:
            skills = lines
        
        # Process skills
        pdf.set_font("Arial", size=10)
        skills_text = ' | '.join(skill.strip() for skill in skills if skill.strip())
        wrapped_lines = textwrap.wrap(skills_text, width=80)
        for wrapped_line in wrapped_lines:
            pdf.cell(0, 5, wrapped_line, ln=True)
        
        pdf.ln(3)

def process_general_section(pdf, content):
    """Process general section with proper formatting."""
    lines = content.split('\n')
    pdf.set_font("Arial", size=10)
    
    for line in lines:
        if line.strip():
            wrapped_lines = textwrap.wrap(line, width=80)
            for wrapped_line in wrapped_lines:
                pdf.cell(0, 5, wrapped_line, ln=True)
    
    pdf.ln(3)

def create_docx(resume_text):
    """
    Create a DOCX document from the optimized resume text.
    
    Args:
        resume_text (str): The optimized resume text
        
    Returns:
        bytes: DOCX file as bytes
    """
    try:
        # Create a new Document
        doc = Document()
        
        # Process the text line by line
        lines = resume_text.split('\n')
        
        for line in lines:
            line = line.strip()
            
            # Skip empty lines
            if not line:
                doc.add_paragraph()
                continue
            
            # Check if it's a heading (uppercase or ending with a colon)
            if line.isupper() or line.endswith(':'):
                heading = doc.add_heading(line, level=1)
                continue
            
            # Add regular paragraph
            doc.add_paragraph(line)
        
        # Save DOCX to a bytes buffer
        docx_bytes = io.BytesIO()
        doc.save(docx_bytes)
        docx_bytes.seek(0)
        
        return docx_bytes.getvalue()
    
    except Exception as e:
        print(f"Error creating DOCX: {e}")
        return create_error_document("DOCX")

def create_error_document(format_type):
    """
    Create a simple error document when the main document creation fails.
    
    Args:
        format_type (str): 'PDF' or 'DOCX'
        
    Returns:
        bytes: Error document as bytes
    """
    try:
        if format_type.upper() == 'PDF':
            error_pdf = FPDF()
            error_pdf.add_page()
            error_pdf.set_font("Arial", size=12)
            error_pdf.cell(0, 10, "Error creating optimized resume PDF", ln=True)
            error_pdf.cell(0, 10, "Please try again or download the text version.", ln=True)
            
            error_output = error_pdf.output(dest='S')
            if isinstance(error_output, str):
                error_bytes = error_output.encode('latin-1')
            else:
                error_bytes = error_output
                
            return error_bytes
            
        elif format_type.upper() == 'DOCX':
            error_doc = Document()
            error_doc.add_heading("Error creating optimized resume DOCX", 0)
            error_doc.add_paragraph("Please try again or download the text version.")
            
            error_bytes = io.BytesIO()
            error_doc.save(error_bytes)
            error_bytes.seek(0)
            
            return error_bytes.getvalue()
            
    except Exception as e:
        print(f"Error creating error document: {e}")
        return b"" 
