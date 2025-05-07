import PyPDF2
import io
from fpdf import FPDF
import tempfile
import textwrap

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

def create_pdf(resume_text):
    """
    Create a PDF document from the optimized resume text.
    
    Args:
        resume_text (str): The optimized resume text
        
    Returns:
        bytes: PDF file as bytes
    """
    try:
        # Initialize PDF object
        pdf = FPDF(orientation='P', unit='mm', format='A4')
        pdf.add_page()
        
        # Set font
        pdf.set_font("Arial", size=12)
        
        # Add margin
        margin = 15
        effective_width = pdf.w - 2 * margin
        pdf.set_margins(margin, margin, margin)
        
        # Process the text line by line
        lines = resume_text.split('\n')
        
        for line in lines:
            line = line.strip()
            
            # Skip empty lines
            if not line:
                pdf.ln(5)  # Add some space for empty lines
                continue
            
            # Check if it's a heading (uppercase or ending with a colon)
            if line.isupper() or line.endswith(':'):
                pdf.set_font("Arial", 'B', 14)  # Bold, larger font
                pdf.cell(0, 10, line, ln=True)
                pdf.set_font("Arial", size=12)  # Reset font
                continue
            
            # Wrap text to fit the page width
            wrapped_lines = textwrap.wrap(line, width=90)  # Adjust width as needed
            
            for wrapped_line in wrapped_lines:
                pdf.cell(0, 7, wrapped_line, ln=True)
        
        # Save PDF to a bytes buffer
        pdf_buffer = io.BytesIO()
        pdf.output(pdf_buffer)
        pdf_buffer.seek(0)
        
        return pdf_buffer.getvalue()
    
    except Exception as e:
        print(f"Error creating PDF: {e}")
        
        # Create a simple error PDF if there's an error
        error_pdf = FPDF()
        error_pdf.add_page()
        error_pdf.set_font("Arial", size=12)
        error_pdf.cell(0, 10, "Error creating optimized resume PDF", ln=True)
        error_pdf.cell(0, 10, f"Please try again or download the text version.", ln=True)
        
        error_buffer = io.BytesIO()
        error_pdf.output(error_buffer)
        error_buffer.seek(0)
        
        return error_buffer.getvalue()
