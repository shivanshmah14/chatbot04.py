import streamlit as st
import uuid
import os
import requests
import tempfile
import json
from pathlib import Path
from datetime import datetime

# Optional imports with fallbacks
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

# --- Streamlit UI setup ---
st.set_page_config(
    page_title="Shiva AI",
    layout="wide",
    page_icon="🤖",
    initial_sidebar_state="expanded"
)

# Custom CSS - BLACK THEME WITH WHITE TEXT
st.markdown("""
    <style>
    /* FORCE ALL BLACK BACKGROUNDS */
    [data-testid="stAppViewContainer"],
    [data-testid="stHeader"],
    .main,
    [data-testid="stSidebar"],
    .stApp,
    section[data-testid="stSidebar"],
    .main .block-container {
        background-color: #000000 !important;
    }
    
    /* ALL TEXT WHITE */
    *,
    [data-testid="stSidebar"],
    [data-testid="stSidebar"] *,
    [data-testid="stSidebar"] .stMarkdown,
    [data-testid="stSidebar"] h3,
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] span,
    [data-testid="stSidebar"] div,
    .stMarkdown,
    .stMarkdown *,
    h1, h2, h3, h4, h5, h6,
    p, span, div, label {
        color: #ffffff !important;
    }
    
    /* Button - BLACK with WHITE text */
    .stButton > button,
    .stButton > button * {
        color: #ffffff !important;
        background-color: #000000 !important;
        border: 1px solid #ffffff !important;
    }
    
    .stButton > button:hover {
        background-color: #1a1a1a !important;
    }
    
    /* Primary button - Blue with white text */
    .stButton > button[kind="primary"],
    .stButton > button[data-testid="baseButton-primary"] {
        background-color: #2563eb !important;
        color: #ffffff !important;
        border: 1px solid #2563eb !important;
    }
    
    .stButton > button[kind="primary"]:hover,
    .stButton > button[data-testid="baseButton-primary"]:hover {
        background-color: #1d4ed8 !important;
    }
    
    /* Search input - White with Black text */
    .stTextInput > div > div > input {
        background-color: #ffffff !important;
        color: #000000 !important;
        border: 1px solid #ffffff !important;
        border-radius: 8px !important;
        padding: 0.5rem 0.75rem !important;
    }
    
    .stTextInput > div > div > input::placeholder {
        color: #999999 !important;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #2563eb !important;
        outline: none !important;
    }
    
    /* Text input label WHITE */
    .stTextInput label {
        color: #ffffff !important;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* HIDE FILE UPLOADER UI - Show only button */
    div[data-testid="stFileUploader"] > div > div,
    div[data-testid="stFileUploader"] > div > div > div,
    div[data-testid="stFileUploader"] > div > div > div > div,
    div[data-testid="stFileUploader"] > div > div > div > small,
    div[data-testid="stFileUploader"] span:not(label span),
    div[data-testid="stFileUploader"] small,
    section[data-testid="stFileUploadDropzone"],
    section[data-testid="stFileUploadDropzone"] *,
    div[data-testid="stFileUploadDropzone"],
    div[data-testid="stFileUploadDropzone"] * {
        display: none !important;
        visibility: hidden !important;
        height: 0 !important;
        width: 0 !important;
        padding: 0 !important;
        margin: 0 !important;
    }
    
    /* File uploader container */
    div[data-testid="stFileUploader"] {
        background: transparent !important;
        border: none !important;
        padding: 0 !important;
        width: 40px !important;
        height: 40px !important;
    }
    
    div[data-testid="stFileUploader"] > div {
        background: transparent !important;
        border: none !important;
        padding: 0 !important;
        width: 40px !important;
        height: 40px !important;
    }
    
    /* File uploader button - BLACK with WHITE border */
    div[data-testid="stFileUploader"] label {
        display: inline-flex !important;
        visibility: visible !important;
        align-items: center !important;
        justify-content: center !important;
        width: 40px !important;
        height: 40px !important;
        border-radius: 50% !important;
        border: 1px solid #ffffff !important;
        background-color: #000000 !important;
        cursor: pointer !important;
        transition: all 0.2s !important;
        font-size: 20px !important;
        color: #ffffff !important;
        padding: 0 !important;
        margin: 0 !important;
    }
    
    div[data-testid="stFileUploader"] label:hover {
        background-color: #1a1a1a !important;
    }
    
    /* Welcome message - WHITE */
    .welcome-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        min-height: 60vh;
        text-align: center;
    }
    
    .welcome-title {
        font-size: 2.5rem;
        font-weight: 600;
        color: #ffffff !important;
        margin-bottom: 2rem;
    }
    
    /* Chat messages - BLACK background WHITE text */
    .stChatMessage {
        background-color: #000000 !important;
        border: none !important;
        padding: 1.5rem 0 !important;
    }
    
    .stChatMessage[data-testid="chat-message-user"] {
        background-color: #0a0a0a !important;
    }
    
    .stChatMessage[data-testid="chat-message-assistant"] {
        background-color: #000000 !important;
    }
    
    .stChatMessage * {
        color: #ffffff !important;
    }
    
    /* Main content padding */
    .main-content {
        padding-bottom: 200px;
    }
    
    /* Branding footer - WHITE text */
    .branding-footer {
        text-align: center;
        padding: 0.5rem 0;
        color: #ffffff !important;
        font-size: 0.875rem;
        font-weight: 500;
    }
    
    .branding-footer strong {
        color: #2563eb !important;
        font-weight: 600;
    }
    
    /* Chat input - BLACK with WHITE text */
    .stChatInputContainer {
        border: 1px solid #ffffff !important;
        border-radius: 24px !important;
        padding: 0.5rem 1rem !important;
        background-color: #000000 !important;
    }
    
    .stChatInputContainer input {
        background-color: #000000 !important;
        color: #ffffff !important;
    }
    
    .stChatInputContainer input::placeholder {
        color: #999999 !important;
    }
    
    /* Expander - BLACK with WHITE text */
    .streamlit-expanderHeader {
        background-color: #000000 !important;
        color: #ffffff !important;
        border: 1px solid #ffffff !important;
    }
    
    .streamlit-expanderContent {
        background-color: #000000 !important;
        color: #ffffff !important;
    }
    
    /* Caption text - light gray */
    .stCaption,
    [data-testid="stSidebar"] .stCaption {
        color: #999999 !important;
    }
    
    /* Audio player */
    audio {
        width: 100%;
        height: 40px;
        margin-top: 1rem;
    }
    
    /* Dividers - white */
    hr {
        border-color: #ffffff !important;
    }
    
    /* Sidebar border */
    section[data-testid="stSidebar"] {
        border-right: 1px solid #ffffff !important;
    }
    
    /* Toast notifications - BLACK with WHITE text */
    .stToast {
        background-color: #000000 !important;
        color: #ffffff !important;
        border: 1px solid #ffffff !important;
    }
    
    /* Warning messages - BLACK with WHITE text */
    .stAlert {
        background-color: #000000 !important;
        color: #ffffff !important;
        border: 1px solid #ffffff !important;
    }
    
    /* Mobile responsiveness */
    @media (max-width: 768px) {
        .welcome-title {
            font-size: 1.8rem;
        }
        
        .main-content {
            padding-bottom: 220px;
        }
        
        [data-testid="stSidebar"] {
            width: 100% !important;
        }
        
        .stChatMessage {
            padding: 1rem 0 !important;
        }
    }
    
    @media (max-width: 480px) {
        .welcome-title {
            font-size: 1.5rem;
        }
    }
    </style>
""", unsafe_allow_html=True)

# --- Configuration ---
API_KEY = os.getenv("CHATBOT_API_KEY", "sk_h4gsam68_z6e2xo8u9aaleUaBshwjVyDk")
MODEL = "sarvam-m"
SYSTEM_PROMPT = (
    "You are Shiva AI, an advanced intelligent assistant. "
    "Provide helpful, accurate, and detailed responses. "
    "When files are provided, analyze them thoroughly and reference specific details. "
    "Be professional, clear, and comprehensive in your answers."
)

# --- Session state initialization ---
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
if "voice_enabled" not in st.session_state:
    st.session_state.voice_enabled = True
if "search_query" not in st.session_state:
    st.session_state.search_query = ""
if "last_processed_files" not in st.session_state:
    st.session_state.last_processed_files = []

# --- Helper Functions ---
@st.cache_data
def extract_file_content(file_bytes, filename):
    """Extract text content from various file formats"""
    try:
        file_extension = Path(filename).suffix.lower()
        
        if file_extension == '.txt':
            return file_bytes.decode('utf-8')
        
        elif file_extension == '.pdf':
            if not PDF_SUPPORT:
                return "⚠️ PDF support requires PyPDF2. Install: pip install PyPDF2"
            import io
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(file_bytes))
            text = ""
            for page_num, page in enumerate(pdf_reader.pages, 1):
                text += f"\n--- Page {page_num} ---\n"
                text += page.extract_text() + "\n"
            return text
        
        elif file_extension == '.json':
            data = json.loads(file_bytes.decode('utf-8'))
            return json.dumps(data, indent=2)
        
        elif file_extension == '.csv':
            return file_bytes.decode('utf-8')
        
        elif file_extension in ['.py', '.md', '.html', '.css', '.js', '.htm']:
            return file_bytes.decode('utf-8')
        
        else:
            return file_bytes.decode('utf-8', errors='ignore')
    except Exception as e:
        return f"❌ Error reading {filename}: {str(e)}"

def speak_text(text):
    """Generate TTS audio for the response"""
    if not TTS_AVAILABLE:
        return None
    
    try:
        tts_text = text[:500] if len(text) > 500 else text
        tts = gTTS(text=tts_text, lang="en", tld="co.in")
        audio_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
        tts.save(audio_file.name)
        return audio_file.name
    except Exception as e:
        st.warning(f"🔇 Voice unavailable: {str(e)}")
        return None

def generate_chat_title(first_message):
    """Generate a short title from the first message"""
    title = first_message[:50].strip()
    if len(first_message) > 50:
        last_space = title.rfind(' ')
        if last_space > 30:
            title = title[:last_space] + "..."
        else:
            title += "..."
    return title

def create_new_chat():
    new_id = str(uuid.uuid4())
    st.session_state.chat_sessions[new_id] = {
        "messages": [{"role": "system", "content": SYSTEM_PROMPT}],
        "files": [],
        "title": "New Chat",
        "created": datetime.now().strftime("%Y-%m-%d %H:%M")
    }
    st.session_state.current_session_id = new_id
    st.session_state.last_processed_files = []

def switch_chat(session_id):
    st.session_state.current_session_id = session_id
    st.session_state.last_processed_files = []

def get_current_session():
    return st.session_state.chat_sessions[st.session_state.current_session_id]

def update_chat_title(session_id, title):
    if st.session_state.chat_sessions[session_id]["title"] == "New Chat":
        st.session_state.chat_sessions[session_id]["title"] = generate_chat_title(title)

def delete_chat(session_id):
    if len(st.session_state.chat_sessions) > 1:
        del st.session_state.chat_sessions[session_id]
        if session_id == st.session_state.current_session_id:
            st.session_state.current_session_id = list(st.session_state.chat_sessions.keys())[0]
        return True
    return False

# --- Sidebar: Chat History ---
with st.sidebar:
    if st.button("✨ New Chat", use_container_width=True, type="primary"):
        create_new_chat()
        st.rerun()
    
    st.markdown("---")
    
    # Search chats
    search = st.text_input("🔍 Search chats", value=st.session_state.search_query, placeholder="Search chats...")
    st.session_state.search_query = search
    
    st.markdown("---")
    st.markdown("### 💬 Chats")
    
    sorted_sessions = sorted(
        st.session_state.chat_sessions.items(),
        key=lambda x: x[1]["created"],
        reverse=True
    )
    
    if search:
        sorted_sessions = [
            (sid, sdata) for sid, sdata in sorted_sessions
            if search.lower() in sdata["title"].lower()
        ]
    
    for session_id, session_data in sorted_sessions:
        col1, col2 = st.columns([5, 1])
        
        with col1:
            if st.button(
                session_data["title"],
                key=f"chat_{session_id}",
                use_container_width=True,
                type="secondary",
                help=f"Created: {session_data['created']}"
            ):
                switch_chat(session_id)
                st.rerun()
        
        with col2:
            if st.button("🗑️", key=f"del_{session_id}", help="Delete chat"):
                if delete_chat(session_id):
                    st.rerun()
                else:
                    st.warning("Cannot delete the last chat")
    
    st.markdown("---")
    current = get_current_session()
    user_msg_count = len([m for m in current["messages"] if m["role"] == "user"])
    st.caption(f"💬 {user_msg_count} messages in current chat")

# --- Main Chat Area ---
current_session = get_current_session()
user_messages = [m for m in current_session["messages"] if m["role"] == "user"]

# Main content
st.markdown('<div class="main-content">', unsafe_allow_html=True)

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

st.markdown('</div>', unsafe_allow_html=True)

# Show attached files
if current_session["files"]:
    with st.expander(f"📎 {len(current_session['files'])} file(s) attached"):
        for file_data in current_session["files"]:
            col1, col2 = st.columns([5, 1])
            with col1:
                st.text(f"📄 {file_data['filename']} ({file_data['size']} chars)")
            with col2:
                if st.button("❌", key=f"remove_{file_data['filename']}", help="Remove file"):
                    current_session["files"].remove(file_data)
                    st.rerun()

# Input area
input_col1, input_col2 = st.columns([1, 20])

with input_col1:
    supported_types = ['txt', 'json', 'csv', 'py', 'md', 'html', 'css', 'js', 'htm']
    if PDF_SUPPORT:
        supported_types.insert(0, 'pdf')
    
    uploaded_files = st.file_uploader(
        "➕",
        type=supported_types,
        accept_multiple_files=True,
        key="file_uploader"
    )
    
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
                            'size': len(content)
                        })
            st.toast(f"✅ {len(uploaded_files)} file(s) attached!", icon="✅")
            st.rerun()

with input_col2:
    user_message = st.chat_input("Ask anything...")

# Branding
st.markdown("""
    <div class="branding-footer">
        🤖 <strong>Shiva AI</strong> - by Shivansh Mahajan
    </div>
""", unsafe_allow_html=True)

# Handle user message
if user_message:
    update_chat_title(st.session_state.current_session_id, user_message)
    current_session["messages"].append({"role": "user", "content": user_message})
    
    with st.chat_message("user"):
        st.markdown(user_message)
    
    files_context = ""
    if current_session["files"]:
        files_context = "\n\n=== UPLOADED FILES ===\n"
        for file_data in current_session["files"]:
            files_context += f"\n[FILE: {file_data['filename']}]\n"
            files_context += file_data['content'][:3000]
            if len(file_data['content']) > 3000:
                files_context += f"\n... (truncated)\n"
            files_context += "\n"
        files_context += "=== END FILES ===\n\n"
    
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
        
        except requests.exceptions.Timeout:
            response_text = "⏱️ Request timeout. Please try again."
        except requests.exceptions.RequestException as e:
            response_text = f"🌐 Connection error: {str(e)}"
        except Exception as e:
            response_text = f"❌ Error: {str(e)}"
        
        placeholder.markdown(response_text)
        
        audio_file = speak_text(response_text) if TTS_AVAILABLE else None
        
        current_session["messages"].append({
            "role": "assistant", 
            "content": response_text,
            "audio_file": audio_file
        })
        
        if audio_file:
            st.audio(audio_file, format="audio/mp3")
        
        st.rerun()

