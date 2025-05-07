import streamlit as st
import os
import base64
import tempfile
from io import BytesIO

from resume_analyzer import analyze_resume, generate_improvement_tips, rewrite_resume_sections
from resume_generator import generate_optimized_resume
from pdf_utils import extract_text_from_pdf, create_pdf

# Set up page configuration
st.set_page_config(
    page_title="AI Resume Enhancer",
    page_icon="📄",
    layout="wide"
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
if 'original_file_name' not in st.session_state:
    st.session_state.original_file_name = None

# Page header
st.title("AI Resume Enhancer")
st.markdown("""
Upload your resume and enter your target job role to get an AI-enhanced resume that's optimized for your job application!
""")

# Sidebar for inputs
with st.sidebar:
    st.header("Upload Your Resume")
    uploaded_file = st.file_uploader("Choose a PDF file", type=["pdf"])
    
    st.header("Enter Job Details")
    job_role = st.text_input("Target Job Role", placeholder="e.g., Software Engineer, Marketing Manager")
    
    if uploaded_file and job_role:
        if st.button("Analyze & Enhance Resume"):
            with st.spinner("Processing your resume..."):
                # Store the original filename
                st.session_state.original_file_name = uploaded_file.name
                
                # Extract text from PDF
                resume_text = extract_text_from_pdf(uploaded_file)
                st.session_state.resume_text = resume_text
                st.session_state.job_role = job_role
                
                # Analyze resume
                analysis_results = analyze_resume(resume_text, job_role)
                st.session_state.analysis_results = analysis_results
                
                # Generate improvement tips
                improvement_tips = generate_improvement_tips(analysis_results, job_role)
                st.session_state.improvement_tips = improvement_tips
                
                # Rewrite resume sections
                rewritten_sections = rewrite_resume_sections(resume_text, analysis_results, job_role)
                st.session_state.rewritten_sections = rewritten_sections
                
                # Generate optimized resume text
                optimized_resume_text = rewritten_sections['full_optimized_resume']
                st.session_state.optimized_resume_text = optimized_resume_text
                
                # Generate PDF
                optimized_resume_pdf = create_pdf(optimized_resume_text)
                st.session_state.optimized_resume_pdf = optimized_resume_pdf
                
                st.success("Resume analysis and enhancement complete!")
                st.rerun()

# Main content area
if st.session_state.resume_text and st.session_state.job_role:
    tabs = st.tabs(["Original Resume", "Analysis", "Enhanced Resume"])
    
    # Tab 1: Original Resume
    with tabs[0]:
        st.subheader("Your Original Resume")
        st.text_area("Original Content", st.session_state.resume_text, height=400, disabled=True)
    
    # Tab 2: Analysis
    with tabs[1]:
        st.subheader("Resume Analysis")
        
        if st.session_state.analysis_results:
            st.markdown("### Strengths")
            for strength in st.session_state.analysis_results.get('strengths', []):
                st.markdown(f"- {strength}")
            
            st.markdown("### Areas for Improvement")
            for weakness in st.session_state.analysis_results.get('weaknesses', []):
                st.markdown(f"- {weakness}")
            
            st.markdown("### Improvement Tips")
            for tip in st.session_state.improvement_tips:
                st.markdown(f"- {tip}")
    
    # Tab 3: Enhanced Resume
    with tabs[2]:
        st.subheader("Your Enhanced Resume")
        
        if st.session_state.optimized_resume_text:
            st.text_area("Enhanced Content", st.session_state.optimized_resume_text, height=400, disabled=True)
            
            # Download button for the enhanced resume
            if st.session_state.optimized_resume_pdf:
                # Create a download button for the PDF
                original_name = st.session_state.original_file_name
                if original_name:
                    # Remove .pdf extension if present and add _enhanced.pdf
                    if original_name.lower().endswith('.pdf'):
                        enhanced_filename = original_name[:-4] + "_enhanced.pdf"
                    else:
                        enhanced_filename = original_name + "_enhanced.pdf"
                else:
                    enhanced_filename = "enhanced_resume.pdf"
                
                st.download_button(
                    label="Download Enhanced Resume",
                    data=st.session_state.optimized_resume_pdf,
                    file_name=enhanced_filename,
                    mime="application/pdf"
                )
else:
    # Display instructions when no resume is uploaded
    st.info("👈 Please upload your resume and enter your target job role to get started.")
    
    # Show example of what the app does
    with st.expander("How it works"):
        st.markdown("""
        ### The AI Resume Enhancer will help you:
        
        1. **Analyze your existing resume** to identify strengths and weaknesses
        2. **Provide actionable improvement tips** based on your target job role
        3. **Rewrite bullet points and sections** to be more impactful
        4. **Generate an optimized resume** ready to download and submit
        
        Simply upload your PDF resume and specify the job you're targeting to get started!
        """)

# Footer
st.markdown("---")
st.markdown("AI Resume Enhancer - Powered by AI to help you land your dream job")
