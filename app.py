# app.py
import streamlit as st
import os
import base64
import tempfile
from io import BytesIO

from resume_analyzer import analyze_resume, generate_improvement_tips, rewrite_resume_sections
from resume_generator import generate_optimized_resume
from pdf_utils import extract_text_from_document, create_document

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
if 'optimized_resume_docx' not in st.session_state:
    st.session_state.optimized_resume_docx = None
if 'original_file_name' not in st.session_state:
    st.session_state.original_file_name = None
if 'processing_complete' not in st.session_state:
    st.session_state.processing_complete = False

try:
    from sample_resume import create_sample_resume
    SAMPLE_RESUME_AVAILABLE = True
except ImportError:
    SAMPLE_RESUME_AVAILABLE = False

st.title("🚀 AI Resume Enhancer")
st.markdown("""
<div style='text-align: center; padding: 10px; margin-bottom: 30px;'>
    <h3>Transform Your Resume Into an Interview-Winning Document</h3>
    <p>Upload your resume, enter your target job role, and let AI optimize it for your dream job!</p>
</div>
""", unsafe_allow_html=True)

if st.session_state.processing_complete:
    tabs = st.tabs(["Original Resume", "Analysis", "Enhanced Resume"])
    
    with tabs[0]:
        st.subheader("Your Original Resume")
        st.text_area("Original Content", st.session_state.resume_text, height=400, disabled=True)
    
    with tabs[1]:
        st.subheader("Resume Analysis")
        if st.session_state.analysis_results:
            job_match = st.session_state.analysis_results.get('job_match_score', 0) * 100
            st.markdown(f"#### Job Match Score: {job_match:.1f}%")
            st.progress(float(job_match/100))
            
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("### 💪 Strengths")
                for strength in st.session_state.analysis_results.get('strengths', []):
                    st.markdown(f"✓ {strength}")
            with col2:
                st.markdown("### 🔍 Areas for Improvement")
                for weakness in st.session_state.analysis_results.get('weaknesses', []):
                    st.markdown(f"→ {weakness}")
            
            st.markdown("### 📝 Weak Phrases to Improve")
            weak_phrases = st.session_state.analysis_results.get('weak_phrases', [])
            if weak_phrases:
                for phrase in weak_phrases:
                    with st.expander(f"Original: {phrase['phrase']}"):
                        st.markdown(f"**Suggestion:** {phrase['suggestion']}")
                        st.markdown(f"**Reason:** {phrase['reason']}")
            else:
                st.info("No weak phrases identified.")
            
            st.markdown("### 🔑 Missing Keywords")
            missing_keywords = st.session_state.analysis_results.get('missing_keywords', [])
            if missing_keywords:
                for keyword in missing_keywords:
                    with st.expander(f"{keyword['keyword']} ({keyword['importance']} importance)"):
                        st.markdown(f"**Suggestion:** {keyword['suggestion']}")
                        st.markdown(f"**Context:** {keyword['context']}")
            else:
                st.info("No missing keywords identified.")
            
            st.markdown("### 📊 Quantification Opportunities")
            quantification = st.session_state.analysis_results.get('quantification_opportunities', [])
            if quantification:
                for opp in quantification:
                    with st.expander(f"Current: {opp['current_text']}"):
                        st.markdown(f"**Suggestion:** {opp['suggestion']}")
                        st.markdown(f"**Reason:** {opp['reason']}")
            else:
                st.info("No quantification opportunities identified.")
            
            st.markdown("### 💡 Improvement Tips")
            if st.session_state.improvement_tips:
                for tip in st.session_state.improvement_tips:
                    st.markdown(f"• {tip}")
            else:
                st.markdown("• Focus on quantifiable achievements rather than just listing responsibilities.")
                st.markdown("• Tailor your resume to specifically highlight skills relevant to the target position.")
                st.markdown("• Ensure your resume is properly formatted and easy to scan.")
    
    with tabs[2]:
        st.subheader("Your Enhanced Resume")
        if st.session_state.optimized_resume_text:
            st.text_area("Enhanced Content", st.session_state.optimized_resume_text, height=400, disabled=True)
            
            col1, col2, col3 = st.columns(3)
            with col1:
                if st.session_state.optimized_resume_pdf:
                    original_name = st.session_state.original_file_name or "resume"
                    base_name = os.path.splitext(original_name)[0]
                    enhanced_filename = f"{base_name}_enhanced.pdf"
                    st.download_button(
                        label="⬇️ Download as PDF",
                        data=st.session_state.optimized_resume_pdf,
                        file_name=enhanced_filename,
                        mime="application/pdf",
                        help="Download your enhanced resume as a PDF file"
                    )
            with col2:
                if st.session_state.optimized_resume_docx:
                    original_name = st.session_state.original_file_name or "resume"
                    base_name = os.path.splitext(original_name)[0]
                    enhanced_filename = f"{base_name}_enhanced.docx"
                    st.download_button(
                        label="⬇️ Download as DOCX",
                        data=st.session_state.optimized_resume_docx,
                        file_name=enhanced_filename,
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                        help="Download your enhanced resume as a DOCX file"
                    )
            with col3:
                if st.session_state.optimized_resume_text:
                    original_name = st.session_state.original_file_name or "resume"
                    base_name = os.path.splitext(original_name)[0]
                    enhanced_filename = f"{base_name}_enhanced.txt"
                    st.download_button(
                        label="⬇️ Download as TXT",
                        data=st.session_state.optimized_resume_text.encode('utf-8'),
                        file_name=enhanced_filename,
                        mime="text/plain",
                        help="Download your enhanced resume as a text file"
                    )
            
            if st.button("Start Over with a New Resume"):
                for key in list(st.session_state.keys()):
                    del st.session_state[key]
                st.rerun()

else:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
        <div style='text-align: center; background-color: #f0f2f6; padding: 20px; border-radius: 10px; margin-bottom: 20px;'>
            <h2>📄 Upload Your Resume</h2>
        </div>
        """, unsafe_allow_html=True)
        
        use_sample = False
        if SAMPLE_RESUME_AVAILABLE:
            use_sample = st.checkbox("📋 Use sample résumé for testing", value=False)
        
        if not use_sample:
            uploaded_file = st.file_uploader("Choose a PDF or DOCX file", type=["pdf", "docx"])
            if uploaded_file:
                st.success(f"Uploaded: {uploaded_file.name}")
        else:
            uploaded_file = None
            st.info("Sample résumé will be used for demonstration purposes.")
            
        st.markdown("<h3 style='text-align: center; margin-top: 20px;'>🎯 Target Job Role</h3>", unsafe_allow_html=True)
        job_role = st.text_input("Target Job Role", placeholder="e.g., Software Engineer, Marketing Manager, Data Analyst", label_visibility="collapsed")
        
        process_resume = False
        if use_sample and job_role:
            if st.button("✨ Enhance Sample Résumé", help="Process the sample résumé for the specified job role", type="primary"):
                process_resume = True
                with st.spinner("Preparing sample résumé..."):
                    sample_resume_bytes = create_sample_resume()
                    sample_file = BytesIO(sample_resume_bytes)
                    sample_file.name = "sample_resume.pdf"
                    uploaded_file = sample_file
                    st.session_state.original_file_name = "sample_resume.pdf"
        
        elif uploaded_file and job_role:
            if st.button("✨ Enhance My Résumé", help="Process your résumé for the specified job role", type="primary"):
                process_resume = True
                st.session_state.original_file_name = uploaded_file.name
        
        elif not job_role and (uploaded_file or use_sample):
            st.warning("Please enter a target job role to continue.")
        elif not uploaded_file and not use_sample:
            st.info("Please upload your résumé to get started.")
        
        if process_resume:
            progress_text = "Analyzing and enhancing your résumé..."
            progress_bar = st.progress(0)
            
            progress_bar.progress(10, text=progress_text + " Extracting text...")
            try:
                resume_text = extract_text_from_document(uploaded_file)
            except Exception as e:
                st.error(f"Failed to extract text from résumé: {str(e)}")
                st.stop()
            st.session_state.resume_text = resume_text
            st.session_state.job_role = job_role
            
            progress_bar.progress(30, text=progress_text + " Analyzing résumé content...")
            analysis_results = analyze_resume(resume_text, job_role)
            st.session_state.analysis_results = analysis_results
            
            progress_bar.progress(50, text=progress_text + " Generating improvement tips...")
            improvement_tips = generate_improvement_tips(analysis_results, job_role)
            st.session_state.improvement_tips = improvement_tips
            
            progress_bar.progress(70, text=progress_text + " Rewriting résumé sections...")
            rewritten_sections = rewrite_resume_sections(resume_text, analysis_results, job_role)
            st.session_state.rewritten_sections = rewritten_sections
            
            progress_bar.progress(85, text=progress_text + " Finalizing enhanced résumé...")
            optimized_resume_text = rewritten_sections['full_optimized_resume']
            st.session_state.optimized_resume_text = optimized_resume_text
            
            progress_bar.progress(95, text=progress_text + " Creating documents...")
            try:
                st.session_state.optimized_resume_pdf = create_document(optimized_resume_text, 'pdf')
                st.session_state.optimized_resume_docx = create_document(optimized_resume_text, 'docx')
            except Exception as e:
                st.error(f"Failed to create output documents: {str(e)}")
                st.stop()
            
            progress_bar.progress(100, text="Enhancement complete!")
            st.session_state.processing_complete = True
            st.success("Résumé analysis and enhancement complete!")
            st.rerun()
    
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; margin: 20px 0;'>
        <h2>Why Enhance Your Résumé with AI?</h2>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
        ### 🔍 Expert Analysis
        Our AI identifies strengths and weaknesses in your résumé, comparing it against industry standards for your target role.
        """)
    with col2:
        st.markdown("""
        ### 📊 Tailored Content
        Get personalized recommendations and content optimized specifically for the job you're applying to.
        """)
    with col3:
        st.markdown("""
        ### ✅ ATS-Friendly
        Our enhanced résumés are designed to pass through Applicant Tracking Systems and catch the recruiter's eye.
        """)
    
    st.markdown("""
    <div style='text-align: center; margin-top: 40px;'>
        <h2>How It Works</h2>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown("""
        ### Step 1
        Upload your current résumé in PDF or DOCX format.
        """)
    with col2:
        st.markdown("""
        ### Step 2
        Enter the specific job role you're targeting.
        """)
    with col3:
        st.markdown("""
        ### Step 3
        AI analyzes your résumé and identifies improvements.
        """)
    with col4:
        st.markdown("""
        ### Step 4
        Download your enhanced, job-specific résumé.
        """)

st.markdown("---")
st.markdown("<div style='text-align: center;'>AI Résumé Enhancer - Powered by AI to help you land your dream job</div>", unsafe_allow_html=True)
