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
        
        # Set margins
        margin = 20
        pdf.set_margins(margin, margin, margin)
        
        # Set default font
        pdf.set_font("Arial", size=11)
        
        # Process sections
        sections = parse_resume_sections(resume_text)
        
        # Add name and contact info if present
        if 'name' in sections:
            pdf.set_font("Arial", 'B', 16)
            pdf.cell(0, 10, sections['name'], ln=True, align='C')
            pdf.ln(2)
            
            if 'contact' in sections:
                pdf.set_font("Arial", size=10)
                contact_lines = sections['contact'].split('\n')
                for line in contact_lines:
                    if line.strip():
                        pdf.cell(0, 5, line.strip(), ln=True, align='C')
                pdf.ln(5)
        
        # Process each section
        for section_name, content in sections.items():
            if section_name in ['name', 'contact']:
                continue
                
            # Add section header
            pdf.set_font("Arial", 'B', 12)
            pdf.set_text_color(0, 0, 0)  # Black color
            pdf.cell(0, 8, section_name.upper(), ln=True)
            pdf.line(pdf.get_x(), pdf.get_y(), pdf.get_x() + 170, pdf.get_y())
            pdf.ln(3)
            
            # Reset font for content
            pdf.set_font("Arial", size=11)
            pdf.set_text_color(0, 0, 0)  # Black color
            
            # Process content based on section type
            if section_name.lower() in ['experience', 'work experience', 'employment']:
                process_experience_section(pdf, content)
            elif section_name.lower() in ['education', 'academic background']:
                process_education_section(pdf, content)
            elif section_name.lower() in ['skills', 'technical skills', 'core competencies']:
                process_skills_section(pdf, content)
            else:
                process_general_section(pdf, content)
            
            pdf.ln(5)
        
        # Save PDF to a bytes buffer
        pdf_output = pdf.output(dest='S')
        
        # Handle string or bytes output
        if isinstance(pdf_output, str):
            pdf_bytes = pdf_output.encode('latin-1')
        else:
            pdf_bytes = pdf_output
            
        return pdf_bytes
    
    except Exception as e:
        print(f"Error creating PDF: {e}")
        return create_error_document("PDF")

def parse_resume_sections(resume_text):
    """
    Parse resume text into sections.
    
    Args:
        resume_text (str): The resume text
        
    Returns:
        dict: Dictionary of sections and their content
    """
    sections = {}
    current_section = None
    current_content = []
    
    # Common section headers
    section_headers = [
        'PROFESSIONAL SUMMARY', 'SUMMARY', 'OBJECTIVE',
        'EXPERIENCE', 'WORK EXPERIENCE', 'EMPLOYMENT',
        'EDUCATION', 'ACADEMIC BACKGROUND',
        'SKILLS', 'TECHNICAL SKILLS', 'CORE COMPETENCIES',
        'PROJECTS', 'CERTIFICATIONS', 'ACHIEVEMENTS'
    ]
    
    # Split text into lines
    lines = resume_text.split('\n')
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Check if line is a section header
        is_header = False
        for header in section_headers:
            if line.upper() == header:
                if current_section:
                    sections[current_section] = '\n'.join(current_content)
                current_section = header
                current_content = []
                is_header = True
                break
        
        if not is_header:
            if not current_section:
                # If no section found yet, this might be name/contact info
                if len(sections) == 0:
                    current_section = 'name'
                else:
                    current_section = 'other'
            current_content.append(line)
    
    # Add the last section
    if current_section and current_content:
        sections[current_section] = '\n'.join(current_content)
    
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
            
            # Add a regular paragraph
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
    Could you create a simple error document when the main document creation failed?
    
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
