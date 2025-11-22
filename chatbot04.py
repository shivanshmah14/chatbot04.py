import streamlit as st
import uuid
import os
import requests
import tempfile
import json
from pathlib import Path
from datetime import datetime
import io
import pickle

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
    "When image files are uploaded but OCR is not available, acknowledge the image was received "
    "and ask the user to describe what's in the image or provide any text from it if they need analysis. "
    "Be professional, clear, and comprehensive in your answers."
)

# Storage directory for persistent data
STORAGE_DIR = Path("shiva_ai_data")
STORAGE_DIR.mkdir(exist_ok=True)

# ----------------------
# Helper Functions for User Management
# ----------------------
def get_user_id():
    """Get or create a unique user ID for this browser/device"""
    if "user_id" not in st.session_state:
        # Check if user has a stored ID in browser cookies (via query params)
        query_params = st.query_params
        if "user_id" in query_params:
            st.session_state.user_id = query_params["user_id"]
        else:
            # Create new user ID
            st.session_state.user_id = str(uuid.uuid4())
            # Store in URL for persistence across sessions
            st.query_params["user_id"] = st.session_state.user_id
    return st.session_state.user_id

def get_user_sessions_file():
    """Get the session file path for current user"""
    user_id = get_user_id()
    return STORAGE_DIR / f"user_{user_id}_sessions.pkl"

# ----------------------
# Helper Functions for Persistence (User-Specific)
# ----------------------
def save_sessions():
    """Save all chat sessions to disk for current user"""
    try:
        sessions_file = get_user_sessions_file()
        with open(sessions_file, 'wb') as f:
            # Remove audio files before saving (they're temporary)
            sessions_to_save = {}
            for sid, sdata in st.session_state.chat_sessions.items():
                sessions_to_save[sid] = {
                    "messages": [{k: v for k, v in m.items() if k != "audio_file"} 
                                for m in sdata["messages"]],
                    "files": sdata["files"],
                    "title": sdata["title"],
                    "created": sdata["created"]
                }
            pickle.dump(sessions_to_save, f)
    except Exception as e:
        st.error(f"Error saving sessions: {e}")

def load_sessions():
    """Load chat sessions from disk for current user"""
    try:
        sessions_file = get_user_sessions_file()
        if sessions_file.exists():
            with open(sessions_file, 'rb') as f:
                return pickle.load(f)
    except Exception as e:
        st.error(f"Error loading sessions: {e}")
    return None

# ----------------------
# Session State Initialization with Persistence
# ----------------------
# Initialize user ID first
get_user_id()

if "chat_sessions" not in st.session_state:
    # Try to load existing sessions for this user
    loaded_sessions = load_sessions()
    
    if loaded_sessions and len(loaded_sessions) > 0:
        st.session_state.chat_sessions = loaded_sessions
        # Set current session to the most recent one
        try:
            sorted_ids = sorted(
                loaded_sessions.keys(),
                key=lambda x: loaded_sessions[x].get("created", ""),
                reverse=True
            )
            st.session_state.current_session_id = sorted_ids[0]
        except:
            st.session_state.current_session_id = list(loaded_sessions.keys())[0]
    else:
        # Create first session if no saved data
        st.session_state.chat_sessions = {}
        new_session_id = str(uuid.uuid4())
        st.session_state.current_session_id = new_session_id
        st.session_state.chat_sessions[new_session_id] = {
            "messages": [{"role": "system", "content": SYSTEM_PROMPT}],
            "files": [],
            "title": "New Chat",
            "created": datetime.now().strftime("%Y-%m-%d %H:%M")
        }
        save_sessions()

if "current_session_id" not in st.session_state:
    if st.session_state.chat_sessions:
        st.session_state.current_session_id = list(st.session_state.chat_sessions.keys())[0]
    else:
        new_session_id = str(uuid.uuid4())
        st.session_state.current_session_id = new_session_id
        st.session_state.chat_sessions[new_session_id] = {
            "messages": [{"role": "system", "content": SYSTEM_PROMPT}],
            "files": [],
            "title": "New Chat",
            "created": datetime.now().strftime("%Y-%m-%d %H:%M")
        }
        save_sessions()

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
            page_text = page.extract_text()
            if page_text.strip():
                text.append(page_text)
        result = "\n".join(text)
        return result if result.strip() else "PDF appears to be empty or contains only images."
    except Exception as e:
        return f"Unable to extract text from PDF: {str(e)}"

def extract_text_from_docx(file_bytes):
    """Extract text from Word document"""
    try:
        doc = Document(io.BytesIO(file_bytes))
        text = []
        
        # Extract paragraphs
        for paragraph in doc.paragraphs:
            if paragraph.text.strip():
                text.append(paragraph.text)
        
        # Extract text from tables
        for table in doc.tables:
            for row in table.rows:
                for cell in row.cells:
                    if cell.text.strip():
                        text.append(cell.text)
        
        result = "\n".join(text)
        return result if result.strip() else "Word document appears to be empty."
    except Exception as e:
        return f"Unable to extract text from Word document: {str(e)}"

def extract_text_from_pptx(file_bytes):
    """Extract text from PowerPoint"""
    try:
        prs = Presentation(io.BytesIO(file_bytes))
        text = []
        
        for slide_num, slide in enumerate(prs.slides, 1):
            slide_text = []
            for shape in slide.shapes:
                if hasattr(shape, "text") and shape.text.strip():
                    slide_text.append(shape.text)
            
            if slide_text:
                text.append(f"--- Slide {slide_num} ---")
                text.extend(slide_text)
        
        result = "\n".join(text)
        return result if result.strip() else "PowerPoint appears to be empty or contains only images."
    except Exception as e:
        return f"Unable to extract text from PowerPoint: {str(e)}"

def extract_text_from_excel(file_bytes):
    """Extract text from Excel"""
    try:
        df_dict = pd.read_excel(io.BytesIO(file_bytes), sheet_name=None)
        text = []
        
        for sheet_name, df in df_dict.items():
            if not df.empty:
                text.append(f"\n--- Sheet: {sheet_name} ---")
                text.append(df.to_string(index=False))
        
        result = "\n".join(text)
        return result if result.strip() else "Excel file appears to be empty."
    except Exception as e:
        return f"Unable to extract data from Excel: {str(e)}"

def extract_text_from_image(file_bytes):
    """Extract text from image using OCR or provide image description"""
    try:
        image = Image.open(io.BytesIO(file_bytes))
        
        # Get image info
        img_format = image.format or "Unknown"
        img_size = f"{image.size[0]}x{image.size[1]}"
        img_mode = image.mode
        
        # Try OCR if available
        if OCR_SUPPORT:
            try:
                text = pytesseract.image_to_string(image)
                if text.strip():
                    return f"[Image: {img_format}, {img_size} pixels]\n\nText extracted from image:\n{text}"
                else:
                    return f"[Image uploaded: {img_format} format, {img_size} pixels. The image appears to contain no readable text, or may contain graphics/photos only.]"
            except Exception as ocr_error:
                # OCR failed, provide basic image info
                return f"[Image uploaded: {img_format} format, {img_size} pixels, {img_mode} mode. OCR is installed but could not extract text - the image may contain graphics, photos, or handwriting rather than typed text.]"
        else:
            # No OCR - just acknowledge the image with details
            return f"[Image uploaded: {img_format} format, {img_size} pixels, {img_mode} mode. The image has been received. Note: Text extraction from images (OCR) is not available. If this image contains important text, please describe it or provide the text separately.]"
    
    except Exception as e:
        return f"[Image file uploaded but could not be processed. Error: {str(e)}]"

@st.cache_data
def extract_file_content(file_bytes, filename):
    """Extract text content from various file types"""
    ext = Path(filename).suffix.lower()
    
    try:
        # PDF files
        if ext == '.pdf':
            if PDF_SUPPORT:
                return extract_text_from_pdf(file_bytes)
            else:
                return f"[PDF file uploaded: {filename}. Install PyPDF2 to extract content]"
        
        # Word documents
        elif ext in ['.docx', '.doc']:
            if DOCX_SUPPORT:
                return extract_text_from_docx(file_bytes)
            else:
                return f"[Word document uploaded: {filename}. Install python-docx to extract content]"
        
        # PowerPoint presentations
        elif ext in ['.pptx', '.ppt']:
            if PPTX_SUPPORT:
                return extract_text_from_pptx(file_bytes)
            else:
                return f"[PowerPoint uploaded: {filename}. Install python-pptx to extract content]"
        
        # Excel files
        elif ext in ['.xlsx', '.xls']:
            if EXCEL_SUPPORT:
                return extract_text_from_excel(file_bytes)
            else:
                return f"[Excel file uploaded: {filename}. Install openpyxl and pandas to extract content]"
        
        # Image files
        elif ext in ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff']:
            return extract_text_from_image(file_bytes)
        
        # Text-based files
        elif ext == '.txt':
            return file_bytes.decode('utf-8', errors='ignore')
        
        # JSON files
        elif ext == '.json':
            try:
                return json.dumps(json.loads(file_bytes.decode('utf-8')), indent=2)
            except:
                return file_bytes.decode('utf-8', errors='ignore')
        
        # Code and markup files
        elif ext in ['.csv', '.py', '.md', '.html', '.css', '.js', '.xml', '.yaml', '.yml', '.java', '.cpp', '.c']:
            return file_bytes.decode('utf-8', errors='ignore')
        
        # Try to decode as text for any other file
        else:
            try:
                decoded = file_bytes.decode('utf-8', errors='ignore')
                if decoded.strip():
                    return decoded
                else:
                    return f"[Binary file uploaded: {filename} ({format_file_size(len(file_bytes))})]"
            except:
                return f"[Binary file uploaded: {filename} ({format_file_size(len(file_bytes))})]"
    
    except Exception as e:
        return f"[File uploaded: {filename}, but encountered error during processing: {str(e)}]"

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
    save_sessions()  # Save after creating new chat

def delete_chat(session_id):
    """Delete a chat session if not the last one"""
    if len(st.session_state.chat_sessions) > 1:
        del st.session_state.chat_sessions[session_id]
        if session_id == st.session_state.current_session_id:
            st.session_state.current_session_id = list(st.session_state.chat_sessions.keys())[0]
        save_sessions()  # Save after deleting
        return True
    return False

def remove_file(filename):
    """Remove a file from the current session"""
    current_session = get_current_session()
    current_session["files"] = [f for f in current_session["files"] if f['filename'] != filename]
    save_sessions()  # Save after removing file

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
        
        save_sessions()  # Save after processing files
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
    st.markdown(f"**{'✅' if PDF_SUPPORT else '❌'} PDF:** {'Enabled' if PDF_SUPPORT else '⚠️ Install PyPDF2: pip install PyPDF2'}")
    st.markdown(f"**{'✅' if DOCX_SUPPORT else '❌'} Word (.docx):** {'Enabled' if DOCX_SUPPORT else '⚠️ Install python-docx: pip install python-docx'}")
    st.markdown(f"**{'✅' if PPTX_SUPPORT else '❌'} PowerPoint (.pptx):** {'Enabled' if PPTX_SUPPORT else '⚠️ Install python-pptx: pip install python-pptx'}")
    st.markdown(f"**{'✅' if EXCEL_SUPPORT else '❌'} Excel (.xlsx):** {'Enabled' if EXCEL_SUPPORT else '⚠️ Install openpyxl pandas: pip install openpyxl pandas'}")
    st.markdown(f"**{'✅' if OCR_SUPPORT else '❌'} Images (OCR):** {'Enabled' if OCR_SUPPORT else '⚠️ Install Pillow pytesseract: pip install Pillow pytesseract'}")
    
    st.markdown("---")
    st.markdown("**🔍 Deployment Check:**")
    if not (PDF_SUPPORT and DOCX_SUPPORT and PPTX_SUPPORT and EXCEL_SUPPORT):
        st.warning("⚠️ Some libraries are missing! Make sure you have requirements.txt in your deployment.")
        st.code("""# requirements.txt content:
streamlit
requests
gtts
PyPDF2
python-docx
python-pptx
openpyxl
pandas
Pillow
pytesseract""")
    else:
        st.success("✅ All document libraries are installed!")
    
    st.markdown("\n**📝 For Streamlit Cloud:**")
    st.markdown("1. Add `requirements.txt` to your GitHub repo")
    st.markdown("2. Click 'Reboot app' in Streamlit Cloud dashboard")
    st.markdown("3. Wait 2-3 minutes for installation to complete")

# ----------------------
# Chat Input
# ----------------------
user_message = st.chat_input("Ask anything...")

if user_message:
    # Update chat title if new
    if current_session["title"] == "New Chat":
        current_session["title"] = generate_chat_title(user_message)
    
    current_session["messages"].append({"role": "user", "content": user_message})
    save_sessions()  # Save after user message
    
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
            # Build complete conversation history for API with proper alternating turns
            messages_for_api = [{"role": "system", "content": SYSTEM_PROMPT}]
            
            # Get all messages except system prompt
            conversation_messages = [m for m in current_session["messages"][1:] if m["role"] in ["user", "assistant"]]
            
            # Add conversation history (should already alternate)
            for i, m in enumerate(conversation_messages):
                # Skip the last message since we'll add it separately with file context
                if i == len(conversation_messages) - 1 and m["role"] == "user" and m["content"] == user_message:
                    continue
                messages_for_api.append({"role": m["role"], "content": m["content"]})
            
            # Add the current user message with file context
            user_content = files_context + user_message if files_context else user_message
            messages_for_api.append({"role": "user", "content": user_content})
            
            # Ensure proper alternation (fix if needed)
            cleaned_messages = [messages_for_api[0]]  # Keep system prompt
            for i in range(1, len(messages_for_api)):
                current_msg = messages_for_api[i]
                # Only add if it alternates with previous (or if it's the first non-system message)
                if len(cleaned_messages) == 1 or cleaned_messages[-1]["role"] != current_msg["role"]:
                    cleaned_messages.append(current_msg)
            
            payload = {"model": MODEL, "messages": cleaned_messages}
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
        save_sessions()  # Save after assistant response
        
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
