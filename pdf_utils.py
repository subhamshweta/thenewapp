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
            
            # Clean the line of special characters that can't be encoded in latin-1
            cleaned_line = ""
            for char in line:
                if ord(char) < 256:  # Only include ASCII and extended ASCII characters
                    cleaned_line += char
                else:
                    # Replace common special characters with alternatives
                    if char == '–' or char == '—':  # en dash, em dash
                        cleaned_line += '-'
                    elif char == '"' or char == '"':  # curly quotes
                        cleaned_line += '"'
                    elif char == ''' or char == ''':  # curly apostrophes
                        cleaned_line += "'"
                    elif char == '•':  # bullet
                        cleaned_line += '*'
                    elif char == '…':  # ellipsis
                        cleaned_line += '...'
                    else:
                        cleaned_line += '?'  # Replace other non-latin1 chars with ?
            
            # Check if it's a heading (uppercase or ending with a colon)
            if cleaned_line.isupper() or cleaned_line.endswith(':'):
                pdf.set_font("Arial", 'B', 14)  # Bold, larger font
                pdf.cell(0, 10, cleaned_line, ln=True)
                pdf.set_font("Arial", size=12)  # Reset font
                continue
            
            # Wrap text to fit the page width
            wrapped_lines = textwrap.wrap(cleaned_line, width=90)  # Adjust width as needed
            
            for wrapped_line in wrapped_lines:
                pdf.cell(0, 7, wrapped_line, ln=True)
        
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
        
        # Create a simple error PDF if there's an error
        try:
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
            
        except Exception as inner_error:
            print(f"Error creating error PDF: {inner_error}")
            # Return a pre-generated empty PDF as last resort
            return b"%PDF-1.3\n1 0 obj\n<</Type/Catalog/Pages 2 0 R>>\nendobj\n2 0 obj\n<</Type/Pages/Kids[3 0 R]/Count 1>>\nendobj\n3 0 obj\n<</Type/Page/MediaBox[0 0 612 792]/Parent 2 0 R/Resources<<>>/Contents 4 0 R>>\nendobj\n4 0 obj\n<</Length 10>>\nstream\nBT\n/F1 12 Tf\nET\nendstream\nendobj\nxref\n0 5\n0000000000 65535 f \n0000000010 00000 n \n0000000053 00000 n \n0000000102 00000 n \n0000000194 00000 n \ntrailer\n<</Size 5/Root 1 0 R>>\nstartxref\n254\n%%EOF"
