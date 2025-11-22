import streamlit as st
import uuid
import os
import requests
import tempfile
import json
from pathlib import Path
from datetime import datetime

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
# Custom CSS for White Theme
# ----------------------
st.markdown("""
<style>
    /* Main background */
    .stApp {
        background-color: white;
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background-color: #f8f9fa;
    }
    
    [data-testid="stSidebar"] .stButton button {
        width: 100%;
        background-color: white;
        color: black;
        border: 1px solid #ddd;
        border-radius: 8px;
        padding: 10px;
        margin: 2px 0;
    }
    
    [data-testid="stSidebar"] .stButton button:hover {
        background-color: #f0f0f0;
    }
    
    [data-testid="stSidebar"] h3 {
        color: black;
    }
    
    /* Search input in sidebar */
    [data-testid="stSidebar"] input {
        background-color: white;
        color: black;
        border: 1px solid #ddd;
    }
    
    /* Welcome screen */
    .welcome-container {
        display: flex;
        justify-content: center;
        align-items: center;
        height: 60vh;
    }
    
    .welcome-title {
        font-size: 2.5rem;
        font-weight: 300;
        color: black;
        text-align: center;
    }
    
    /* Chat messages */
    .stChatMessage {
        background-color: white;
        color: black;
        border: 1px solid #e0e0e0;
        border-radius: 12px;
        padding: 15px;
        margin: 10px 0;
    }
    
    /* All text black */
    p, span, div, label {
        color: black !important;
    }
    
    /* Chat input */
    .stChatInput input {
        background-color: white;
        color: black;
        border: 1px solid #ddd;
    }
    
    /* File upload area */
    .uploadedFile {
        background-color: #f8f9fa;
        border: 1px solid #ddd;
        border-radius: 8px;
        padding: 10px;
        margin: 5px 0;
    }
    
    /* File badge */
    .file-badge {
        display: inline-block;
        background-color: #e3f2fd;
        color: #1976d2;
        padding: 5px 12px;
        border-radius: 15px;
        margin: 3px;
        font-size: 0.85rem;
        border: 1px solid #90caf9;
    }
    
    /* File container */
    .file-container {
        background-color: #f8f9fa;
        border: 1px solid #ddd;
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
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
@st.cache_data
def extract_file_content(file_bytes, filename):
    """Extract text content from various file types"""
    ext = Path(filename).suffix.lower()
    try:
        if ext == '.txt':
            return file_bytes.decode('utf-8')
        if ext == '.pdf' and PDF_SUPPORT:
            import io
            pdf = PyPDF2.PdfReader(io.BytesIO(file_bytes))
            return "\n".join([p.extract_text() for p in pdf.pages])
        if ext == '.json':
            return json.dumps(json.loads(file_bytes.decode('utf-8')), indent=2)
        if ext in ['.csv', '.py', '.md', '.html', '.css', '.js']:
            return file_bytes.decode('utf-8')
        return file_bytes.decode('utf-8', errors='ignore')
    except Exception as e:
        return f"Error reading {filename}: {e}"

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
# File Upload Section (Enhanced)
# ----------------------
st.markdown("---")

# File upload area
col1, col2 = st.columns([3, 1])

with col1:
    supported_types = ['txt', 'json', 'csv', 'py', 'md', 'html', 'css', 'js']
    if PDF_SUPPORT:
        supported_types.insert(0, 'pdf')
    
    uploaded_files = st.file_uploader(
        "📎 Attach files to your conversation", 
        type=supported_types, 
        accept_multiple_files=True,
        key="file_uploader",
        help="Upload documents to enhance the AI's context"
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
        for uploaded_file in uploaded_files:
            file_bytes = uploaded_file.read()
            content = extract_file_content(file_bytes, uploaded_file.name)
            if content:
                if not any(f['filename'] == uploaded_file.name for f in current_session["files"]):
                    current_session["files"].append({
                        'filename': uploaded_file.name,
                        'content': content,
                        'size': len(file_bytes),
                        'type': Path(uploaded_file.name).suffix.upper()[1:]
                    })
        st.toast(f"✅ {len(uploaded_files)} file(s) attached!", icon="✅")
        st.rerun()

# Display attached files
if current_session["files"]:
    st.markdown("#### 📁 Attached Files")
    
    for idx, file_data in enumerate(current_session["files"]):
        col1, col2, col3, col4 = st.columns([3, 1, 1, 0.5])
        
        with col1:
            st.markdown(f"**{file_data['filename']}**")
        
        with col2:
            st.markdown(f"`{file_data.get('type', 'FILE')}`")
        
        with col3:
            st.markdown(f"*{format_file_size(file_data['size'])}*")
        
        with col4:
            if st.button("❌", key=f"remove_file_{idx}", help=f"Remove {file_data['filename']}"):
                remove_file(file_data['filename'])
                st.session_state.last_processed_files = [
                    f for f in st.session_state.last_processed_files 
                    if f != file_data['filename']
                ]
                st.rerun()
    
    st.markdown("---")

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
            files_context += fdata['content'][:3000]
            if len(fdata['content']) > 3000:
                files_context += "\n... (truncated)\n"
        files_context += "=== END FILES ===\n\n"
    
    # Assistant response
    with st.chat_message("assistant"):
        placeholder = st.empty()
        placeholder.markdown("🤔 Thinking...")
        try:
            messages_for_api = [{"role": "system", "content": SYSTEM_PROMPT}]
            user_content = files_context + user_message if files_context else user_message
            
            for m in current_session["messages"][1:]:
                if m["role"] == "user" and m["content"] == user_message:
                    messages_for_api.append({"role": "user", "content": user_content})
                else:
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
