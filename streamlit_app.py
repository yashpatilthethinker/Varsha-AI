import streamlit as st
import google.generativeai as genai
from document_processor import DocumentProcessor
from gemini_integration import GeminiChat
import pandas as pd
import json
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure page
st.set_page_config(
    page_title="Varsha - AI Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Helper functions
def generate_chat_text():
    """Generate a well-formatted text version of chat history"""
    if not st.session_state.messages:
        return ""
    
    text_content = []
    text_content.append("=" * 50)
    text_content.append("🤖 VARSHA AI ASSISTANT - CHAT HISTORY")
    text_content.append("=" * 50)
    text_content.append(f"Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}")
    text_content.append(f"Total Messages: {len(st.session_state.messages)}")
    if st.session_state.documents:
        text_content.append(f"Documents Analyzed: {len(st.session_state.documents)}")
    text_content.append("=" * 50)
    text_content.append("")
    
    for i, message in enumerate(st.session_state.messages):
        role = message["role"]
        content = message["content"]
        
        if role == "user":
            text_content.append(f"👤 USER:")
        else:
            text_content.append(f"🤖 VARSHA:")
        
        text_content.append(content)
        text_content.append("-" * 30)
        text_content.append("")
    
    return "\n".join(text_content)

def generate_chat_pdf():
    """Generate a professionally formatted PDF of the chat history"""
    try:
        # Import PDF libraries only when needed
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.colors import HexColor
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
        from reportlab.lib.enums import TA_CENTER
        import io
        
        if not st.session_state.messages:
            return None
        
        # Create a BytesIO buffer
        buffer = io.BytesIO()
        
        # Create the PDF document
        doc = SimpleDocTemplate(buffer, pagesize=A4, 
                              rightMargin=72, leftMargin=72, 
                              topMargin=72, bottomMargin=18)
        
        # Define styles
        styles = getSampleStyleSheet()
        
        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=HexColor('#667eea')
        )
        
        user_style = ParagraphStyle(
            'UserMessage',
            parent=styles['Normal'],
            fontSize=11,
            spaceAfter=12,
            leftIndent=20,
            textColor=HexColor('#1f2937')
        )
        
        assistant_style = ParagraphStyle(
            'AssistantMessage',
            parent=styles['Normal'],
            fontSize=11,
            spaceAfter=12,
            leftIndent=20,
            textColor=HexColor('#2563eb')
        )
        
        # Build the story
        story = []
        
        # Title
        story.append(Paragraph("Varsha AI Assistant - Chat History", title_style))
        story.append(Spacer(1, 12))
        
        # Metadata
        timestamp = datetime.now().strftime("%B %d, %Y at %I:%M %p")
        story.append(Paragraph(f"<b>Generated:</b> {timestamp}", styles['Normal']))
        story.append(Paragraph(f"<b>Total Messages:</b> {len(st.session_state.messages)}", styles['Normal']))
        if st.session_state.documents:
            story.append(Paragraph(f"<b>Documents Analyzed:</b> {len(st.session_state.documents)}", styles['Normal']))
        story.append(Spacer(1, 20))
        
        # Add messages
        for i, message in enumerate(st.session_state.messages):
            role = message["role"]
            content = message["content"]
            
            # Clean content for PDF
            clean_content = content.replace('**', '').replace('*', '').replace('###', '').replace('##', '')
            
            if role == "user":
                story.append(Paragraph(f"USER: {clean_content}", user_style))
            else:
                story.append(Paragraph(f"VARSHA: {clean_content}", assistant_style))
            
            story.append(Spacer(1, 10))
        
        # Build PDF
        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()
        
    except ImportError:
        return None
    except Exception as e:
        return None

# Clean, modern CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    .stApp {
        font-family: 'Inter', sans-serif;
    }
    
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 15px;
        text-align: center;
        margin-bottom: 2rem;
        color: white;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    
    .main-title {
        font-size: 2.5rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }
    
    .main-subtitle {
        font-size: 1.1rem;
        opacity: 0.9;
        font-weight: 300;
    }
    
    .control-panel {
        background: white;
        border-radius: 15px;
        padding: 1.5rem;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        margin-bottom: 2rem;
        border: 1px solid #e1e5e9;
    }
    
    .upload-area {
        border: 2px dashed #667eea;
        border-radius: 15px;
        padding: 2rem;
        text-align: center;
        background: #f8f9ff;
        margin: 1rem 0;
        transition: all 0.3s ease;
    }
    
    .upload-area:hover {
        border-color: #764ba2;
        background: #f0f2ff;
    }
    
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }
    .stDeployButton { display: none; }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "documents" not in st.session_state:
    st.session_state.documents = {}
if "processed_content" not in st.session_state:
    st.session_state.processed_content = ""

# Initialize components
@st.cache_resource
def initialize_components():
    doc_processor = DocumentProcessor()
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        st.error("❌ GEMINI_API_KEY not found in environment variables!")
        st.stop()
    
    try:
        gemini_chat = GeminiChat(api_key)
        return doc_processor, gemini_chat
    except Exception as e:
        st.error(f"❌ Failed to initialize Gemini: {str(e)}")
        st.stop()

doc_processor, gemini_chat = initialize_components()

# Main Header
st.markdown("""
<div class="main-header">
    <div class="main-title">🤖 Varsha</div>
    <div class="main-subtitle">Your Intelligent AI Assistant</div>
</div>
""", unsafe_allow_html=True)

# Control Panel
with st.container():
    st.markdown('<div class="control-panel">', unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns([2, 2, 2, 1])
    
    with col1:
        st.markdown("**📁 Documents**")
        if st.session_state.documents:
            st.success(f"✅ {len(st.session_state.documents)} files loaded")
        else:
            st.info("📤 No documents uploaded")
    
    with col2:
        st.markdown("**🤖 AI Status**")
        st.success("✅ Varsha is ready!")
    
    with col3:
        st.markdown("**💬 Chat**")
        if st.session_state.messages:
            st.info(f"📝 {len(st.session_state.messages)} messages")
        else:
            st.info("👋 Start a conversation!")
    
    with col4:
        if st.button("🗑️ Clear", help="Clear chat history"):
            st.session_state.messages = []
            st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)

# Document Upload Section (Collapsible)
with st.expander("📁 Upload Documents (Optional)", expanded=False):
    st.markdown("""
    <div class="upload-area">
        <h4>📄 Drag & Drop Files Here</h4>
        <p>Upload documents for analysis, or just chat without any files!</p>
    </div>
    """, unsafe_allow_html=True)
    
    uploaded_files = st.file_uploader(
        "Choose files",
        accept_multiple_files=True,
        type=['pdf', 'docx', 'pptx', 'txt'],
        label_visibility="collapsed"
    )
    
    if uploaded_files:
        st.write(f"📄 **{len(uploaded_files)} file(s) selected:**")
        for file in uploaded_files:
            st.write(f"• {file.name} ({file.size // 1024} KB)")
        
        if st.button("🚀 Process Documents", type="primary"):
            with st.spinner("Processing documents..."):
                processed_docs = {}
                progress = st.progress(0)
                
                for i, file in enumerate(uploaded_files):
                    try:
                        extracted_text = doc_processor.process_file(file)
                        processed_docs[file.name] = {
                            'content': extracted_text,
                            'type': file.type,
                            'size': file.size,
                            'processed_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        }
                    except Exception as e:
                        st.error(f"Error processing {file.name}: {str(e)}")
                    
                    progress.progress((i + 1) / len(uploaded_files))
                
                st.session_state.documents.update(processed_docs)
                st.session_state.processed_content = "\n\n".join([doc['content'] for doc in processed_docs.values()])
                st.success("✅ Documents processed successfully!")

# Show conversation starters if no messages
if not st.session_state.messages:
    st.markdown("### 💡 Try asking:")
    
    suggestions = [
        "👋 Hello Varsha, how are you?",
        "🤔 What can you help me with?", 
        "🔬 Explain quantum computing simply",
        "✍️ Help me write a creative story",
        "📊 What's machine learning?",
        "🌍 Tell me about climate change"
    ]
    
    cols = st.columns(2)
    for i, suggestion in enumerate(suggestions):
        with cols[i % 2]:
            if st.button(suggestion, key=f"suggestion_{i}", use_container_width=True):
                # Automatically trigger the conversation
                st.session_state.auto_message = suggestion.split(" ", 1)[1] if " " in suggestion else suggestion

# Display chat messages
for i, message in enumerate(st.session_state.messages):
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Handle auto message from suggestions
if hasattr(st.session_state, 'auto_message'):
    prompt = st.session_state.auto_message
    del st.session_state.auto_message
    
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Generate response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                response = gemini_chat.intelligent_chat(prompt, st.session_state.processed_content)
                st.markdown(response)
                st.session_state.messages.append({"role": "assistant", "content": response})
                st.rerun()
            except Exception as e:
                error_msg = f"Sorry, I encountered an error: {str(e)}"
                st.error(error_msg)
                st.session_state.messages.append({"role": "assistant", "content": error_msg})

# Chat input
if prompt := st.chat_input("💬 Chat with Varsha - ask me anything!"):
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Generate response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                response = gemini_chat.intelligent_chat(prompt, st.session_state.processed_content)
                st.markdown(response)
                st.session_state.messages.append({"role": "assistant", "content": response})
            except Exception as e:
                error_msg = f"Sorry, I encountered an error: {str(e)}"
                st.error(error_msg)
                st.session_state.messages.append({"role": "assistant", "content": error_msg})

# Quick Actions (only show if there are messages)
if st.session_state.messages:
    st.markdown("---")
    st.markdown("### ⚡ Quick Actions")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("📊 Sentiment", use_container_width=True):
            if st.session_state.processed_content:
                with st.spinner("Analyzing..."):
                    sentiment = gemini_chat.analyze_sentiment(st.session_state.processed_content[:2000])
                    st.info(f"Sentiment: {sentiment.get('sentiment_category', 'Unknown')}")
    
    with col2:
        if st.button("📝 Summarize", use_container_width=True):
            if st.session_state.processed_content:
                with st.spinner("Summarizing..."):
                    summary = gemini_chat.summarize_document(st.session_state.processed_content)
                    st.session_state.messages.append({"role": "assistant", "content": f"**Summary:**\n\n{summary}"})
                    st.rerun()
    
    with col3:
        if st.button("🔑 Keywords", use_container_width=True):
            if st.session_state.processed_content:
                with st.spinner("Extracting..."):
                    keywords = gemini_chat.extract_key_information(st.session_state.processed_content, "keywords")
                    st.session_state.messages.append({"role": "assistant", "content": f"**Keywords:**\n\n{keywords}"})
                    st.rerun()
    
    with col4:
        if st.button("💾 Export", use_container_width=True):
            # Show export options in expander
            with st.expander("📥 Download Options", expanded=True):
                col_pdf, col_txt = st.columns(2)
                
                with col_pdf:
                    pdf_data = generate_chat_pdf()
                    if pdf_data:
                        st.download_button(
                            "📄 PDF Format",
                            pdf_data,
                            file_name=f"varsha_chat_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                            mime="application/pdf"
                        )
                    else:
                        st.info("Install 'reportlab' for PDF export")
                
                with col_txt:
                    chat_text = generate_chat_text()
                    st.download_button(
                        "📝 Text Format",
                        chat_text,
                        file_name=f"varsha_chat_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                        mime="text/plain"
                    )

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #6b7280; padding: 1rem;">
    <p>🤖 <strong>Varsha AI Assistant</strong> - Chat about anything, analyze documents, and more!</p>
</div>
""", unsafe_allow_html=True)