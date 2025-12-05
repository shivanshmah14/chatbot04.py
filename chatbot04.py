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
import subprocess
import sys

# ----------------------
# Auto-install missing packages
# ----------------------
def install_package(package_name):
    """Install a package using pip"""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package_name, "-q"])
        return True
    except:
        return False

# Required packages
REQUIRED_PACKAGES = {
    'gtts': 'gtts',
    'PyPDF2': 'PyPDF2',
    'docx': 'python-docx',
    'pptx': 'python-pptx',
    'openpyxl': 'openpyxl',
    'pandas': 'pandas',
    'PIL': 'Pillow',
    'deep_translator': 'deep-translator'
}

# Auto-install missing packages
for module_name, package_name in REQUIRED_PACKAGES.items():
    try:
        __import__(module_name)
    except ImportError:
        install_package(package_name)

# Now import after ensuring installation
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
    install_package('python-pptx')
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
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

try:
    import pytesseract
    OCR_SUPPORT = True
except ImportError:
    OCR_SUPPORT = False

# Import Google Translate
try:
    from deep_translator import GoogleTranslator
    TRANSLATE_SUPPORT = True
except ImportError:
    install_package('deep-translator')
    try:
        from deep_translator import GoogleTranslator
        TRANSLATE_SUPPORT = True
    except ImportError:
        TRANSLATE_SUPPORT = False

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
    * {
        color: black !important;
    }
    
    body, .stApp, .main, .block-container, section, .element-container {
        background-color: white !important;
        color: black !important;
    }
    
    p, span, div, label, h1, h2, h3, h4, h5, h6, li, a, strong, em, code, pre {
        color: black !important;
    }
    
    .stMarkdown, .stMarkdown p, .stMarkdown span, .stMarkdown div {
        color: black !important;
    }
    
    [data-testid="stSidebar"], [data-testid="stSidebar"] > div {
        background-color: #f8f9fa !important;
        color: black !important;
    }
    
    [data-testid="stSidebar"] * {
        color: black !important;
    }
    
    .stButton>button, button {
        background-color: white !important;
        color: black !important;
        border: 1px solid #ddd !important;
    }
    
    .stButton>button:hover, button:hover {
        background-color: #f0f0f0 !important;
    }
    
    input, textarea, select {
        background-color: white !important;
        color: black !important;
        border: 1px solid #ddd !important;
    }
    
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
    
    .streamlit-expanderHeader, .streamlit-expanderContent {
        background-color: white !important;
        color: black !important;
    }
    
    code, pre {
        background-color: #f5f5f5 !important;
        color: black !important;
    }
    
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
    
    .stChatInput, .stChatInput input {
        background-color: white !important;
        color: black !important;
        border: 1px solid #ddd !important;
    }
    
    .uploadedFile, [data-testid="stFileUploader"] {
        background-color: #f8f9fa !important;
        color: black !important;
        border: 1px solid #ddd !important;
        border-radius: 8px;
    }
    
    [data-testid="stFileUploader"] * {
        color: black !important;
    }
    
    .stSpinner > div {
        border-color: black !important;
    }
    
    .stToast {
        background-color: white !important;
        color: black !important;
    }
    
    header, [data-testid="stHeader"] {
        background-color: white !important;
    }
    
    footer {
        background-color: white !important;
        color: black !important;
    }
    
    [data-testid="column"] {
        background-color: white !important;
    }
    
    [data-theme="dark"] {
        display: none !important;
    }
</style>
""", unsafe_allow_html=True)

# ----------------------
# Configuration
# ----------------------
API_KEY = os.getenv("CHATBOT_API_KEY", "sk_h4gsam68_z6e2xo8u9aaleUaBshwjVyDk")
PRESENTATION_API_KEY = "sk_u0xsaah7_pxzQfsbxtI4S7SsXlLLIsjaa"
MODEL = "sarvam-m"
SYSTEM_PROMPT = (
    "You are Shiva AI, an advanced intelligent assistant. "
    "Provide helpful, accurate, and detailed responses. "
    "When files are provided, analyze them thoroughly and reference specific details. "
    "When image files are uploaded but OCR is not available, acknowledge the image was received "
    "and ask the user to describe what's in the image or provide any text from it if they need analysis. "
    "Be professional, clear, and comprehensive in your answers."
)

# Presentation Generator Configuration
CHAT_API_URL = "https://api.sarvam.ai/v1/chat/completions"

# Supported languages (4 only - using Google Translate)
SUPPORTED_LANGUAGES = {
    'en': 'English',
    'de': 'German',
    'fr': 'French',
    'es': 'Spanish'
}

# Storage directory for persistent data
STORAGE_DIR = Path("shiva_ai_data")
STORAGE_DIR.mkdir(exist_ok=True)


# ----------------------
# Presentation Generator Functions
# ----------------------
def generate_english_presentation(topic, slide_count):
    """Generates presentation content in English using the Chat API."""
    headers = {"Authorization": f"Bearer {PRESENTATION_API_KEY}", "Content-Type": "application/json"}
    prompt = f"""
    You are an expert content creator. Generate a {slide_count}-slide presentation for the topic: '{topic}'.
    Return a single JSON array of objects. Each object must have "title" and "content" (a string with 3-4 bullet points, separated by newlines).
    Only return the JSON array, no additional text or markdown formatting.
    """
    payload = {"model": "sarvam-m", "messages": [{"role": "user", "content": prompt}]}
    response = requests.post(CHAT_API_URL, headers=headers, json=payload)
    response.raise_for_status()
    response_text = response.json()["choices"][0]["message"]["content"]
    
    # Clean up response if wrapped in markdown code blocks
    if response_text.startswith("```json"):
        response_text = response_text[7:]
    if response_text.startswith("```"):
        response_text = response_text[3:]
    if response_text.endswith("```"):
        response_text = response_text[:-3]
    response_text = response_text.strip()
    
    return json.loads(response_text)


def translate_content(text, target_lang):
    """Translates text to the target language using Google Translate."""
    if not text.strip() or target_lang == 'en':
        return text
    
    if not TRANSLATE_SUPPORT:
        return text
    
    try:
        translator = GoogleTranslator(source='en', target=target_lang)
        return translator.translate(text)
    except Exception:
        return text


def create_powerpoint_presentation(slides, topic, target_lang_name):
    """Creates a PowerPoint presentation from the slide content."""
    prs = Presentation()
    
    # Title Slide
    title_slide_layout = prs.slide_layouts[0]
    slide = prs.slides.add_slide(title_slide_layout)
    slide.shapes.title.text = topic
    slide.placeholders[1].text = f"Generated by Shiva AI in {target_lang_name}"
    
    # Content Slides
    for slide_data in slides:
        content_slide_layout = prs.slide_layouts[1]
        slide = prs.slides.add_slide(content_slide_layout)
        slide.shapes.title.text = slide_data['title']
        slide.shapes.placeholders[1].text = slide_data['content']

    # Save presentation to a byte stream to be downloaded
    ppt_stream = io.BytesIO()
    prs.save(ppt_stream)
    ppt_stream.seek(0)
    return ppt_stream


# ----------------------
# Helper Functions for User Management
# ----------------------
def get_user_id():
    """Get or create a unique user ID for this browser/device"""
    if "user_id" not in st.session_state:
        query_params = st.query_params
        if "user_id" in query_params:
            st.session_state.user_id = query_params["user_id"]
        else:
            st.session_state.user_id = str(uuid.uuid4())
            st.query_params["user_id"] = st.session_state.user_id
    return st.session_state.user_id


def get_user_sessions_file():
    """Get the session file path for current user"""
    user_id = get_user_id()
    return STORAGE_DIR / f"user_{user_id}_sessions.pkl"


# ----------------------
# Helper Functions for Persistence
# ----------------------
def save_sessions():
    """Save all chat sessions to disk for current user"""
    try:
        sessions_file = get_user_sessions_file()
        with open(sessions_file, 'wb') as f:
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
    except Exception:
        pass


def load_sessions():
    """Load chat sessions from disk for current user"""
    try:
        sessions_file = get_user_sessions_file()
        if sessions_file.exists():
            with open(sessions_file, 'rb') as f:
                return pickle.load(f)
    except Exception:
        pass
    return None


# ----------------------
# Session State Initialization
# ----------------------
get_user_id()

if "app_mode" not in st.session_state:
    st.session_state.app_mode = "chat"

if "ppt_stage" not in st.session_state:
    st.session_state.ppt_stage = 'enter_details'

if "chat_sessions" not in st.session_state:
    loaded_sessions = load_sessions()
    
    if loaded_sessions and len(loaded_sessions) > 0:
        st.session_state.chat_sessions = loaded_sessions
        try:
            sorted_ids = sorted(
                loaded_sessions.keys(),
                key=lambda x: loaded_sessions[x].get("created", ""),
                reverse=True
            )
            st.session_state.current_session_id = sorted_ids[0]
        except Exception:
            st.session_state.current_session_id = list(loaded_sessions.keys())[0]
    else:
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
# File Processing Helper Functions
# ----------------------
def extract_text_from_pdf(file_bytes):
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
    try:
        doc = Document(io.BytesIO(file_bytes))
        text = []
        
        for paragraph in doc.paragraphs:
            if paragraph.text.strip():
                text.append(paragraph.text)
        
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
    try:
        if PIL_AVAILABLE:
            from PIL import Image as PILImage
            image = PILImage.open(io.BytesIO(file_bytes))
            
            img_format = image.format or "Unknown"
            img_size = f"{image.size[0]}x{image.size[1]}"
            
            if OCR_SUPPORT:
                try:
                    text = pytesseract.image_to_string(image)
                    
                    if text.strip():
                        return f"[Image: {img_format}, {img_size} pixels]\n\nExtracted Text:\n{text.strip()}"
                    else:
                        return f"[Image: {img_format}, {img_size} pixels]\n\nNo text detected in the image."
                except Exception:
                    return f"[Image: {img_format}, {img_size} pixels]\n\nOCR failed."
            else:
                return f"[Image: {img_format}, {img_size} pixels]\n\nOCR not available."
        else:
            return "[Image file received. PIL not available for processing.]"
    except Exception as e:
        return f"[Image file could not be processed. Error: {str(e)}]"


@st.cache_data
def extract_file_content(file_bytes, filename):
    ext = Path(filename).suffix.lower()
    
    try:
        if ext == '.pdf':
            if PDF_SUPPORT:
                return extract_text_from_pdf(file_bytes)
            else:
                return f"[PDF file uploaded: {filename}. PDF support not available.]"
        
        elif ext in ['.docx', '.doc']:
            if DOCX_SUPPORT:
                return extract_text_from_docx(file_bytes)
            else:
                return f"[Word document uploaded: {filename}. DOCX support not available.]"
        
        elif ext in ['.pptx', '.ppt']:
            if PPTX_SUPPORT:
                return extract_text_from_pptx(file_bytes)
            else:
                return f"[PowerPoint uploaded: {filename}. PPTX support not available.]"
        
        elif ext in ['.xlsx', '.xls']:
            if EXCEL_SUPPORT:
                return extract_text_from_excel(file_bytes)
            else:
                return f"[Excel file uploaded: {filename}. Excel support not available.]"
        
        elif ext in ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff']:
            return extract_text_from_image(file_bytes)
        
        elif ext == '.txt':
            return file_bytes.decode('utf-8', errors='ignore')
        
        elif ext == '.json':
            try:
                return json.dumps(json.loads(file_bytes.decode('utf-8')), indent=2)
            except Exception:
                return file_bytes.decode('utf-8', errors='ignore')
        
        elif ext in ['.csv', '.py', '.md', '.html', '.css', '.js', '.xml', '.yaml', '.yml', '.java', '.cpp', '.c']:
            return file_bytes.decode('utf-8', errors='ignore')
        
        else:
            try:
                decoded = file_bytes.decode('utf-8', errors='ignore')
                if decoded.strip():
                    return decoded
                else:
                    return f"[Binary file uploaded: {filename} ({format_file_size(len(file_bytes))})]"
            except Exception:
                return f"[Binary file uploaded: {filename} ({format_file_size(len(file_bytes))})]"
    
    except Exception as e:
        return f"[File uploaded: {filename}, but encountered error during processing: {str(e)}]"


def format_file_size(size_bytes):
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"


def speak_text(text):
    if not TTS_AVAILABLE:
        return None
    try:
        tts = gTTS(text[:500], lang="en")
        audio_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
        tts.save(audio_file.name)
        return audio_file.name
    except Exception:
        return None


def generate_chat_title(msg):
    return msg[:50] + ("..." if len(msg) > 50 else "")


def get_current_session():
    return st.session_state.chat_sessions[st.session_state.current_session_id]


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
    save_sessions()


def delete_chat(session_id):
    if len(st.session_state.chat_sessions) > 1:
        del st.session_state.chat_sessions[session_id]
        if session_id == st.session_state.current_session_id:
            st.session_state.current_session_id = list(st.session_state.chat_sessions.keys())[0]
        save_sessions()
        return True
    return False


def remove_file(filename):
    current_session = get_current_session()
    current_session["files"] = [f for f in current_session["files"] if f['filename'] != filename]
    save_sessions()


def get_file_icon(ext):
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
# Sidebar
# ----------------------
with st.sidebar:
    if st.button("✨ New Chat", key="new_chat", use_container_width=True):
        st.session_state.app_mode = "chat"
        create_new_chat()
        st.rerun()
    
    if st.button("📊 Create Presentation", key="create_ppt", use_container_width=True):
        st.session_state.app_mode = "presentation"
        st.session_state.ppt_stage = 'enter_details'
        st.rerun()
    
    st.markdown("---")
    
    if st.session_state.app_mode == "chat":
        st.markdown("### 💬 Chats")
        search_query = st.text_input("🔍 Search chats", key="search_chats", placeholder="Search...")
        
        sorted_sessions = sorted(
            st.session_state.chat_sessions.items(),
            key=lambda x: x[1]["created"],
            reverse=True
        )
        
        if search_query:
            sorted_sessions = [
                (sid, sdata) for sid, sdata in sorted_sessions
                if search_query.lower() in sdata["title"].lower()
            ]
        
        for session_id, session_data in sorted_sessions:
            col1, col2 = st.columns([5, 1])
            with col1:
                btn_label = session_data["title"]
                if session_id == st.session_state.current_session_id:
                    btn_label = f"▶ {btn_label}"
                
                if st.button(
                    btn_label, 
                    key=f"chat_{session_id}", 
                    use_container_width=True
                ):
                    st.session_state.current_session_id = session_id
                    st.session_state.app_mode = "chat"
                    st.rerun()
            with col2:
                if st.button("🗑️", key=f"del_{session_id}", help="Delete chat"):
                    if delete_chat(session_id):
                        st.rerun()
                    else:
                        st.warning("Cannot delete the last chat")
    
    elif st.session_state.app_mode == "presentation":
        st.markdown("### 📊 Presentation Generator")
        st.markdown("Create AI-powered presentations!")
        
        st.markdown("---")
        st.markdown("**Features:**")
        st.markdown("✅ AI-generated content")
        st.markdown("✅ 4 Languages (EN/DE/FR/ES)")
        st.markdown("✅ Professional layouts")


# ----------------------
# Main Content Area
# ----------------------

if st.session_state.app_mode == "presentation":
    # ----------------------
    # Presentation Generator Mode (Simple - Like Reference)
    # ----------------------
    st.title("🤖 AI Presentation Generator")
    
    if st.session_state.ppt_stage == 'enter_details':
        st.header("Step 1: Provide Presentation Details")
        
        topic = st.text_input("What is the topic of your presentation?")
        
        language = st.selectbox(
            "Choose a language for the presentation", 
            options=list(SUPPORTED_LANGUAGES.keys()), 
            format_func=lambda x: SUPPORTED_LANGUAGES[x]
        )
        
        slide_count = st.slider("How many slides?", 2, 10, 5)

        if st.button("Build My Presentation"):
            if not topic:
                st.warning("Please provide a topic for your presentation.")
            else:
                with st.spinner("The AI is architecting your presentation... This may take a moment."):
                    try:
                        # AI Processing
                        st.info("Generating English content...")
                        english_slides = generate_english_presentation(topic, slide_count)
                        
                        target_lang_name = SUPPORTED_LANGUAGES[language]
                        st.info(f"Translating content to {target_lang_name}...")
                        
                        translated_topic = translate_content(topic, language)
                        translated_slides = []
                        for s in english_slides:
                            translated_slide = {
                                'title': translate_content(s['title'], language),
                                'content': translate_content(s['content'], language)
                            }
                            translated_slides.append(translated_slide)
                        
                        st.info("Building PowerPoint file...")
                        ppt_file_stream = create_powerpoint_presentation(
                            translated_slides, 
                            translated_topic, 
                            target_lang_name
                        )
                        
                        st.session_state.ppt_file = ppt_file_stream
                        st.session_state.ppt_file_name = f"{topic.replace(' ', '_')}_{language}.pptx"
                        st.session_state.ppt_stage = 'download'
                        st.rerun()

                    except Exception as e:
                        st.error(f"An error occurred: {e}")

    elif st.session_state.ppt_stage == 'download':
        st.header("Step 2: Download Your Presentation")
        st.balloons()
        st.success("Your presentation has been generated successfully!")
        
        st.download_button(
            label="Download Presentation (.pptx)",
            data=st.session_state.ppt_file,
            file_name=st.session_state.ppt_file_name,
            mime="application/vnd.openxmlformats-officedocument.presentationml.presentation"
        )
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Create Another Presentation"):
                st.session_state.ppt_stage = 'enter_details'
                st.rerun()
        with col2:
            if st.button("Back to Chat"):
                st.session_state.app_mode = "chat"
                st.session_state.ppt_stage = 'enter_details'
                st.rerun()

else:
    # ----------------------
    # Chat Mode
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

    st.markdown("---")

    col1, col2 = st.columns([3, 1])

    with col1:
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
            
            save_sessions()
            st.toast(f"✅ {len(uploaded_files)} file(s) processed and attached!", icon="✅")
            st.rerun()

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

    user_message = st.chat_input("Ask anything...")

    if user_message:
        if current_session["title"] == "New Chat":
            current_session["title"] = generate_chat_title(user_message)
        
        current_session["messages"].append({"role": "user", "content": user_message})
        save_sessions()
        
        with st.chat_message("user"):
            st.markdown(user_message)
        
        files_context = ""
        if current_session["files"]:
            files_context = "\n\n=== UPLOADED FILES ===\n"
            for fdata in current_session["files"]:
                files_context += f"\n[FILE: {fdata['filename']} ({fdata.get('type', 'FILE')})]\n"
                files_context += fdata['content'][:5000]
                if len(fdata['content']) > 5000:
                    files_context += "\n... (content truncated for context length)\n"
            files_context += "=== END FILES ===\n\n"
        
        with st.chat_message("assistant"):
            placeholder = st.empty()
            placeholder.markdown("🤔 Thinking...")
            try:
                messages_for_api = [{"role": "system", "content": SYSTEM_PROMPT}]
                
                conversation_messages = [m for m in current_session["messages"][1:] if m["role"] in ["user", "assistant"]]
                
                for i, m in enumerate(conversation_messages):
                    if i == len(conversation_messages) - 1 and m["role"] == "user" and m["content"] == user_message:
                        continue
                    messages_for_api.append({"role": m["role"], "content": m["content"]})
                
                user_content = files_context + user_message if files_context else user_message
                messages_for_api.append({"role": "user", "content": user_content})
                
                cleaned_messages = [messages_for_api[0]]
                for i in range(1, len(messages_for_api)):
                    current_msg = messages_for_api[i]
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
            
            audio_file = speak_text(response_text) if TTS_AVAILABLE else None
            current_session["messages"].append({
                "role": "assistant",
                "content": response_text,
                "audio_file": audio_file
            })
            save_sessions()
            
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
