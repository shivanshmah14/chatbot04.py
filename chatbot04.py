import streamlit as st
import uuid
import os
import requests
import tempfile
import json
from pathlib import Path
from datetime import datetime
import hashlib
import base64

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

try:
    from PIL import Image
    IMAGE_SUPPORT = True
except ImportError:
    IMAGE_SUPPORT = False

# --- Streamlit UI setup ---
st.set_page_config(
    page_title="Shiva AI",
    layout="wide",
    page_icon="🤖",
    initial_sidebar_state="expanded"
)

# Custom CSS - FIXED PROFESSIONAL DARK THEME
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
    
    /* ALL TEXT WHITE - FIXED */
    body, p, span, div, label, h1, h2, h3, h4, h5, h6,
    [data-testid="stMarkdownContainer"],
    [data-testid="stMarkdownContainer"] *,
    .stMarkdown,
    .stMarkdown *,
    [data-testid="stSidebar"],
    [data-testid="stSidebar"] *,
    [data-testid="stText"] {
        color: #ffffff !important;
    }
    
    /* BUTTONS - FIXED CONTRAST */
    .stButton > button {
        color: #ffffff !important;
        background-color: #1a1a1a !important;
        border: 1px solid #444444 !important;
        border-radius: 8px !important;
        transition: all 0.2s ease !important;
    }
    
    .stButton > button:hover {
        background-color: #2a2a2a !important;
        border-color: #666666 !important;
    }
    
    /* Button text must always be white */
    .stButton > button p,
    .stButton > button span,
    .stButton > button div {
        color: #ffffff !important;
    }
    
    /* PRIMARY BUTTON - BLUE */
    .stButton > button[kind="primary"] {
        background-color: #2563eb !important;
        color: #ffffff !important;
        border: 1px solid #2563eb !important;
    }
    
    .stButton > button[kind="primary"]:hover {
        background-color: #1d4ed8 !important;
        border-color: #1d4ed8 !important;
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
        color: #888888 !important;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #2563eb !important;
        outline: none !important;
        box-shadow: 0 0 0 2px rgba(37, 99, 235, 0.2) !important;
    }
    
    .stTextInput label {
        color: #ffffff !important;
    }
    
    /* TABS - FIXED VISIBILITY */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: #000000 !important;
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: #1a1a1a !important;
        color: #888888 !important;
        border: 1px solid #333333 !important;
        border-radius: 8px 8px 0 0 !important;
        padding: 8px 16px !important;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #2563eb !important;
        color: #ffffff !important;
        border-color: #2563eb !important;
    }
    
    .stTabs [data-baseweb="tab-panel"] {
        background-color: #000000 !important;
        padding-top: 1rem !important;
    }
    
    /* TOOLTIPS - FIXED READABILITY */
    [data-baseweb="tooltip"],
    .stTooltipIcon,
    div[role="tooltip"],
    [data-baseweb="popover"] {
        background-color: #1a1a1a !important;
        color: #ffffff !important;
        border: 1px solid #444444 !important;
        padding: 8px 12px !important;
        border-radius: 6px !important;
        font-size: 14px !important;
    }
    
    /* Tooltip inner content */
    [data-baseweb="tooltip"] > div,
    div[role="tooltip"] > div {
        color: #ffffff !important;
        background-color: transparent !important;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* FILE UPLOADER - COMPLETE FIX */
    div[data-testid="stFileUploader"] {
        width: 40px !important;
        height: 40px !important;
        padding: 0 !important;
        margin: 0 !important;
        background: transparent !important;
        overflow: visible !important;
    }
    
    div[data-testid="stFileUploader"] > div,
    div[data-testid="stFileUploader"] section {
        width: 40px !important;
        height: 40px !important;
        padding: 0 !important;
        margin: 0 !important;
        background: transparent !important;
    }
    
    /* HIDE ALL TEXT AND LABELS */
    div[data-testid="stFileUploader"] small,
    div[data-testid="stFileUploader"] label,
    div[data-testid="stFileUploader"] p,
    div[data-testid="stFileUploader"] span:not(.emoji) {
        display: none !important;
        visibility: hidden !important;
        width: 0 !important;
        height: 0 !important;
        font-size: 0 !important;
        line-height: 0 !important;
        opacity: 0 !important;
    }
    
    /* File upload dropzone - visible circle */
    section[data-testid="stFileUploadDropzone"] {
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        width: 40px !important;
        height: 40px !important;
        min-width: 40px !important;
        min-height: 40px !important;
        max-width: 40px !important;
        max-height: 40px !important;
        border-radius: 50% !important;
        border: 2px solid #ffffff !important;
        background-color: #1a1a1a !important;
        cursor: pointer !important;
        transition: all 0.2s !important;
        position: relative !important;
        overflow: hidden !important;
    }
    
    section[data-testid="stFileUploadDropzone"]:hover {
        background-color: #2a2a2a !important;
        border-color: #2563eb !important;
    }
    
    /* Show the + symbol - VISIBLE */
    section[data-testid="stFileUploadDropzone"]::before {
        content: "+" !important;
        font-size: 28px !important;
        color: #ffffff !important;
        font-weight: 300 !important;
        position: absolute !important;
        top: 50% !important;
        left: 50% !important;
        transform: translate(-50%, -50%) !important;
        z-index: 100 !important;
        pointer-events: none !important;
        line-height: 1 !important;
    }
    
    /* Hide all text inside dropzone */
    section[data-testid="stFileUploadDropzone"] p,
    section[data-testid="stFileUploadDropzone"] span,
    section[data-testid="stFileUploadDropzone"] small,
    section[data-testid="stFileUploadDropzone"] label,
    section[data-testid="stFileUploadDropzone"] > div > div,
    section[data-testid="stFileUploadDropzone"] > div > button > div {
        display: none !important;
        visibility: hidden !important;
        width: 0 !important;
        height: 0 !important;
        font-size: 0 !important;
        opacity: 0 !important;
    }
    
    /* Make button clickable but invisible */
    section[data-testid="stFileUploadDropzone"] > button {
        opacity: 0 !important;
        width: 100% !important;
        height: 100% !important;
        position: absolute !important;
        cursor: pointer !important;
        z-index: 99 !important;
        border: none !important;
        background: transparent !important;
    }
    
    /* Hide all inner divs */
    section[data-testid="stFileUploadDropzone"] > div {
        display: none !important;
    }
    
    /* LOGIN CONTAINER - CENTERED */
    .login-container {
        max-width: 420px;
        margin: 0 auto;
        padding: 2.5rem;
        background-color: #0a0a0a !important;
        border: 1px solid #333333 !important;
        border-radius: 16px !important;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3) !important;
    }
    
    /* Remove any weird boxes on login page */
    .login-container > div,
    .login-container [data-testid="stVerticalBlock"] {
        background-color: transparent !important;
        border: none !important;
    }
    
    /* WELCOME CONTAINER - FIXED CENTERING */
    .welcome-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        min-height: 70vh;
        text-align: center;
        padding: 2rem;
    }
    
    .welcome-title {
        font-size: 2.8rem;
        font-weight: 600;
        color: #ffffff !important;
        margin-bottom: 1rem;
        text-shadow: 0 2px 4px rgba(0,0,0,0.5);
    }
    
    /* CHAT MESSAGES - PROFESSIONAL */
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
    
    /* CHAT INPUT - ALWAYS VISIBLE */
    .stChatInputContainer {
        background-color: #1a1a1a !important;
        border: 1px solid #444444 !important;
        border-radius: 24px !important;
        padding: 0.5rem 1rem !important;
    }
    
    .stChatInputContainer:focus-within {
        border-color: #2563eb !important;
        box-shadow: 0 0 0 2px rgba(37, 99, 235, 0.2) !important;
    }
    
    .stChatInputContainer input,
    .stChatInputContainer textarea {
        background-color: transparent !important;
        color: #ffffff !important;
        border: none !important;
    }
    
    .stChatInputContainer input::placeholder,
    .stChatInputContainer textarea::placeholder {
        color: #888888 !important;
    }
    
    /* EXPANDER - DARK THEME */
    .streamlit-expanderHeader {
        background-color: #1a1a1a !important;
        color: #ffffff !important;
        border: 1px solid #333333 !important;
        border-radius: 8px !important;
    }
    
    .streamlit-expanderHeader:hover {
        background-color: #2a2a2a !important;
    }
    
    .streamlit-expanderContent {
        background-color: #0a0a0a !important;
        color: #ffffff !important;
        border: 1px solid #333333 !important;
        border-top: none !important;
    }
    
    /* SIDEBAR - PROFESSIONAL */
    section[data-testid="stSidebar"] {
        background-color: #000000 !important;
        border-right: 1px solid #222222 !important;
    }
    
    /* Sidebar buttons - ensure visibility */
    [data-testid="stSidebar"] .stButton > button {
        background-color: #1a1a1a !important;
        color: #ffffff !important;
        border: 1px solid #444444 !important;
    }
    
    [data-testid="stSidebar"] .stButton > button:hover {
        background-color: #2a2a2a !important;
        border-color: #666666 !important;
    }
    
    /* Sidebar button text always white */
    [data-testid="stSidebar"] .stButton > button p,
    [data-testid="stSidebar"] .stButton > button span,
    [data-testid="stSidebar"] .stButton > button div {
        color: #ffffff !important;
    }
    
    /* CAPTION TEXT */
    .stCaption {
        color: #888888 !important;
    }
    
    /* AUDIO PLAYER */
    audio {
        width: 100%;
        filter: invert(1) hue-rotate(180deg);
    }
    
    /* DIVIDERS */
    hr {
        border-color: #333333 !important;
        margin: 1rem 0 !important;
    }
    
    /* ALERTS - VISIBLE */
    .stAlert {
        background-color: #1a1a1a !important;
        color: #ffffff !important;
        border: 1px solid #444444 !important;
        border-radius: 8px !important;
    }
    
    /* SUCCESS/ERROR MESSAGES */
    .stSuccess {
        background-color: #1a3a1a !important;
        color: #7cfc00 !important;
        border: 1px solid #4a7c4a !important;
    }
    
    .stError {
        background-color: #3a1a1a !important;
        color: #ff6b6b !important;
        border: 1px solid #7c4a4a !important;
    }
    
    /* BRANDING FOOTER */
    .branding-footer {
        text-align: center;
        padding: 1rem 0;
        color: #888888 !important;
        font-size: 0.875rem;
        margin-top: 2rem;
    }
    
    .branding-footer strong {
        color: #2563eb !important;
        font-weight: 600;
    }
    
    /* MAIN CONTENT PADDING */
    .main-content {
        padding-bottom: 200px;
    }
    
    /* LOGOUT BUTTON - FIXED */
    [data-testid="stSidebar"] .stButton > button {
        background-color: #1a1a1a !important;
        color: #ffffff !important;
        border: 1px solid #444444 !important;
    }
    
    [data-testid="stSidebar"] .stButton > button:hover {
        background-color: #dc2626 !important;
        border-color: #dc2626 !important;
        color: #ffffff !important;
    }
    
    /* Force all nested elements in sidebar buttons to be white */
    [data-testid="stSidebar"] .stButton > button *,
    [data-testid="stSidebar"] .stButton > button p,
    [data-testid="stSidebar"] .stButton > button span,
    [data-testid="stSidebar"] .stButton > button div {
        color: #ffffff !important;
        background-color: transparent !important;
    }
    
    /* IMAGE PREVIEW */
    .image-preview {
        max-width: 100%;
        border-radius: 8px;
        margin: 1rem 0;
        border: 1px solid #333333;
    }
    
    /* MOBILE RESPONSIVENESS */
    @media (max-width: 768px) {
        .welcome-title {
            font-size: 2rem;
        }
        
        .login-container {
            padding: 1.5rem;
            margin: 1rem;
        }
        
        .main-content {
            padding-bottom: 220px;
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

# --- User Authentication Functions ---
def hash_password(password):
    """Hash password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def init_user_data():
    """Initialize user data structure with persistence"""
    if "users" not in st.session_state:
        st.session_state.users = {}
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    if "current_user" not in st.session_state:
        st.session_state.current_user = None
    if "session_initialized" not in st.session_state:
        st.session_state.session_initialized = True

def register_user(username, password):
    """Register a new user"""
    if username in st.session_state.users:
        return False, "Username already exists"
    
    st.session_state.users[username] = {
        "password": hash_password(password),
        "chat_sessions": {},
        "created": datetime.now().strftime("%Y-%m-%d %H:%M")
    }
    return True, "Registration successful"

def login_user(username, password):
    """Login user"""
    if username not in st.session_state.users:
        return False, "Invalid username or password"
    
    if st.session_state.users[username]["password"] != hash_password(password):
        return False, "Invalid username or password"
    
    st.session_state.logged_in = True
    st.session_state.current_user = username
    
    # Load user's chat sessions
    st.session_state.chat_sessions = st.session_state.users[username]["chat_sessions"]
    
    # Create first chat if none exist
    if not st.session_state.chat_sessions:
        new_id = str(uuid.uuid4())
        st.session_state.chat_sessions[new_id] = {
            "messages": [{"role": "system", "content": SYSTEM_PROMPT}],
            "files": [],
            "title": "New Chat",
            "created": datetime.now().strftime("%Y-%m-%d %H:%M")
        }
        st.session_state.current_session_id = new_id
    else:
        st.session_state.current_session_id = list(st.session_state.chat_sessions.keys())[0]
    
    return True, "Login successful"

def logout_user():
    """Logout user and save their data"""
    if st.session_state.current_user and "chat_sessions" in st.session_state:
        st.session_state.users[st.session_state.current_user]["chat_sessions"] = st.session_state.chat_sessions
    
    st.session_state.logged_in = False
    st.session_state.current_user = None
    if "chat_sessions" in st.session_state:
        del st.session_state.chat_sessions
    if "current_session_id" in st.session_state:
        del st.session_state.current_session_id

# --- Session state initialization ---
init_user_data()

if st.session_state.logged_in:
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
def process_image(file_bytes, filename):
    """Process image file and return base64 encoding"""
    try:
        if IMAGE_SUPPORT:
            img = Image.open(tempfile.NamedTemporaryFile(delete=False, suffix=Path(filename).suffix))
            # Save to temp file for display
            temp_path = tempfile.NamedTemporaryFile(delete=False, suffix=Path(filename).suffix).name
            with open(temp_path, 'wb') as f:
                f.write(file_bytes)
            return {
                'type': 'image',
                'path': temp_path,
                'base64': base64.b64encode(file_bytes).decode('utf-8'),
                'format': Path(filename).suffix[1:].upper()
            }
        return None
    except Exception as e:
        st.warning(f"Could not process image: {e}")
        return None

@st.cache_data
def extract_file_content(file_bytes, filename):
    """Extract text content from various file formats"""
    try:
        file_extension = Path(filename).suffix.lower()
        
        # Check if it's an image
        if file_extension in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']:
            return f"[IMAGE: {filename}]"
        
        if file_extension == '.txt':
            return file_bytes.decode('utf-8')
        
        elif file_extension == '.pdf':
            if not PDF_SUPPORT:
                return "⚠️ PDF support requires PyPDF2"
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

# --- Login/Registration UI ---
if not st.session_state.logged_in:
    st.markdown("""
        <div class="welcome-container">
            <h1 class="welcome-title">🤖 Shiva AI</h1>
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown('<div class="login-container">', unsafe_allow_html=True)
        
        tab1, tab2 = st.tabs(["Login", "Register"])
        
        with tab1:
            st.markdown("### Login")
            login_username = st.text_input("Username", key="login_username", placeholder="Enter your username")
            login_password = st.text_input("Password", type="password", key="login_password", placeholder="Enter your password")
            
            if st.button("Login", use_container_width=True, type="primary"):
                if login_username and login_password:
                    success, message = login_user(login_username, login_password)
                    if success:
                        st.success(message)
                        st.rerun()
                    else:
                        st.error(message)
                else:
                    st.error("Please enter username and password")
        
        with tab2:
            st.markdown("### Register")
            reg_username = st.text_input("Username", key="reg_username", placeholder="Choose a username")
            reg_password = st.text_input("Password", type="password", key="reg_password", placeholder="Choose a password")
            reg_password_confirm = st.text_input("Confirm Password", type="password", key="reg_password_confirm", placeholder="Confirm your password")
            
            if st.button("Register", use_container_width=True, type="primary"):
                if reg_username and reg_password and reg_password_confirm:
                    if reg_password != reg_password_confirm:
                        st.error("Passwords do not match")
                    elif len(reg_password) < 6:
                        st.error("Password must be at least 6 characters")
                    else:
                        success, message = register_user(reg_username, reg_password)
                        if success:
                            st.success(message + " - Please login")
                        else:
                            st.error(message)
                else:
                    st.error("Please fill all fields")
        
        st.markdown('</div>', unsafe_allow_html=True)

else:
    # --- Sidebar: Chat History ---
    with st.sidebar:
        col1, col2 = st.columns([4, 1])
        with col1:
            st.markdown(f"### 👤 {st.session_state.current_user}")
        with col2:
            if st.button("🚪", key="logout_btn", help="Logout"):
                logout_user()
                st.rerun()
        
        if st.button("✨ New Chat", use_container_width=True, type="primary"):
            create_new_chat()
            st.rerun()
        
        st.markdown("---")
        
        # Search chats
        search = st.text_input("", value=st.session_state.search_query, placeholder="🔍 Search chats...", key="search_input")
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
                is_current = session_id == st.session_state.current_session_id
                if st.button(
                    session_data["title"],
                    key=f"chat_{session_id}",
                    use_container_width=True,
                    type="primary" if is_current else "secondary",
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
                    if file_data.get('type') == 'image':
                        st.image(file_data['path'], width=150)
                    st.text(f"📄 {file_data['filename']}")
                with col2:
                    if st.button("❌", key=f"remove_{file_data['filename']}", help="Remove file"):
                        current_session["files"].remove(file_data)
                        st.rerun()

    # Input area
    input_col1, input_col2 = st.columns([1, 20])

    with input_col1:
        supported_types = ['txt', 'json', 'csv', 'py', 'md', 'html', 'css', 'js', 'htm', 'pdf', 'jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp']
        
        uploaded_files = st.file_uploader(
            "",
            type=supported_types,
            accept_multiple_files=True,
            key="file_uploader",
            label_visibility="collapsed"
        )
        
        if uploaded_files:
            current_file_names = [f.name for f in uploaded_files]
            if current_file_names != st.session_state.last_processed_files:
                st.session_state.last_processed_files = current_file_names
                for uploaded_file in uploaded_files:
                    file_bytes = uploaded_file.read()
                    file_extension = Path(uploaded_file.name).suffix.lower()
                    
                    # Check if it's an image
                    if file_extension in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']:
                        image_data = process_image(file_bytes, uploaded_file.name)
                        if image_data and not any(f['filename'] == uploaded_file.name for f in current_session["files"]):
                            current_session["files"].append({
                                'filename': uploaded_file.name,
                                'type': 'image',
                                'path': image_data['path'],
                                'base64': image_data['base64'],
                                'format': image_data['format']
                            })
                    else:
                        content = extract_file_content(file_bytes, uploaded_file.name)
                        if content and not any(f['filename'] == uploaded_file.name for f in current_session["files"]):
                            current_session["files"].append({
                                'filename': uploaded_file.name,
                                'content': content,
                                'type': 'text',
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
        # Save chat sessions before processing
        if st.session_state.current_user:
            st.session_state.users[st.session_state.current_user]["chat_sessions"] = st.session_state.chat_sessions
        
        update_chat_title(st.session_state.current_session_id, user_message)
        current_session["messages"].append({"role": "user", "content": user_message})
        
        with st.chat_message("user"):
            st.markdown(user_message)
        
        files_context = ""
        if current_session["files"]:
            files_context = "\n\n=== UPLOADED FILES ===\n"
            for file_data in current_session["files"]:
                if file_data.get('type') == 'image':
                    files_context += f"\n[IMAGE: {file_data['filename']}]\n"
                else:
                    files_context += f"\n[FILE: {file_data['filename']}]\n"
                    files_context += file_data.get('content', '')[:3000]
                    if len(file_data.get('content', '')) > 3000:
                        files_context += f"\n... (truncated)\n"
                files_context += "\n"
            files_context += "=== END FILES ===\n\n"
        
        st.rerun()

