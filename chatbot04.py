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
    'deep_translator': 'deep-translator',
    'fpdf': 'fpdf',
    'speech_recognition': 'SpeechRecognition',
    'audio_recorder_streamlit': 'audio-recorder-streamlit'
}

for module_name, package_name in REQUIRED_PACKAGES.items():
    try:
        __import__(module_name)
    except ImportError:
        install_package(package_name)

# Imports
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
    from docx.shared import Pt
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    DOCX_SUPPORT = True
except ImportError:
    DOCX_SUPPORT = False

try:
    import pptx
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

try:
    from deep_translator import GoogleTranslator
    TRANSLATE_SUPPORT = True
except ImportError:
    TRANSLATE_SUPPORT = False

try:
    from fpdf import FPDF
    FPDF_AVAILABLE = True
except ImportError:
    FPDF_AVAILABLE = False

try:
    import speech_recognition as sr
    SPEECH_RECOGNITION_AVAILABLE = True
except ImportError:
    SPEECH_RECOGNITION_AVAILABLE = False

try:
    from audio_recorder_streamlit import audio_recorder
    AUDIO_RECORDER_AVAILABLE = True
except ImportError:
    AUDIO_RECORDER_AVAILABLE = False

# ----------------------
# Streamlit UI Setup
# ----------------------
st.set_page_config(
    page_title="Shiva AI",
    layout="wide",
    page_icon="🔱",
    initial_sidebar_state="collapsed"
)

# ----------------------
# Custom CSS - White UI, Black Font, Mobile Friendly, Blue Toggle
# ----------------------
st.markdown("""
<style>
    /* ===== FORCE WHITE THEME EVERYWHERE ===== */
    :root {
        color-scheme: light only !important;
        --background-color: #ffffff !important;
        --text-color: #000000 !important;
    }
    
    * {
        color-scheme: light only !important;
    }
    
    html, body, [data-testid="stAppViewContainer"], [data-testid="stApp"], .main, .stApp {
        background-color: #ffffff !important;
        color: #000000 !important;
    }
    
    /* All text black */
    *, p, span, div, label, li, a, h1, h2, h3, h4, h5, h6,
    .stMarkdown, .stMarkdown *, .stText, [class*="css"] {
        color: #000000 !important;
    }
    
    /* ===== SIDEBAR ===== */
    [data-testid="stSidebar"],
    [data-testid="stSidebar"] > div:first-child,
    [data-testid="stSidebar"] * {
        background-color: #f5f5f5 !important;
        color: #000000 !important;
    }
    
    section[data-testid="stSidebar"] {
        background-color: #f5f5f5 !important;
    }
    
    /* ===== BUTTONS - Mobile Friendly ===== */
    .stButton > button {
        background-color: #ffffff !important;
        color: #000000 !important;
        border: 2px solid #cccccc !important;
        border-radius: 12px !important;
        padding: 12px 20px !important;
        font-size: 16px !important;
        font-weight: 500 !important;
        min-height: 48px !important;
        touch-action: manipulation !important;
        -webkit-tap-highlight-color: transparent !important;
    }
    
    .stButton > button:hover, .stButton > button:active {
        background-color: #f0f0f0 !important;
        border-color: #999999 !important;
        transform: scale(0.98);
    }
    
    .stButton > button[kind="primary"] {
        background-color: #2196F3 !important;
        color: #ffffff !important;
        border: none !important;
    }
    
    /* ===== TEXT INPUTS ===== */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    input, textarea {
        background-color: #ffffff !important;
        color: #000000 !important;
        border: 2px solid #e0e0e0 !important;
        border-radius: 10px !important;
        padding: 12px !important;
        font-size: 16px !important;
        min-height: 48px !important;
    }
    
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: #2196F3 !important;
        box-shadow: 0 0 0 2px rgba(33, 150, 243, 0.2) !important;
    }
    
    /* ===== SELECT BOXES ===== */
    .stSelectbox > div > div,
    .stSelectbox [data-baseweb="select"],
    [data-baseweb="select"] > div,
    [data-baseweb="popover"],
    [data-baseweb="menu"],
    [role="listbox"],
    [role="option"] {
        background-color: #ffffff !important;
        color: #000000 !important;
    }
    
    [data-baseweb="menu"] li,
    [role="option"] {
        background-color: #ffffff !important;
        color: #000000 !important;
        padding: 12px !important;
        min-height: 44px !important;
    }
    
    [data-baseweb="menu"] li:hover,
    [role="option"]:hover {
        background-color: #e3f2fd !important;
    }
    
    /* ===== CHAT MESSAGES ===== */
    .stChatMessage, [data-testid="stChatMessage"] {
        background-color: #f9f9f9 !important;
        border: 1px solid #e0e0e0 !important;
        border-radius: 15px !important;
        padding: 15px !important;
        margin: 10px 0 !important;
    }
    
    .stChatMessage *, [data-testid="stChatMessage"] * {
        color: #000000 !important;
    }
    
    /* ===== CHAT INPUT ===== */
    [data-testid="stChatInput"],
    .stChatInputContainer,
    .stChatInputContainer * {
        background-color: #ffffff !important;
        color: #000000 !important;
    }
    
    [data-testid="stChatInput"] textarea {
        background-color: #ffffff !important;
        color: #000000 !important;
        border: 2px solid #e0e0e0 !important;
        border-radius: 25px !important;
        padding: 12px 20px !important;
        font-size: 16px !important;
    }
    
    /* ===== EXPANDER ===== */
    .streamlit-expanderHeader,
    [data-testid="stExpander"],
    [data-testid="stExpander"] * {
        background-color: #ffffff !important;
        color: #000000 !important;
    }
    
    .streamlit-expanderHeader {
        border-radius: 10px !important;
        padding: 15px !important;
        min-height: 50px !important;
    }
    
    /* ===== FILE UPLOADER ===== */
    .stFileUploader, [data-testid="stFileUploader"] {
        background-color: #f9f9f9 !important;
        border: 2px dashed #cccccc !important;
        border-radius: 15px !important;
        padding: 20px !important;
    }
    
    .stFileUploader *, [data-testid="stFileUploader"] * {
        color: #000000 !important;
    }
    
    /* ===== SLIDERS ===== */
    .stSlider > div > div > div {
        background-color: #e0e0e0 !important;
    }
    
    .stSlider [data-baseweb="slider"] div[role="slider"] {
        background-color: #2196F3 !important;
    }
    
    /* ===== CHECKBOXES ===== */
    .stCheckbox label, .stCheckbox span {
        color: #000000 !important;
        font-size: 16px !important;
    }
    
    .stCheckbox > label > div[data-testid="stCheckbox"] > div:first-child {
        width: 24px !important;
        height: 24px !important;
    }
    
    /* ===== DOWNLOAD BUTTONS ===== */
    .stDownloadButton > button {
        background-color: #ffffff !important;
        color: #000000 !important;
        border: 2px solid #2196F3 !important;
        border-radius: 12px !important;
        padding: 12px 20px !important;
        min-height: 48px !important;
    }
    
    .stDownloadButton > button:hover {
        background-color: #e3f2fd !important;
    }
    
    /* ===== ALERTS ===== */
    .stAlert, [data-testid="stAlert"] {
        border-radius: 12px !important;
        padding: 15px !important;
    }
    
    .stAlert *, [data-testid="stAlert"] * {
        color: #000000 !important;
    }
    
    /* ===== CODE BLOCKS ===== */
    code, pre, .stCodeBlock {
        background-color: #f5f5f5 !important;
        color: #000000 !important;
        border-radius: 8px !important;
    }
    
    /* ===== WELCOME CONTAINER ===== */
    .welcome-container {
        display: flex;
        justify-content: center;
        align-items: center;
        min-height: 50vh;
        padding: 20px;
        text-align: center;
    }
    
    .welcome-title {
        font-size: clamp(1.5rem, 5vw, 2.5rem);
        font-weight: 300;
        color: #000000 !important;
    }
    
    /* ===== BLUE TOGGLE SWITCH ===== */
    .toggle-container {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 15px;
        padding: 15px;
        background: #f5f5f5;
        border-radius: 50px;
        margin: 10px 0;
    }
    
    .toggle-label {
        font-size: 14px;
        font-weight: 600;
        color: #000000 !important;
        white-space: nowrap;
    }
    
    .toggle-label.active {
        color: #2196F3 !important;
    }
    
    .toggle-switch {
        position: relative;
        width: 70px;
        height: 36px;
        background: #2196F3;
        border-radius: 50px;
        cursor: pointer;
        transition: all 0.3s ease;
        border: none;
        padding: 0;
    }
    
    .toggle-switch:hover {
        background: #1976D2;
    }
    
    .toggle-switch::after {
        content: '';
        position: absolute;
        top: 3px;
        left: 3px;
        width: 30px;
        height: 30px;
        background: white;
        border-radius: 50%;
        transition: all 0.3s ease;
        box-shadow: 0 2px 5px rgba(0,0,0,0.2);
    }
    
    .toggle-switch.active::after {
        left: calc(100% - 33px);
    }
    
    /* ===== MODEL BADGE ===== */
    .model-badge {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        padding: 8px 16px;
        border-radius: 20px;
        font-size: 14px;
        font-weight: 600;
        margin-bottom: 15px;
    }
    
    .model-shiva01 {
        background: linear-gradient(135deg, #ff9933, #ff6600);
        color: white !important;
    }
    
    .model-shiva02 {
        background: linear-gradient(135deg, #2196F3, #1565C0);
        color: white !important;
    }
    
    /* ===== MOBILE RESPONSIVE ===== */
    @media (max-width: 768px) {
        .main .block-container {
            padding: 1rem 0.5rem !important;
            max-width: 100% !important;
        }
        
        .stButton > button {
            width: 100% !important;
            padding: 15px !important;
            font-size: 16px !important;
        }
        
        .stTextArea > div > div > textarea {
            font-size: 16px !important;
        }
        
        h1 {
            font-size: 1.5rem !important;
        }
        
        h2 {
            font-size: 1.25rem !important;
        }
        
        h3 {
            font-size: 1.1rem !important;
        }
        
        .stExpander {
            margin: 5px 0 !important;
        }
        
        .streamlit-expanderHeader {
            padding: 12px !important;
            font-size: 14px !important;
        }
        
        [data-testid="column"] {
            padding: 0 5px !important;
        }
        
        .toggle-container {
            flex-direction: row;
            padding: 12px;
            gap: 10px;
        }
        
        .toggle-label {
            font-size: 12px;
        }
        
        .toggle-switch {
            width: 60px;
            height: 32px;
        }
        
        .toggle-switch::after {
            width: 26px;
            height: 26px;
        }
        
        .toggle-switch.active::after {
            left: calc(100% - 29px);
        }
    }
    
    /* ===== HIDE DARK MODE ELEMENTS ===== */
    [data-theme="dark"],
    [data-testid="stHeader"] [data-theme="dark"] {
        display: none !important;
    }
    
    /* Force header white */
    header, [data-testid="stHeader"] {
        background-color: #ffffff !important;
    }
    
    /* ===== SCROLLBAR ===== */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: #f1f1f1;
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: #c1c1c1;
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: #a1a1a1;
    }
    
    /* ===== TOAST ===== */
    [data-testid="stToast"] {
        background-color: #ffffff !important;
        color: #000000 !important;
        border-radius: 12px !important;
    }
    
    /* ===== METRIC ===== */
    .stMetric, .stMetric * {
        color: #000000 !important;
    }
    
    /* ===== PLACEHOLDER ===== */
    ::placeholder {
        color: #888888 !important;
        opacity: 1 !important;
    }
    
    /* ===== DIVIDER ===== */
    hr {
        border-color: #e0e0e0 !important;
        margin: 20px 0 !important;
    }
    
    /* ===== LINKS ===== */
    a {
        color: #2196F3 !important;
    }
    
    /* ===== SPINNER ===== */
    .stSpinner > div {
        border-top-color: #2196F3 !important;
    }
</style>
""", unsafe_allow_html=True)

# ----------------------
# API Configuration
# ----------------------
SARVAM_API_KEY = os.getenv("CHATBOT_API_KEY", "sk_h4gsam68_z6e2xo8u9aaleUaBshwjVyDk")
SARVAM_API_URL = "https://api.sarvam.ai/v1/chat/completions"
SARVAM_MODEL = "sarvam-m"

GROQ_API_KEY = "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"
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL = "llama-3.1-8b-instant"

PRESENTATION_API_KEY = "sk_u0xsaah7_pxzQfsbxtI4S7SsXlLLIsjaa"
PEXELS_API_KEY = "3Y3jiJZ6WAL49N6lPsdlRbRZ6IZBfHZFHP86dr9yZfxFYoxedLLlDKAC"

SYSTEM_PROMPT = (
    "You are Shiva AI, an advanced intelligent assistant created by Shivansh Mahajan. "
    "Provide helpful, accurate, and detailed responses. "
    "Be professional, clear, and comprehensive in your answers."
)

SUPPORTED_LANGUAGES = {'en': 'English', 'de': 'German', 'fr': 'French', 'es': 'Spanish'}

FLASHCARD_STYLE_HINTS = {
    "qa": "Create Q&A flashcards with a clear question and concise answer.",
    "cloze": "Create cloze deletion cards with fill-in-the-blank format.",
    "term-def": "Create term-definition pairs.",
    "mixed": "Mix different flashcard styles."
}

STORAGE_DIR = Path("shiva_ai_data")
STORAGE_DIR.mkdir(exist_ok=True)


# ----------------------
# Helper Functions
# ----------------------
def transcribe_audio(audio_bytes):
    if not SPEECH_RECOGNITION_AVAILABLE:
        return None, "Speech recognition not available"
    try:
        recognizer = sr.Recognizer()
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_audio:
            temp_audio.write(audio_bytes)
            temp_audio_path = temp_audio.name
        with sr.AudioFile(temp_audio_path) as source:
            audio_data = recognizer.record(source)
        try:
            text = recognizer.recognize_google(audio_data)
            os.unlink(temp_audio_path)
            return text, None
        except sr.UnknownValueError:
            os.unlink(temp_audio_path)
            return None, "Could not understand audio."
        except sr.RequestError as e:
            os.unlink(temp_audio_path)
            return None, f"Service error: {e}"
    except Exception as e:
        return None, f"Error: {e}"


def get_ai_response_sarvam(messages, max_retries=3):
    headers = {"Authorization": f"Bearer {SARVAM_API_KEY}", "Content-Type": "application/json"}
    payload = {"model": SARVAM_MODEL, "messages": messages, "max_tokens": 4096, "temperature": 0.7}
    
    for attempt in range(max_retries):
        try:
            response = requests.post(SARVAM_API_URL, headers=headers, json=payload, timeout=120)
            if response.status_code == 200:
                data = response.json()
                if "choices" in data and len(data["choices"]) > 0:
                    return data["choices"][0].get("message", {}).get("content", "No response.")
            elif response.status_code == 429:
                import time
                time.sleep(2 ** attempt)
                continue
            else:
                return f"⚠️ Error {response.status_code}"
        except requests.exceptions.Timeout:
            continue
        except Exception as e:
            return f"❌ Error: {e}"
    return "⚠️ Failed after retries."


def get_ai_response_groq(messages, max_retries=3):
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
    payload = {"model": GROQ_MODEL, "messages": messages, "max_tokens": 4096, "temperature": 0.7}
    
    for attempt in range(max_retries):
        try:
            response = requests.post(GROQ_API_URL, headers=headers, json=payload, timeout=60)
            if response.status_code == 200:
                data = response.json()
                if "choices" in data and len(data["choices"]) > 0:
                    return data["choices"][0].get("message", {}).get("content", "No response.")
            elif response.status_code == 429:
                import time
                time.sleep(2 ** attempt)
                continue
            else:
                return f"⚠️ Error {response.status_code}"
        except requests.exceptions.Timeout:
            continue
        except Exception as e:
            return f"❌ Error: {e}"
    return "⚠️ Failed after retries."


def get_ai_response(messages, model_choice="shiva02"):
    if model_choice == "shiva01":
        return get_ai_response_sarvam(messages)
    return get_ai_response_groq(messages)


def generate_flashcards_from_text(text, n_cards=20, style="qa", focus="balanced", include_mnemonics=True, auto_tags=True):
    system_prompt = f"""You are Shiva AI's flashcard creator. Generate flashcards with {focus} focus.
Return ONLY JSON array: [{{"front": "Q?", "back": "A", "tags": ["tag"], "mnemonic": "tip"}}]
Style: {FLASHCARD_STYLE_HINTS.get(style, "")}"""
    
    payload = {
        "model": GROQ_MODEL,
        "messages": [{"role": "system", "content": system_prompt}, {"role": "user", "content": f"Generate {n_cards} flashcards:\n\n{text}"}],
        "max_tokens": 4000,
        "temperature": 0.7
    }
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
    response = requests.post(GROQ_API_URL, headers=headers, json=payload, timeout=120)
    response.raise_for_status()
    content = response.json()["choices"][0]["message"]["content"].strip()
    
    if "```json" in content:
        content = content.split("```json")[1]
    if "```" in content:
        content = content.split("```")[0]
    content = content.strip()
    
    start_idx, end_idx = content.find("["), content.rfind("]") + 1
    if start_idx != -1 and end_idx > start_idx:
        content = content[start_idx:end_idx]
    
    data = json.loads(content)
    cards = []
    for c in data:
        front, back = str(c.get("front", "")).strip(), str(c.get("back", "")).strip()
        if front and back:
            cards.append({"front": front, "back": back, "tags": c.get("tags") or [], "mnemonic": str(c.get("mnemonic", "")).strip()})
    return cards


def create_flashcard_text_file(cards):
    text = "=" * 50 + "\n   FLASHCARDS - Made by Shiva AI\n" + "=" * 50 + "\n\n"
    for i, c in enumerate(cards, 1):
        text += f"Card {i}\n{'-'*30}\nFRONT: {c['front']}\nBACK: {c['back']}\n"
        if c['tags']:
            text += f"TAGS: {', '.join(c['tags'])}\n"
        if c['mnemonic']:
            text += f"MNEMONIC: {c['mnemonic']}\n"
        text += "\n"
    text += f"Total: {len(cards)} cards\nMade by Shiva AI\n"
    return text


def create_flashcard_word_file(cards):
    if not DOCX_SUPPORT:
        return None
    try:
        doc = Document()
        doc.add_heading("Flashcards - Made by Shiva AI", 0)
        doc.add_paragraph("Created by Shivansh Mahajan")
        for i, c in enumerate(cards, 1):
            doc.add_heading(f"Card {i}", level=1)
            doc.add_paragraph(f"Front: {c['front']}")
            doc.add_paragraph(f"Back: {c['back']}")
            if c['tags']:
                doc.add_paragraph(f"Tags: {', '.join(c['tags'])}")
            if c['mnemonic']:
                doc.add_paragraph(f"Mnemonic: {c['mnemonic']}")
        buffer = io.BytesIO()
        doc.save(buffer)
        buffer.seek(0)
        return buffer
    except:
        return None


def create_flashcard_pdf_file(cards):
    if not FPDF_AVAILABLE:
        return None
    try:
        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()
        pdf.set_font('Arial', 'B', 16)
        pdf.cell(0, 10, 'Flashcards - Made by Shiva AI', 0, 1, 'C')
        pdf.set_font('Arial', '', 11)
        
        for i, c in enumerate(cards, 1):
            if pdf.get_y() > 250:
                pdf.add_page()
            pdf.set_font('Arial', 'B', 12)
            pdf.cell(0, 10, f'Card {i}', 0, 1)
            pdf.set_font('Arial', '', 11)
            
            front = c['front'].encode('latin-1', 'replace').decode('latin-1')
            back = c['back'].encode('latin-1', 'replace').decode('latin-1')
            
            pdf.multi_cell(0, 6, f"Front: {front}")
            pdf.multi_cell(0, 6, f"Back: {back}")
            pdf.ln(5)
        
        buffer = io.BytesIO()
        pdf_output = pdf.output(dest='S').encode('latin-1')
        buffer.write(pdf_output)
        buffer.seek(0)
        return buffer
    except:
        return None


def search_pexels_image(query):
    try:
        response = requests.get("https://api.pexels.com/v1/search", headers={"Authorization": PEXELS_API_KEY}, params={"query": query, "per_page": 1}, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get("photos"):
                return data["photos"][0]["src"].get("large")
    except:
        pass
    return None


def download_image(url):
    try:
        response = requests.get(url, timeout=15)
        if response.status_code == 200:
            return io.BytesIO(response.content)
    except:
        pass
    return None


def generate_english_presentation(topic, slide_count):
    headers = {"Authorization": f"Bearer {PRESENTATION_API_KEY}", "Content-Type": "application/json"}
    prompt = f"Generate {slide_count} slides for '{topic}'. Return JSON array with 'title' and 'content' keys only."
    payload = {"model": "sarvam-m", "messages": [{"role": "user", "content": prompt}], "max_tokens": 4096}
    response = requests.post(SARVAM_API_URL, headers=headers, json=payload, timeout=120)
    response.raise_for_status()
    text = response.json()["choices"][0]["message"]["content"]
    if "```" in text:
        text = text.split("```")[1] if "```json" in text else text.split("```")[1]
    text = text.replace("json", "").strip()
    start, end = text.find("["), text.rfind("]") + 1
    return json.loads(text[start:end])


def translate_content(text, lang):
    if not text.strip() or lang == 'en' or not TRANSLATE_SUPPORT:
        return text
    try:
        return GoogleTranslator(source='en', target=lang).translate(text)
    except:
        return text


def create_powerpoint_presentation(slides, topic, lang_name, include_images=True, progress_callback=None):
    from pptx import Presentation
    from pptx.util import Inches, Pt
    from pptx.dml.color import RGBColor
    from pptx.enum.text import PP_ALIGN
    
    prs = Presentation()
    prs.slide_width, prs.slide_height = Inches(13.333), Inches(7.5)
    
    # Title slide
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    title_box = slide.shapes.add_textbox(Inches(0.5), Inches(3), Inches(12.333), Inches(1.5))
    p = title_box.text_frame.paragraphs[0]
    p.text, p.font.size, p.font.bold, p.alignment = topic, Pt(48), True, PP_ALIGN.CENTER
    
    sub_box = slide.shapes.add_textbox(Inches(0.5), Inches(4.5), Inches(12.333), Inches(0.8))
    p2 = sub_box.text_frame.paragraphs[0]
    p2.text, p2.font.size, p2.alignment = f"Made by Shiva AI in {lang_name}", Pt(24), PP_ALIGN.CENTER
    
    for idx, s in enumerate(slides):
        if progress_callback:
            progress_callback(f"Slide {idx+1}...")
        cs = prs.slides.add_slide(prs.slide_layouts[6])
        tb = cs.shapes.add_textbox(Inches(0.4), Inches(0.5), Inches(12), Inches(1))
        tp = tb.text_frame.paragraphs[0]
        tp.text, tp.font.size, tp.font.bold = s['title'], Pt(32), True
        
        cb = cs.shapes.add_textbox(Inches(0.4), Inches(1.5), Inches(12), Inches(5.5))
        cf = cb.text_frame
        cf.word_wrap = True
        for i, line in enumerate(s.get('content', '').split('\n')):
            line = line.strip().lstrip('•-*● ')
            if not line:
                continue
            para = cf.paragraphs[0] if i == 0 else cf.add_paragraph()
            para.text, para.font.size = f"• {line}", Pt(18)
    
    # Thank you
    ts = prs.slides.add_slide(prs.slide_layouts[6])
    tb = ts.shapes.add_textbox(Inches(0.5), Inches(3), Inches(12.333), Inches(1.5))
    p = tb.text_frame.paragraphs[0]
    p.text, p.font.size, p.font.bold, p.alignment = "Thank You!", Pt(60), True, PP_ALIGN.CENTER
    
    buffer = io.BytesIO()
    prs.save(buffer)
    buffer.seek(0)
    return buffer


# Session helpers
def get_user_id():
    if "user_id" not in st.session_state:
        st.session_state.user_id = str(uuid.uuid4())
    return st.session_state.user_id


def get_sessions_file():
    return STORAGE_DIR / f"user_{get_user_id()}_sessions.pkl"


def save_sessions():
    try:
        with open(get_sessions_file(), 'wb') as f:
            data = {sid: {k: v for k, v in s.items() if k != "audio_file"} for sid, s in st.session_state.chat_sessions.items()}
            pickle.dump(data, f)
    except:
        pass


def load_sessions():
    try:
        if get_sessions_file().exists():
            with open(get_sessions_file(), 'rb') as f:
                return pickle.load(f)
    except:
        pass
    return None


def format_size(b):
    for u in ['B', 'KB', 'MB']:
        if b < 1024:
            return f"{b:.1f} {u}"
        b /= 1024
    return f"{b:.1f} GB"


def speak_text(text):
    if not TTS_AVAILABLE:
        return None
    try:
        tts = gTTS(text[:1000], lang="en")
        f = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
        tts.save(f.name)
        return f.name
    except:
        return None


def chat_title(msg):
    return msg[:40] + "..." if len(msg) > 40 else msg


def get_session():
    return st.session_state.chat_sessions[st.session_state.current_session_id]


def new_chat():
    nid = str(uuid.uuid4())
    st.session_state.chat_sessions[nid] = {
        "messages": [{"role": "system", "content": SYSTEM_PROMPT}],
        "files": [],
        "title": "New Chat",
        "created": datetime.now().strftime("%Y-%m-%d %H:%M")
    }
    st.session_state.current_session_id = nid
    save_sessions()


def delete_chat(sid):
    if len(st.session_state.chat_sessions) > 1:
        del st.session_state.chat_sessions[sid]
        if sid == st.session_state.current_session_id:
            st.session_state.current_session_id = list(st.session_state.chat_sessions.keys())[0]
        save_sessions()
        return True
    return False


def extract_file(data, name):
    ext = Path(name).suffix.lower()
    try:
        if ext == '.pdf' and PDF_SUPPORT:
            pdf = PyPDF2.PdfReader(io.BytesIO(data))
            return "\n".join([p.extract_text() or "" for p in pdf.pages])
        elif ext in ['.docx', '.doc'] and DOCX_SUPPORT:
            return "\n".join([p.text for p in Document(io.BytesIO(data)).paragraphs])
        elif ext in ['.txt', '.py', '.js', '.html', '.css', '.json', '.md', '.csv']:
            return data.decode('utf-8', errors='ignore')
    except:
        pass
    return f"[File: {name}]"


def file_icon(ext):
    return {'pdf': '📕', '.docx': '📘', '.txt': '📄', '.py': '🐍', '.js': '💛'}.get(ext.lower(), '📎')


# ----------------------
# Session State Init
# ----------------------
get_user_id()

for key, default in [
    ("app_mode", "chat"),
    ("ppt_stage", "enter_details"),
    ("flashcard_stage", "enter_text"),
    ("generated_flashcards", []),
    ("selected_model", "shiva02"),
    ("last_processed_files", [])
]:
    if key not in st.session_state:
        st.session_state[key] = default

if "chat_sessions" not in st.session_state:
    loaded = load_sessions()
    if loaded:
        st.session_state.chat_sessions = loaded
        st.session_state.current_session_id = list(loaded.keys())[0]
    else:
        st.session_state.chat_sessions = {}
        new_chat()

if "current_session_id" not in st.session_state:
    st.session_state.current_session_id = list(st.session_state.chat_sessions.keys())[0]


# ----------------------
# Sidebar
# ----------------------
with st.sidebar:
    st.markdown("## 🔱 Shiva AI")
    st.markdown("*Made by Shivansh Mahajan*")
    st.markdown("---")
    
    # Blue Toggle for Model Selection
    st.markdown("### 🧠 AI Model")
    
    current_model = st.session_state.selected_model
    
    # Toggle HTML
    toggle_class = "active" if current_model == "shiva02" else ""
    left_active = "" if current_model == "shiva02" else "active"
    right_active = "active" if current_model == "shiva02" else ""
    
    st.markdown(f"""
    <div class="toggle-container">
        <span class="toggle-label {left_active}">Shiva0.1</span>
        <div class="toggle-switch {toggle_class}" id="model-toggle"></div>
        <span class="toggle-label {right_active}">Shiva0.2</span>
    </div>
    """, unsafe_allow_html=True)
    
    # Actual toggle using checkbox (hidden but functional)
    toggle_value = st.checkbox(
        "Use Shiva0.2",
        value=(current_model == "shiva02"),
        key="model_toggle_checkbox",
        label_visibility="collapsed"
    )
    
    if toggle_value:
        st.session_state.selected_model = "shiva02"
        st.caption("⚡ Fast & great for multiple languages")
    else:
        st.session_state.selected_model = "shiva01"
        st.caption("🇮🇳 Good for Hindi & Indian languages")
    
    st.markdown("---")
    
    if st.button("✨ New Chat", use_container_width=True):
        st.session_state.app_mode = "chat"
        new_chat()
        st.rerun()
    
    if st.button("📊 Presentation", use_container_width=True):
        st.session_state.app_mode = "presentation"
        st.session_state.ppt_stage = "enter_details"
        st.rerun()
    
    if st.button("📚 Flashcards", use_container_width=True):
        st.session_state.app_mode = "flashcards"
        st.session_state.flashcard_stage = "enter_text"
        st.rerun()
    
    st.markdown("---")
    
    if st.session_state.app_mode == "chat":
        st.markdown("### 💬 Chats")
        for sid, sdata in sorted(st.session_state.chat_sessions.items(), key=lambda x: x[1].get("created", ""), reverse=True):
            cols = st.columns([5, 1])
            label = f"{'▶ ' if sid == st.session_state.current_session_id else ''}{sdata['title']}"
            if cols[0].button(label, key=f"c_{sid}", use_container_width=True):
                st.session_state.current_session_id = sid
                st.rerun()
            if cols[1].button("🗑️", key=f"d_{sid}"):
                delete_chat(sid)
                st.rerun()


# ----------------------
# Main Content
# ----------------------

# FLASHCARDS
if st.session_state.app_mode == "flashcards":
    st.markdown("# 📚 Flashcard Generator")
    st.markdown("*Made by Shiva AI*")
    st.markdown("---")
    
    if st.session_state.flashcard_stage == "enter_text":
        text = st.text_area("📝 Paste your text:", height=200, key="fc_text")
        
        c1, c2 = st.columns(2)
        num = c1.slider("Cards", 5, 30, 10)
        style = c2.selectbox("Style", ["qa", "cloze", "term-def", "mixed"])
        
        if st.button("🚀 Generate", type="primary", use_container_width=True):
            if text and len(text) >= 50:
                with st.spinner("Generating..."):
                    try:
                        cards = generate_flashcards_from_text(text, num, style)
                        if cards:
                            st.session_state.generated_flashcards = cards
                            st.session_state.flashcard_stage = "view_cards"
                            st.rerun()
                    except Exception as e:
                        st.error(f"Error: {e}")
            else:
                st.error("Enter at least 50 characters.")
        
        if st.button("🏠 Back"):
            st.session_state.app_mode = "chat"
            st.rerun()
    
    elif st.session_state.flashcard_stage == "view_cards":
        cards = st.session_state.generated_flashcards
        st.success(f"✅ {len(cards)} flashcards generated!")
        
        for i, c in enumerate(cards, 1):
            with st.expander(f"📝 {i}. {c['front'][:40]}..."):
                st.info(f"**Q:** {c['front']}")
                st.success(f"**A:** {c['back']}")
                if c['tags']:
                    st.write(f"Tags: {', '.join(c['tags'])}")
        
        st.markdown("### 📥 Download")
        c1, c2, c3 = st.columns(3)
        c1.download_button("📄 TXT", create_flashcard_text_file(cards), "flashcards.txt", use_container_width=True)
        
        word = create_flashcard_word_file(cards)
        if word:
            c2.download_button("📘 WORD", word, "flashcards.docx", use_container_width=True)
        
        pdf = create_flashcard_pdf_file(cards)
        if pdf:
            c3.download_button("📕 PDF", pdf, "flashcards.pdf", use_container_width=True)
        
        if st.button("🔄 More"):
            st.session_state.flashcard_stage = "enter_text"
            st.rerun()
        
        if st.button("🏠 Back"):
            st.session_state.app_mode = "chat"
            st.rerun()


# PRESENTATION
elif st.session_state.app_mode == "presentation":
    st.markdown("# 📊 Presentation Generator")
    st.markdown("*Made by Shiva AI*")
    
    if st.session_state.ppt_stage == "enter_details":
        topic = st.text_input("Topic:")
        lang = st.selectbox("Language", list(SUPPORTED_LANGUAGES.keys()), format_func=lambda x: SUPPORTED_LANGUAGES[x])
        slides = st.slider("Slides", 2, 10, 5)
        
        if st.button("🚀 Create", type="primary", use_container_width=True):
            if topic:
                with st.spinner("Creating..."):
                    try:
                        content = generate_english_presentation(topic, slides)
                        t_topic = translate_content(topic, lang)
                        t_slides = [{"title": translate_content(s["title"], lang), "content": translate_content(s["content"], lang)} for s in content]
                        ppt = create_powerpoint_presentation(t_slides, t_topic, SUPPORTED_LANGUAGES[lang])
                        st.session_state.ppt_file = ppt
                        st.session_state.ppt_name = f"{topic}_shiva.pptx"
                        st.session_state.ppt_stage = "download"
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error: {e}")
        
        if st.button("🏠 Back"):
            st.session_state.app_mode = "chat"
            st.rerun()
    
    elif st.session_state.ppt_stage == "download":
        st.balloons()
        st.success("✅ Ready!")
        st.download_button("📥 Download PPTX", st.session_state.ppt_file, st.session_state.ppt_name, use_container_width=True)
        
        if st.button("🔄 Another"):
            st.session_state.ppt_stage = "enter_details"
            st.rerun()
        
        if st.button("🏠 Back"):
            st.session_state.app_mode = "chat"
            st.rerun()


# CHAT
else:
    session = get_session()
    
    # Model badge
    if st.session_state.selected_model == "shiva01":
        st.markdown('<div class="model-badge model-shiva01">🔱 Shiva0.1</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="model-badge model-shiva02">🚀 Shiva0.2</div>', unsafe_allow_html=True)
    
    # Messages
    user_msgs = [m for m in session["messages"] if m["role"] == "user"]
    
    if not user_msgs:
        st.markdown("""
        <div class="welcome-container">
            <h1 class="welcome-title">🔱 How can Shiva AI help you?</h1>
        </div>
        """, unsafe_allow_html=True)
    else:
        for msg in session["messages"]:
            if msg["role"] == "system":
                continue
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])
                if msg["role"] == "assistant" and msg.get("audio_file"):
                    st.audio(msg["audio_file"])
    
    st.markdown("---")
    
    # Voice input
    if AUDIO_RECORDER_AVAILABLE:
        st.markdown("### 🎤 Voice")
        c1, c2 = st.columns([1, 3])
        
        with c1:
            audio = audio_recorder(text="", recording_color="#e74c3c", neutral_color="#2196F3", icon_size="2x")
        
        with c2:
            if audio:
                with st.spinner("🔊 Processing..."):
                    text, err = transcribe_audio(audio)
                    if text:
                        st.success(f"📝 {text}")
                        if st.button("📤 Send"):
                            if session["title"] == "New Chat":
                                session["title"] = chat_title(text)
                            session["messages"].append({"role": "user", "content": text})
                            save_sessions()
                            
                            msgs = [{"role": "system", "content": SYSTEM_PROMPT}]
                            msgs.extend([{"role": m["role"], "content": m["content"]} for m in session["messages"][-10:] if m["role"] in ["user", "assistant"]])
                            
                            resp = get_ai_response(msgs, st.session_state.selected_model)
                            session["messages"].append({"role": "assistant", "content": resp, "audio_file": speak_text(resp)})
                            save_sessions()
                            st.rerun()
                    elif err:
                        st.error(err)
        
        st.markdown("---")
    
    # File upload
    files = st.file_uploader("📎 Files", accept_multiple_files=True, type=['pdf', 'docx', 'txt', 'py', 'js', 'json', 'md'])
    
    if files:
        names = [f.name for f in files]
        if names != st.session_state.last_processed_files:
            st.session_state.last_processed_files = names
            for f in files:
                data = f.read()
                content = extract_file(data, f.name)
                if "files" not in session:
                    session["files"] = []
                if not any(x["filename"] == f.name for x in session["files"]):
                    session["files"].append({"filename": f.name, "content": content, "size": len(data)})
            save_sessions()
            st.rerun()
    
    if session.get("files"):
        st.markdown("#### 📁 Attached")
        for i, f in enumerate(session["files"]):
            c1, c2 = st.columns([6, 1])
            c1.write(f"📎 **{f['filename']}** ({format_size(f['size'])})")
            if c2.button("❌", key=f"rf_{i}"):
                session["files"] = [x for x in session["files"] if x["filename"] != f["filename"]]
                save_sessions()
                st.rerun()
        st.markdown("---")
    
    # Chat input
    user_input = st.chat_input("Ask Shiva AI...")
    
    if user_input:
        if session["title"] == "New Chat":
            session["title"] = chat_title(user_input)
        
        session["messages"].append({"role": "user", "content": user_input})
        save_sessions()
        
        with st.chat_message("user"):
            st.markdown(user_input)
        
        # Context
        ctx = ""
        if session.get("files"):
            ctx = "\n\n=== FILES ===\n"
            for f in session["files"]:
                ctx += f"\n[{f['filename']}]\n{f['content'][:3000]}\n"
            ctx += "=== END ===\n\n"
        
        with st.chat_message("assistant"):
            placeholder = st.empty()
            model_name = "Shiva0.1" if st.session_state.selected_model == "shiva01" else "Shiva0.2"
            placeholder.markdown(f"🔱 {model_name} is thinking...")
            
            try:
                msgs = [{"role": "system", "content": SYSTEM_PROMPT}]
                recent = [m for m in session["messages"] if m["role"] in ["user", "assistant"]][-10:]
                for m in recent[:-1]:
                    msgs.append({"role": m["role"], "content": m["content"][:2000]})
                msgs.append({"role": "user", "content": ctx + user_input if ctx else user_input})
                
                resp = get_ai_response(msgs, st.session_state.selected_model)
            except Exception as e:
                resp = f"❌ Error: {e}"
            
            placeholder.markdown(resp)
            
            audio = speak_text(resp) if TTS_AVAILABLE else None
            session["messages"].append({"role": "assistant", "content": resp, "audio_file": audio})
            save_sessions()
            
            if audio:
                st.audio(audio)
            
            st.rerun()


# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; padding: 20px;">
    <p><strong>🔱 Shiva AI</strong> - Made by Shivansh Mahajan</p>
</div>
""", unsafe_allow_html=True)
