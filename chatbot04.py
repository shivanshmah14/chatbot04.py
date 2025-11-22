import streamlit as st
import uuid
import os
import requests
import tempfile
import json
from pathlib import Path
from datetime import datetime
import io

# Optional imports
try:
    from gtts import gTTS
    TTS_AVAILABLE = True
except ImportError:
    TTS_AVAILABLE = False

try:
    import PyPDF2
    PDF_SUPPORT = True
except ImportError:
    PDF_SUPPORT = False

try:
    from docx import Document
    DOCX_SUPPORT = True
except ImportError:
    DOCX_SUPPORT = False

try:
    from pptx import Presentation
    PPTX_SUPPORT = True
except ImportError:
    PPTX_SUPPORT = False

try:
    import openpyxl
    import pandas as pd
    EXCEL_SUPPORT = True
except ImportError:
    EXCEL_SUPPORT = False

try:
    from PIL import Image
    import pytesseract
    OCR_SUPPORT = True
except ImportError:
    OCR_SUPPORT = False

# ----------------------
# Streamlit UI Setup
# ----------------------
st.set_page_config(
    page_title="Shiva AI",
    layout="wide",
    page_icon="🤖",
    initial_sidebar_state="expanded"
)

# ----------------------
# Custom CSS for White Theme (COMPREHENSIVE)
# ----------------------
st.markdown("""
<style>
    /* Force light mode EVERYWHERE - Nuclear option */
    * {
        color: black !important;
    }
    
    body, .stApp, .main, .block-container, section, .element-container {
        background-color: white !important;
        color: black !important;
    }
    
    /* All possible text elements */
    p, span, div, label, h1, h2, h3, h4, h5, h6, li, a, strong, em, code, pre {
        color: black !important;
    }
    
    /* Markdown content */
    .stMarkdown, .stMarkdown p, .stMarkdown span, .stMarkdown div {
        color: black !important;
    }
    
    /* Force sidebar light background */
    [data-testid="stSidebar"], [data-testid="stSidebar"] > div {
        background-color: #f8f9fa !important;
        color: black !important;
    }
    
    /* All sidebar content */
    [data-testid="stSidebar"] * {
        color: black !important;
    }
    
    /* Buttons everywhere */
    .stButton>button, button {
        background-color: white !important;
        color: black !important;
        border: 1px solid #ddd !important;
    }
    
    .stButton>button:hover, button:hover {
        background-color: #f0f0f0 !important;
    }
    
    /* All inputs and textareas */
    input, textarea, select {
        background-color: white !important;
        color: black !important;
        border: 1px solid #ddd !important;
    }
    
    /* Sidebar buttons specific */
    [data-testid="stSidebar"] .stButton button {
        width: 100%;
        background-color: white !important;
        color: black !important;
        border: 1px solid #ddd !important;
        border-radius: 8px;
        padding: 10px;
        margin: 2px 0;
    }
    
    [data-testid="stSidebar"] .stButton button:hover {
        background-color: #f0f0f0 !important;
    }
    
    /* Expander */
    .streamlit-expanderHeader, .streamlit-expanderContent {
        background-color: white !important;
        color: black !important;
    }
    
    /* Code blocks */
    code, pre {
        background-color: #f5f5f5 !important;
        color: black !important;
    }
    
    /* Welcome screen */
    .welcome-container {
        display: flex;
        justify-content: center;
        align-items: center;
        height: 60vh;
        background-color: white !important;
    }
    
    .welcome-title {
        font-size: 2.5rem;
        font-weight: 300;
        color: black !important;
        text-align: center;
    }
    
    /* Chat messages */
    .stChatMessage {
        background-color: white !important;
        color: black !important;
        border: 1px solid #e0e0e0 !important;
        border-radius: 12px;
        padding: 15px;
        margin: 10px 0;
    }
    
    .stChatMessage * {
        color: black !important;
    }
    
    /* Chat input */
    .stChatInput, .stChatInput input {
        background-color: white !important;
        color: black !important;
        border: 1px solid #ddd !important;
    }
    
    /* File uploader */
    .uploadedFile, [data-testid="stFileUploader"] {
        background-color: #f8f9fa !important;
        color: black !important;
        border: 1px solid #ddd !important;
        border-radius: 8px;
    }
    
    [data-testid="stFileUploader"] * {
        color: black !important;
    }
    
    /* Spinners and loading indicators */
    .stSpinner > div {
        border-color: black !important;
    }
    
    /* Toast notifications */
    .stToast {
        background-color: white !important;
        color: black !important;
    }
    
    /* Headers */
    header, [data-testid="stHeader"] {
        background-color: white !important;
    }
    
    /* Footer */
    footer {
        background-color: white !important;
        color: black !important;
    }
    
    /* Columns */
    [data-testid="column"] {
        background-color: white !important;
    }
    
    /* Remove any dark mode artifacts */
    [data-theme="dark"] {
        display: none !important;
    }
</style>
""", unsafe_allow_html=True)

# ----------------------
# Configuration
# ----------------------
API_KEY = os.getenv("CHATBOT_API_KEY", "sk_h4gsam68_z6e2xo8u9aaleUaBshwjVyDk")
MODEL = "sarvam-m"
SYSTEM_PROMPT = (
    "You are Shiva AI, an advanced intelligent assistant. "
    "Provide helpful, accurate, and detailed responses. "
    "When files are provided, analyze them thoroughly and reference specific details. "
    "Be professional, clear, and comprehensive in your answers."
)

# ----------------------
# Session State Initialization
# ----------------------
if "chat_sessions" not in st.session_state:
    st.session_state.chat_sessions = {}

if "current_session_id" not in st.session_state:
    st.session_state.current_session_id = str(uuid.uuid4())
    st.session_state.chat_sessions[st.session_state.current_session_id] = {
        "messages": [{"role": "system", "content": SYSTEM_PROMPT}],
        "files": [],
        "title": "New Chat",
        "created": datetime.now().strftime("%Y-%m-%d %H:%M")
    }

if "last_processed_files" not in st.session_state:
    st.session_state.last_processed_files = []

# ----------------------
# Helper Functions
# ----------------------
def extract_text_from_pdf(file_bytes):
    """Extract text from PDF"""
    try:
        pdf = PyPDF2.PdfReader(io.BytesIO(file_bytes))
        text = []
        for page in pdf.pages:
            text.append(page.extract_text())
        return "\n".join(text)
    except Exception as e:
        return f"Error reading PDF: {e}"

def extract_text_from_docx(file_bytes):
    """Extract text from Word document"""
    try:
        doc = Document(io.BytesIO(file_bytes))
        text = []
        for paragraph in doc.paragraphs:
            text.append(paragraph.text)
        # Also extract text from tables
        for table in doc.tables:
            for row in table.rows:
                for cell in row.cells:
                    text.append(cell.text)
        return "\n".join(text)
    except Exception as e:
        return f"Error reading DOCX: {e}"

def extract_text_from_pptx(file_bytes):
    """Extract text from PowerPoint"""
    try:
        prs = Presentation(io.BytesIO(file_bytes))
        text = []
        for slide_num, slide in enumerate(prs.slides, 1):
            text.append(f"\n--- Slide {slide_num} ---")
            for shape in slide.shapes:
                if hasattr(shape, "text"):
                    text.append(shape.text)
        return "\n".join(text)
    except Exception as e:
        return f"Error reading PPTX: {e}"

def extract_text_from_excel(file_bytes):
    """Extract text from Excel"""
    try:
        # Try reading with pandas
        df_dict = pd.read_excel(io.BytesIO(file_bytes), sheet_name=None)
        text = []
        for sheet_name, df in df_dict.items():
            text.append(f"\n--- Sheet: {sheet_name} ---")
            text.append(df.to_string())
        return "\n".join(text)
    except Exception as e:
        return f"Error reading Excel: {e}"

def extract_text_from_image(file_bytes):
    """Extract text from image using OCR"""
    try:
        image = Image.open(io.BytesIO(file_bytes))
        text = pytesseract.image_to_string(image)
        return text if text.strip() else "No text detected in image"
    except Exception as e:
        return f"Image uploaded (OCR not available): {e}"

@st.cache_data
def extract_file_content(file_bytes, filename):
    """Extract text content from various file types"""
    ext = Path(filename).suffix.lower()
    
    try:
        # PDF files
        if ext == '.pdf' and PDF_SUPPORT:
            return extract_text_from_pdf(file_bytes)
        
        # Word documents
        elif ext in ['.docx', '.doc'] and DOCX_SUPPORT:
            return extract_text_from_docx(file_bytes)
        
        # PowerPoint presentations
        elif ext in ['.pptx', '.ppt'] and PPTX_SUPPORT:
            return extract_text_from_pptx(file_bytes)
        
        # Excel files
        elif ext in ['.xlsx', '.xls'] and EXCEL_SUPPORT:
            return extract_text_from_excel(file_bytes)
        
        # Image files
        elif ext in ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff'] and OCR_SUPPORT:
            return extract_text_from_image(file_bytes)
        
        # Text-based files
        elif ext == '.txt':
            return file_bytes.decode('utf-8')
        
        # JSON files
        elif ext == '.json':
            return json.dumps(json.loads(file_bytes.decode('utf-8')), indent=2)
        
        # Code and markup files
        elif ext in ['.csv', '.py', '.md', '.html', '.css', '.js', '.xml', '.yaml', '.yml']:
            return file_bytes.decode('utf-8')
        
        # Try to decode as text for any other file
        else:
            try:
                return file_bytes.decode('utf-8', errors='ignore')
            except:
                return f"Binary file uploaded: {filename} ({format_file_size(len(file_bytes))})"
    
    except Exception as e:
        return f"Error reading {filename}: {str(e)}"

def format_file_size(size_bytes):
    """Format file size in human-readable format"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"

def speak_text(text):
    """Convert text to speech using gTTS"""
    if not TTS_AVAILABLE:
        return None
    try:
        tts = gTTS(text[:500], lang="en")
        audio_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
        tts.save(audio_file.name)
        return audio_file.name
    except:
        return None

def generate_chat_title(msg):
    """Generate a short title from the first message"""
    return msg[:50] + ("..." if len(msg) > 50 else "")

def get_current_session():
    """Get the currently active chat session"""
    return st.session_state.chat_sessions[st.session_state.current_session_id]

def create_new_chat():
    """Create a new chat session"""
    new_id = str(uuid.uuid4())
    st.session_state.chat_sessions[new_id] = {
        "messages": [{"role": "system", "content": SYSTEM_PROMPT}],
        "files": [],
        "title": "New Chat",
        "created": datetime.now().strftime("%Y-%m-%d %H:%M")
    }
    st.session_state.current_session_id = new_id
    st.session_state.last_processed_files = []

def delete_chat(session_id):
    """Delete a chat session if not the last one"""
    if len(st.session_state.chat_sessions) > 1:
        del st.session_state.chat_sessions[session_id]
        if session_id == st.session_state.current_session_id:
            st.session_state.current_session_id = list(st.session_state.chat_sessions.keys())[0]
        return True
    return False

def remove_file(filename):
    """Remove a file from the current session"""
    current_session = get_current_session()
    current_session["files"] = [f for f in current_session["files"] if f['filename'] != filename]

def get_file_icon(ext):
    """Get appropriate icon for file type"""
    icons = {
        '.pdf': '📕',
        '.doc': '📘', '.docx': '📘',
        '.xls': '📊', '.xlsx': '📊',
        '.ppt': '📊', '.pptx': '📊',
        '.txt': '📄',
        '.csv': '📊',
        '.json': '🔧',
        '.py': '🐍',
        '.js': '💛',
        '.html': '🌐',
        '.css': '🎨',
        '.png': '🖼️', '.jpg': '🖼️', '.jpeg': '🖼️', '.gif': '🖼️'
    }
    return icons.get(ext.lower(), '📎')

# ----------------------
# Sidebar: Chat History
# ----------------------
with st.sidebar:
    # New Chat Button
    if st.button("✨ New Chat", key="new_chat"):
        create_new_chat()
        st.rerun()
    
    st.markdown("---")
    
    # Search chats
    st.markdown("### 💬 Chats")
    search_query = st.text_input("🔍 Search chats", key="search_chats", placeholder="Search...")
    
    # Filter and sort sessions
    sorted_sessions = sorted(
        st.session_state.chat_sessions.items(),
        key=lambda x: x[1]["created"],
        reverse=True
    )
    
    # Apply search filter
    if search_query:
        sorted_sessions = [
            (sid, sdata) for sid, sdata in sorted_sessions
            if search_query.lower() in sdata["title"].lower()
        ]
    
    for session_id, session_data in sorted_sessions:
        col1, col2 = st.columns([5, 1])
        with col1:
            if st.button(
                session_data["title"], 
                key=f"chat_{session_id}", 
                use_container_width=True
            ):
                st.session_state.current_session_id = session_id
                st.rerun()
        with col2:
            if st.button("🗑️", key=f"del_{session_id}", help="Delete chat"):
                if delete_chat(session_id):
                    st.rerun()
                else:
                    st.warning("Cannot delete the last chat")

# ----------------------
# Main Chat Area
# ----------------------
current_session = get_current_session()
user_messages = [m for m in current_session["messages"] if m["role"] == "user"]

if not user_messages:
    st.markdown("""
        <div class="welcome-container">
            <h1 class="welcome-title">What can I help with?</h1>
        </div>
    """, unsafe_allow_html=True)
else:
    for msg in current_session["messages"]:
        if msg["role"] == "system":
            continue
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if msg["role"] == "assistant" and "audio_file" in msg and msg["audio_file"]:
                st.audio(msg["audio_file"], format="audio/mp3")

# ----------------------
# File Upload Section (Universal Support)
# ----------------------
st.markdown("---")

# File upload area
col1, col2 = st.columns([3, 1])

with col1:
    # Accept ALL file types by listing comprehensive extensions
    uploaded_files = st.file_uploader(
        "📎 Attach any files (Word, PDF, Excel, PowerPoint, Images, Code, etc.)", 
        accept_multiple_files=True,
        key="file_uploader",
        help="Upload any document type - we'll extract the content automatically!",
        type=['pdf', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx', 
              'txt', 'csv', 'json', 'xml', 'yaml', 'yml',
              'py', 'js', 'html', 'css', 'md', 'java', 'cpp', 'c',
              'png', 'jpg', 'jpeg', 'gif', 'bmp', 'tiff', 'svg',
              'zip', 'rar', '7z', 'tar', 'gz']
    )

with col2:
    if current_session["files"]:
        if st.button("🗑️ Clear All Files", use_container_width=True):
            current_session["files"] = []
            st.session_state.last_processed_files = []
            st.rerun()

# Process uploaded files
if uploaded_files:
    current_file_names = [f.name for f in uploaded_files]
    if current_file_names != st.session_state.last_processed_files:
        st.session_state.last_processed_files = current_file_names
        
        with st.spinner("Processing files..."):
            for uploaded_file in uploaded_files:
                file_bytes = uploaded_file.read()
                content = extract_file_content(file_bytes, uploaded_file.name)
                
                if not any(f['filename'] == uploaded_file.name for f in current_session["files"]):
                    current_session["files"].append({
                        'filename': uploaded_file.name,
                        'content': content,
                        'size': len(file_bytes),
                        'type': Path(uploaded_file.name).suffix.upper()[1:] or 'FILE',
                        'icon': get_file_icon(Path(uploaded_file.name).suffix)
                    })
        
        st.toast(f"✅ {len(uploaded_files)} file(s) processed and attached!", icon="✅")
        st.rerun()

# Display attached files
if current_session["files"]:
    st.markdown("#### 📁 Attached Files")
    
    for idx, file_data in enumerate(current_session["files"]):
        col1, col2, col3, col4 = st.columns([0.5, 3, 1, 0.5])
        
        with col1:
            st.markdown(f"{file_data.get('icon', '📎')}")
        
        with col2:
            st.markdown(f"**{file_data['filename']}**")
        
        with col3:
            st.markdown(f"`{file_data.get('type', 'FILE')}` • *{format_file_size(file_data['size'])}*")
        
        with col4:
            if st.button("❌", key=f"remove_file_{idx}", help=f"Remove {file_data['filename']}"):
                remove_file(file_data['filename'])
                st.session_state.last_processed_files = [
                    f for f in st.session_state.last_processed_files 
                    if f != file_data['filename']
                ]
                st.rerun()
    
    st.markdown("---")

# Display library status
with st.expander("📚 Supported File Types & Library Status"):
    st.markdown("**✅ Always Supported:** TXT, JSON, CSV, Python, Markdown, HTML, CSS, JavaScript")
    st.markdown(f"**{'✅' if PDF_SUPPORT else '❌'} PDF:** {'Enabled' if PDF_SUPPORT else 'Install PyPDF2'}")
    st.markdown(f"**{'✅' if DOCX_SUPPORT else '❌'} Word (.docx):** {'Enabled' if DOCX_SUPPORT else 'Install python-docx'}")
    st.markdown(f"**{'✅' if PPTX_SUPPORT else '❌'} PowerPoint (.pptx):** {'Enabled' if PPTX_SUPPORT else 'Install python-pptx'}")
    st.markdown(f"**{'✅' if EXCEL_SUPPORT else '❌'} Excel (.xlsx):** {'Enabled' if EXCEL_SUPPORT else 'Install openpyxl and pandas'}")
    st.markdown(f"**{'✅' if OCR_SUPPORT else '❌'} Images (OCR):** {'Enabled' if OCR_SUPPORT else 'Install Pillow and pytesseract'}")
    st.markdown("\n**To enable all formats, run:**")
    st.code("pip install PyPDF2 python-docx python-pptx openpyxl pandas Pillow pytesseract")

# ----------------------
# Chat Input
# ----------------------
user_message = st.chat_input("Ask anything...")

if user_message:
    # Update chat title if new
    if current_session["title"] == "New Chat":
        current_session["title"] = generate_chat_title(user_message)
    
    current_session["messages"].append({"role": "user", "content": user_message})
    with st.chat_message("user"):
        st.markdown(user_message)
    
    # Prepare context with files
    files_context = ""
    if current_session["files"]:
        files_context = "\n\n=== UPLOADED FILES ===\n"
        for fdata in current_session["files"]:
            files_context += f"\n[FILE: {fdata['filename']} ({fdata.get('type', 'FILE')})]\n"
            files_context += fdata['content'][:5000]  # Increased from 3000
            if len(fdata['content']) > 5000:
                files_context += "\n... (content truncated for context length)\n"
        files_context += "=== END FILES ===\n\n"
    
    # Assistant response
    with st.chat_message("assistant"):
        placeholder = st.empty()
        placeholder.markdown("🤔 Thinking...")
        try:
            # Build complete conversation history for API
            messages_for_api = [{"role": "system", "content": SYSTEM_PROMPT}]
            
            # Add ALL previous messages from this session (for memory)
            for m in current_session["messages"][1:]:  # Skip system prompt
                if m["role"] in ["user", "assistant"]:
                    # For the current user message, add file context
                    if m["role"] == "user" and m["content"] == user_message:
                        user_content = files_context + user_message if files_context else user_message
                        messages_for_api.append({"role": "user", "content": user_content})
                    else:
                        # Add all other messages as-is for full conversation history
                        messages_for_api.append({"role": m["role"], "content": m["content"]})
            
            payload = {"model": MODEL, "messages": messages_for_api}
            headers = {
                "Authorization": f"Bearer {API_KEY}",
                "Content-Type": "application/json"
            }
            url = "https://api.sarvam.ai/v1/chat/completions"
            resp = requests.post(url, headers=headers, json=payload, timeout=60)
            
            if resp.status_code != 200:
                response_text = f"⚠️ API Error {resp.status_code}\n\n{resp.text[:500]}"
            else:
                data = resp.json()
                response_text = data.get("choices", [{}])[0].get("message", {}).get("content", "No response.")
        except Exception as e:
            response_text = f"❌ Error: {e}"
        
        placeholder.markdown(response_text)
        
        # TTS audio
        audio_file = speak_text(response_text) if TTS_AVAILABLE else None
        current_session["messages"].append({
            "role": "assistant",
            "content": response_text,
            "audio_file": audio_file
        })
        if audio_file:
            st.audio(audio_file, format="audio/mp3")
        st.rerun()

# ----------------------
# Footer
# ----------------------
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: black; padding: 20px;'>"
    "<p>Shiva AI by Shivansh Mahajan</p>"
    "</div>",
    unsafe_allow_html=True
)
