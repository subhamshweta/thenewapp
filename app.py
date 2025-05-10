# app.py
import streamlit as st
import os
import base64
import tempfile
from io import BytesIO
import logging
import difflib
import json

from resume_analyzer import analyze_resume, generate_improvement_tips, rewrite_resume_sections, extract_resume_details
from resume_generator import generate_optimized_resume
from pdf_utils import extract_text_from_document, create_document

# Set up logging
logging.basicConfig(filename='resume_enhancer.log', level=logging.DEBUG, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Custom CSS for Apple-inspired design
st.markdown("""
    <style>
    /* Reset default Streamlit styles */
    body {
        color: #000000;
        background-color: #FFFFFF;
        font-family: 'Helvetica Neue', Arial, sans-serif;
    }
    .stApp {
        background-color: #FFFFFF;
        max-width: 900px;
        margin: 0 auto;
        padding: 20px;
    }
    h1 {
        font-size: 36px;
        font-weight: 600;
        text-align: center;
        color: #000000;
        margin-bottom: 20px;
    }
    h2 {
        font-size: 24px;
        font-weight: 500;
        color: #000000;
        margin-top: 20px;
        margin-bottom: 10px;
    }
    h3 {
        font-size: 18px;
        font-weight: 500;
        color: #000000;
        margin-bottom: 8px;
    }
    p, label, .stTextInput, .stTextArea, .stFileUploader, .stButton button, .stDownloadButton button, .stTabs button {
        font-size: 16px;
        color: #000000;
        font-weight: 400;
    }
    .stTextArea textarea, .stTextInput input {
        background-color: #F5F5F5;
        border: 1px solid #E0E0E0;
        border-radius: 8px;
        padding: 10px;
        color: #000000;
    }
    .stTextArea textarea:disabled {
        background-color: #F0F0F0;
        color: #333333;
    }
    .stButton button, .stDownloadButton button {
        background-color: #000000;
        color: #FFFFFF;
        border: none;
        border-radius: 8px;
        padding: 10px 20px;
        font-weight: 500;
        transition: background-color 0.3s ease;
    }
    .stButton button:hover, .stDownloadButton button:hover {
        background-color: #333333;
    }
    .stFileUploader {
        border: 1px dashed #E0E0E0;
        border-radius: 8px;
        padding: 20px;
        text-align: center;
    }
    .stTabs [role="tablist"] {
        border-bottom: 1px solid #E0E0E0;
        margin-bottom: 20px;
    }
    .stTabs [role="tab"] {
        color: #000000;
        font-weight: 500;
        padding: 10px 20px;
        border-bottom: 2px solid transparent;
        transition: border-bottom 0.3s ease;
    }
    .stTabs [role="tab"][aria-selected="true"] {
        border-bottom: 2px solid #000000;
    }
    .stTabs [role="tab"]:hover {
        border-bottom: 2px solid #666666;
    }
    .stProgress > div > div {
        background-color: #000000;
    }
    .stWarning, .stError, .stInfo {
        background-color: #F5F5F5;
        border: 1px solid #E0E0E0;
        border-radius: 8px;
        color: #000000;
    }
    .stExpander {
        border: 1px solid #E0E0E0;
        border-radius: 8px;
        margin-bottom: 10px;
    }
    .stExpanderHeader {
        background-color: #F5F5F5;
        color: #000000;
        font-weight: 500;
    }
    .stCodeBlock {
        background-color: #F5F5F5;
        border: 1px solid #E0E0E0;
        border-radius: 8px;
        padding: 10px;
        font-size: 14px;
    }
    .stCheckbox label {
        color: #000000;
        font-size: 16px;
    }
    hr {
        border: 0;
        border-top: 1px solid #E0E0E0;
        margin: 20px 0;
    }
    /* Remove unnecessary Streamlit elements */
    [data-testid="stToolbar"] {
        display: none;
    }
    [data-testid="stDecoration"] {
        display: none;
    }
    footer {
        display: none;
    }
    </style>
""", unsafe_allow_html=True)

st.set_page_config(
    page_title="Resume Enhancer",
    page_icon="📄",
    layout="centered"
)

# Session state initialization
if 'resume_text' not in st.session_state:
    st.session_state.resume_text = None
if 'job_role' not in st.session_state:
    st.session_state.job_role = None
if 'analysis_results' not in st.session_state:
    st.session_state.analysis_results = None
if 'improvement_tips' not in st.session_state:
    st.session_state.improvement_tips = None
if 'rewritten_sections' not in st.session_state:
    st.session_state.rewritten_sections = None
if 'optimized_resume_text' not in st.session_state:
    st.session_state.optimized_resume_text = None
if 'optimized_resume_pdf' not in st.session_state:
    st.session_state.optimized_resume_pdf = None
if 'optimized_resume_docx' not in st.session_state:
    st.session_state.optimized_resume_docx = None
if 'original_file_name' not in st.session_state:
    st.session_state.original_file_name = None
if 'processing_complete' not in st.session_state:
    st.session_state.processing_complete = False
if 'parsing_warnings' not in st.session_state:
    st.session_state.parsing_warnings = []
if 'extracted_details' not in st.session_state:
    st.session_state.extracted_details = None

try:
    from sample_resume import create_sample_resume
    SAMPLE_RESUME_AVAILABLE = True
except ImportError:
    SAMPLE_RESUME_AVAILABLE = False

st.title("Resume Enhancer")

if st.session_state.processing_complete:
    tabs = st.tabs(["Original", "Analysis", "Enhanced", "Debug"])
    
    with tabs[0]:
        st.subheader("Original Resume")
        st.text_area("", st.session_state.resume_text, height=400, disabled=True, label_visibility="collapsed")
    
    with tabs[1]:
        st.subheader("Analysis")
        if st.session_state.analysis_results:
            job_match = st.session_state.analysis_results.get('job_match_score', 0) * 100
            st.markdown(f"#### Job Match Score: {job_match:.1f}%")
            st.progress(float(job_match/100))
            
            col1, col2 = st.columns(2, gap="medium")
            with col1:
                st.markdown("### Strengths")
                for strength in st.session_state.analysis_results.get('strengths', []):
                    st.markdown(f"• {strength}")
            with col2:
                st.markdown("### Areas for Improvement")
                for weakness in st.session_state.analysis_results.get('weaknesses', []):
                    st.markdown(f"• {weakness}")
            
            st.markdown("### Weak Phrases")
            weak_phrases = st.session_state.analysis_results.get('weak_phrases', [])
            if weak_phrases:
                for phrase in weak_phrases:
                    with st.expander(f"{phrase['phrase']}"):
                        st.markdown(f"**Suggestion:** {phrase['suggestion']}")
                        st.markdown(f"**Reason:** {phrase['reason']}")
            else:
                st.info("No weak phrases identified.")
            
            st.markdown("### Missing Keywords")
            missing_keywords = st.session_state.analysis_results.get('missing_keywords', [])
            if missing_keywords:
                for keyword in missing_keywords:
                    with st.expander(f"{keyword['keyword']} ({keyword['importance']})"):
                        st.markdown(f"**Suggestion:** {keyword['suggestion']}")
                        st.markdown(f"**Context:** {keyword['context']}")
            else:
                st.info("No missing keywords identified.")
            
            st.markdown("### Quantification Opportunities")
            quantification = st.session_state.analysis_results.get('quantification_opportunities', [])
            if quantification:
                for opp in quantification:
                    with st.expander(f"{opp['current_text']}"):
                        st.markdown(f"**Suggestion:** {opp['suggestion']}")
                        st.markdown(f"**Reason:** {opp['reason']}")
            else:
                st.info("No quantification opportunities identified.")
            
            st.markdown("### Improvement Tips")
            if st.session_state.improvement_tips:
                for tip in st.session_state.improvement_tips:
                    st.markdown(f"• {tip}")
            else:
                st.markdown("• Focus on quantifiable achievements.")
                st.markdown("• Tailor your resume for the role.")
                st.markdown("• Ensure proper formatting.")
    
    with tabs[2]:
        st.subheader("Enhanced Resume")
        if st.session_state.optimized_resume_text:
            st.text_area("", st.session_state.optimized_resume_text, height=400, disabled=True, label_visibility="collapsed")
            
            st.markdown("### Changes Made")
            diff = difflib.unified_diff(
                st.session_state.resume_text.splitlines(),
                st.session_state.optimized_resume_text.splitlines(),
                lineterm='',
                fromfile='Original Resume',
                tofile='Enhanced Resume'
            )
            diff_text = '\n'.join(diff)
            if diff_text:
                st.code(diff_text, language='diff')
            else:
                st.warning("No significant changes detected. Check the Analysis and Debug tabs.")
            
            if st.session_state.parsing_warnings:
                st.warning("Formatting issues detected. The PDF may not be fully structured.")
                for warning in st.session_state.parsing_warnings:
                    st.markdown(f"• {warning}")
            
            col1, col2, col3 = st.columns(3, gap="medium")
            with col1:
                if st.session_state.optimized_resume_pdf:
                    original_name = st.session_state.original_file_name or "resume"
                    base_name = os.path.splitext(original_name)[0]
                    enhanced_filename = f"{base_name}_enhanced.pdf"
                    st.download_button(
                        label="Download PDF",
                        data=st.session_state.optimized_resume_pdf,
                        file_name=enhanced_filename,
                        mime="application/pdf"
                    )
            with col2:
                if st.session_state.optimized_resume_docx:
                    original_name = st.session_state.original_file_name or "resume"
                    base_name = os.path.splitext(original_name)[0]
                    enhanced_filename = f"{base_name}_enhanced.docx"
                    st.download_button(
                        label="Download DOCX",
                        data=st.session_state.optimized_resume_docx,
                        file_name=enhanced_filename,
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                    )
            with col3:
                if st.session_state.optimized_resume_text:
                    original_name = st.session_state.original_file_name or "resume"
                    base_name = os.path.splitext(original_name)[0]
                    enhanced_filename = f"{base_name}_enhanced.txt"
                    st.download_button(
                        label="Download TXT",
                        data=st.session_state.optimized_resume_text.encode('utf-8'),
                        file_name=enhanced_filename,
                        mime="text/plain"
                    )
            
            if st.button("Start Over"):
                for key in list(st.session_state.keys()):
                    del st.session_state[key]
                st.rerun()

    with tabs[3]:
        st.subheader("Debug Info")
        st.markdown("### Extracted Details")
        if st.session_state.extracted_details:
            st.json(st.session_state.extracted_details)
        else:
            st.info("No extracted details available.")
        
        st.markdown("### Log Entries")
        try:
            with open('resume_enhancer.log', 'r') as log_file:
                log_content = log_file.read()
                errors = [line for line in log_content.split('\n') if 'ERROR' in line]
                if errors:
                    st.error("Errors found in the log:")
                    for error in errors:
                        st.markdown(f"• {error}")
                else:
                    st.info("No errors found.")
        except FileNotFoundError:
            st.error("Log file not found.")

else:
    use_sample = False
    if SAMPLE_RESUME_AVAILABLE:
        use_sample = st.checkbox("Use sample resume", value=False)
    
    if not use_sample:
        uploaded_file = st.file_uploader("Upload Resume (PDF or DOCX)", type=["pdf", "docx"], label_visibility="collapsed")
        if uploaded_file:
            st.success(f"Uploaded: {uploaded_file.name}")
    else:
        uploaded_file = None
        st.info("Using sample resume.")
    
    job_role = st.text_input("Target Job Role", placeholder="e.g., Digital Marketing", label_visibility="collapsed")
    
    process_resume = False
    if use_sample and job_role:
        if st.button("Enhance Sample Resume", type="primary"):
            process_resume = True
            with st.spinner("Processing..."):
                sample_resume_bytes = create_sample_resume()
                sample_file = BytesIO(sample_resume_bytes)
                sample_file.name = "sample_resume.pdf"
                uploaded_file = sample_file
                st.session_state.original_file_name = "sample_resume.pdf"
    
    elif uploaded_file and job_role:
        if st.button("Enhance Resume", type="primary"):
            process_resume = True
            st.session_state.original_file_name = uploaded_file.name
    
    elif not job_role and (uploaded_file or use_sample):
        st.warning("Please enter a target job role.")
    elif not uploaded_file and not use_sample:
        st.info("Please upload a resume.")
    
    if process_resume:
        progress_text = "Processing resume..."
        progress_bar = st.progress(0)
        
        progress_bar.progress(10, text=progress_text + " Extracting text...")
        try:
            resume_text = extract_text_from_document(uploaded_file)
            logging.debug(f"Extracted resume text:\n{resume_text}")
        except Exception as e:
            st.error(f"Failed to extract text: {str(e)}")
            logging.error(f"Text extraction failed: {e}")
            st.stop()
        st.session_state.resume_text = resume_text
        st.session_state.job_role = job_role
        
        progress_bar.progress(20, text=progress_text + " Extracting details...")
        st.session_state.extracted_details = extract_resume_details(resume_text)
        
        progress_bar.progress(30, text=progress_text + " Analyzing content...")
        analysis_results = analyze_resume(resume_text, job_role)
        st.session_state.analysis_results = analysis_results
        
        progress_bar.progress(50, text=progress_text + " Generating tips...")
        improvement_tips = generate_improvement_tips(analysis_results, job_role)
        st.session_state.improvement_tips = improvement_tips
        
        progress_bar.progress(70, text=progress_text + " Rewriting sections...")
        rewritten_sections = rewrite_resume_sections(resume_text, analysis_results, job_role)
        st.session_state.rewritten_sections = rewritten_sections
        
        progress_bar.progress(85, text=progress_text + " Finalizing resume...")
        optimized_resume_text = rewritten_sections['full_optimized_resume']
        st.session_state.optimized_resume_text = optimized_resume_text
        
        progress_bar.progress(95, text=progress_text + " Creating documents...")
        try:
            st.session_state.optimized_resume_pdf = create_document(optimized_resume_text, 'pdf')
            st.session_state.optimized_resume_docx = create_document(optimized_resume_text, 'docx')
            
            with open('resume_enhancer.log', 'r') as log_file:
                log_content = log_file.read()
                warnings = [line for line in log_content.split('\n') if 'WARNING' in line and 'section not found or empty' in line]
                st.session_state.parsing_warnings = warnings
        except Exception as e:
            st.error(f"Failed to create documents: {str(e)}")
            logging.error(f"Document creation failed: {e}")
            st.stop()
        
        progress_bar.progress(100, text="Complete!")
        st.session_state.processing_complete = True
        st.success("Resume enhanced successfully!")
        st.rerun()
