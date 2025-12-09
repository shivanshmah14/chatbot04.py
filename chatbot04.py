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
# Auto-install packages
# ----------------------
def install_package(pkg):
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", pkg, "-q"])
        return True
    except:
        return False

PACKAGES = {
    'gtts': 'gtts', 'PyPDF2': 'PyPDF2', 'docx': 'python-docx',
    'pptx': 'python-pptx', 'pandas': 'pandas', 'PIL': 'Pillow',
    'deep_translator': 'deep-translator', 'fpdf': 'fpdf',
    'speech_recognition': 'SpeechRecognition',
    'audio_recorder_streamlit': 'audio-recorder-streamlit'
}

for mod, pkg in PACKAGES.items():
    try:
        __import__(mod)
    except ImportError:
        install_package(pkg)

# Imports
try:
    from gtts import gTTS
    TTS_OK = True
except:
    TTS_OK = False

try:
    import PyPDF2
    PDF_OK = True
except:
    PDF_OK = False

try:
    from docx import Document
    DOCX_OK = True
except:
    DOCX_OK = False

try:
    import pptx
    PPTX_OK = True
except:
    PPTX_OK = False

try:
    from PIL import Image
    PIL_OK = True
except:
    PIL_OK = False

try:
    from deep_translator import GoogleTranslator
    TRANS_OK = True
except:
    TRANS_OK = False

try:
    from fpdf import FPDF
    FPDF_OK = True
except:
    FPDF_OK = False

try:
    import speech_recognition as sr
    SR_OK = True
except:
    SR_OK = False

try:
    from audio_recorder_streamlit import audio_recorder
    AR_OK = True
except:
    AR_OK = False

# ----------------------
# Page Config
# ----------------------
st.set_page_config(
    page_title="Shiva AI",
    layout="wide",
    page_icon="🔱",
    initial_sidebar_state="collapsed"
)

# ----------------------
# 100% WHITE UI CSS - EVERYTHING WHITE, BLACK TEXT
# ----------------------
st.markdown("""
<style>
    /* ==========================================
       FORCE LIGHT MODE - OVERRIDE EVERYTHING
       ========================================== */
    
    :root {
        color-scheme: light only !important;
        --primary-color: #2196F3 !important;
        --background-color: #ffffff !important;
        --secondary-background-color: #f8f8f8 !important;
        --text-color: #000000 !important;
    }
    
    /* Force light mode on html */
    html {
        color-scheme: light only !important;
        background-color: #ffffff !important;
    }
    
    /* ==========================================
       GLOBAL - EVERYTHING WHITE & BLACK TEXT
       ========================================== */
    
    *, *::before, *::after {
        color-scheme: light only !important;
    }
    
    html, body, div, span, p, a, li, ul, ol, 
    h1, h2, h3, h4, h5, h6, label, input, textarea, 
    button, select, option, table, tr, td, th,
    article, section, header, footer, main, nav {
        background-color: #ffffff !important;
        color: #000000 !important;
    }
    
    /* ==========================================
       STREAMLIT MAIN CONTAINERS
       ========================================== */
    
    .stApp,
    .main,
    [data-testid="stAppViewContainer"],
    [data-testid="stAppViewContainer"] > div,
    [data-testid="stAppViewContainer"] > div > div,
    [data-testid="stVerticalBlock"],
    [data-testid="stVerticalBlock"] > div,
    [data-testid="block-container"],
    .block-container,
    .element-container,
    [data-testid="element-container"],
    .stMarkdown,
    .stText {
        background-color: #ffffff !important;
        color: #000000 !important;
    }
    
    /* ==========================================
       HEADER
       ========================================== */
    
    header,
    [data-testid="stHeader"],
    [data-testid="stHeader"] > div,
    [data-testid="stToolbar"],
    [data-testid="stDecoration"] {
        background-color: #ffffff !important;
        color: #000000 !important;
    }
    
    /* ==========================================
       SIDEBAR - WHITE
       ========================================== */
    
    [data-testid="stSidebar"],
    [data-testid="stSidebar"] > div,
    [data-testid="stSidebar"] > div > div,
    [data-testid="stSidebar"] > div > div > div,
    [data-testid="stSidebar"] *,
    .css-1d391kg,
    .css-1lcbmhc,
    section[data-testid="stSidebar"],
    section[data-testid="stSidebar"] > div {
        background-color: #f5f5f5 !important;
        color: #000000 !important;
    }
    
    /* ==========================================
       FILE UPLOADER - 100% WHITE
       ========================================== */
    
    /* Main file uploader container */
    .stFileUploader,
    [data-testid="stFileUploader"],
    [data-testid="stFileUploader"] > div,
    [data-testid="stFileUploader"] > div > div,
    [data-testid="stFileUploader"] section,
    [data-testid="stFileUploader"] label,
    [data-testid="stFileUploader"] span,
    [data-testid="stFileUploader"] p,
    [data-testid="stFileUploader"] button,
    [data-testid="stFileUploader"] small {
        background-color: #ffffff !important;
        color: #000000 !important;
    }
    
    /* File uploader drop zone */
    [data-testid="stFileUploader"] > section,
    [data-testid="stFileUploader"] > div > section,
    .stFileUploader > section,
    .stFileUploader section,
    [data-testid="stFileUploaderDropzone"],
    [data-testid="stFileUploaderDropzoneInstructions"],
    [data-testid="stFileUploaderDropzoneInstructions"] > div,
    [data-testid="stFileUploaderDropzoneInstructions"] span,
    [data-testid="stFileUploaderDropzoneInstructions"] p,
    .uploadedFile,
    .uploadedFileData {
        background-color: #ffffff !important;
        background: #ffffff !important;
        color: #000000 !important;
        border: 2px dashed #cccccc !important;
        border-radius: 10px !important;
    }
    
    /* File uploader button */
    [data-testid="stFileUploader"] button,
    [data-testid="baseButton-secondary"],
    .stFileUploader button {
        background-color: #ffffff !important;
        color: #000000 !important;
        border: 1px solid #cccccc !important;
    }
    
    /* Uploaded file info */
    [data-testid="stFileUploader"] [data-testid="stMarkdownContainer"],
    [data-testid="stFileUploader"] .uploadedFileName,
    .stFileUploader .uploadedFile {
        background-color: #ffffff !important;
        color: #000000 !important;
    }
    
    /* File uploader SVG icons */
    [data-testid="stFileUploader"] svg,
    .stFileUploader svg {
        fill: #000000 !important;
        stroke: #000000 !important;
    }
    
    /* ==========================================
       BUTTONS - WHITE WITH BORDER
       ========================================== */
    
    .stButton > button,
    .stButton button,
    button[kind="primary"],
    button[kind="secondary"],
    [data-testid="baseButton-primary"],
    [data-testid="baseButton-secondary"],
    .stDownloadButton > button,
    .stDownloadButton button {
        background-color: #ffffff !important;
        background: #ffffff !important;
        color: #000000 !important;
        border: 2px solid #cccccc !important;
        border-radius: 10px !important;
        min-height: 45px !important;
    }
    
    .stButton > button:hover,
    .stDownloadButton > button:hover {
        background-color: #f0f0f0 !important;
        border-color: #999999 !important;
    }
    
    /* Primary button - blue */
    button[kind="primary"],
    [data-testid="baseButton-primary"] {
        background-color: #2196F3 !important;
        color: #ffffff !important;
        border: none !important;
    }
    
    /* ==========================================
       TEXT INPUTS & TEXTAREA - WHITE
       ========================================== */
    
    input,
    textarea,
    .stTextInput input,
    .stTextInput > div > div > input,
    .stTextArea textarea,
    .stTextArea > div > div > textarea,
    [data-testid="stTextInput"] input,
    [data-testid="stTextArea"] textarea,
    [data-baseweb="input"],
    [data-baseweb="textarea"] {
        background-color: #ffffff !important;
        background: #ffffff !important;
        color: #000000 !important;
        border: 2px solid #e0e0e0 !important;
        border-radius: 10px !important;
        caret-color: #000000 !important;
    }
    
    input::placeholder,
    textarea::placeholder {
        color: #888888 !important;
    }
    
    /* ==========================================
       CHAT INPUT - WHITE
       ========================================== */
    
    [data-testid="stChatInput"],
    [data-testid="stChatInput"] > div,
    [data-testid="stChatInput"] textarea,
    .stChatInputContainer,
    .stChatInputContainer > div,
    .stChatInputContainer textarea {
        background-color: #ffffff !important;
        background: #ffffff !important;
        color: #000000 !important;
        border-color: #e0e0e0 !important;
    }
    
    /* ==========================================
       CHAT MESSAGES - LIGHT GRAY
       ========================================== */
    
    .stChatMessage,
    [data-testid="stChatMessage"],
    [data-testid="stChatMessage"] > div,
    [data-testid="stChatMessageContent"],
    .stChatMessage > div {
        background-color: #f9f9f9 !important;
        background: #f9f9f9 !important;
        color: #000000 !important;
        border: 1px solid #e0e0e0 !important;
        border-radius: 15px !important;
    }
    
    .stChatMessage *,
    [data-testid="stChatMessage"] * {
        color: #000000 !important;
    }
    
    /* ==========================================
       SELECT BOX / DROPDOWN - WHITE
       ========================================== */
    
    .stSelectbox,
    .stSelectbox > div,
    .stSelectbox > div > div,
    [data-baseweb="select"],
    [data-baseweb="select"] > div,
    [data-baseweb="popover"],
    [data-baseweb="popover"] > div,
    [data-baseweb="menu"],
    [data-baseweb="menu"] > div,
    [role="listbox"],
    [role="option"] {
        background-color: #ffffff !important;
        background: #ffffff !important;
        color: #000000 !important;
    }
    
    [data-baseweb="menu"] li,
    [data-baseweb="menu"] ul,
    [role="option"] {
        background-color: #ffffff !important;
        color: #000000 !important;
    }
    
    [data-baseweb="menu"] li:hover,
    [role="option"]:hover {
        background-color: #e3f2fd !important;
    }
    
    /* ==========================================
       EXPANDER - WHITE
       ========================================== */
    
    .streamlit-expanderHeader,
    .streamlit-expanderContent,
    [data-testid="stExpander"],
    [data-testid="stExpander"] > div,
    [data-testid="stExpander"] summary,
    [data-testid="stExpander"] details,
    details, summary {
        background-color: #ffffff !important;
        background: #ffffff !important;
        color: #000000 !important;
    }
    
    /* ==========================================
       SLIDER - WHITE
       ========================================== */
    
    .stSlider,
    .stSlider > div,
    .stSlider label,
    .stSlider p,
    [data-testid="stSlider"],
    [data-baseweb="slider"] {
        background-color: #ffffff !important;
        color: #000000 !important;
    }
    
    /* ==========================================
       CHECKBOX - WHITE
       ========================================== */
    
    .stCheckbox,
    .stCheckbox > label,
    .stCheckbox span,
    [data-testid="stCheckbox"] {
        background-color: #ffffff !important;
        color: #000000 !important;
    }
    
    /* ==========================================
       ALERTS (INFO, SUCCESS, ERROR, WARNING)
       ========================================== */
    
    .stAlert,
    [data-testid="stAlert"],
    [data-testid="stAlert"] > div,
    .element-container .stAlert {
        background-color: #ffffff !important;
        color: #000000 !important;
        border-radius: 10px !important;
    }
    
    .stAlert *,
    [data-testid="stAlert"] * {
        color: #000000 !important;
    }
    
    /* ==========================================
       CODE BLOCKS - LIGHT GRAY
       ========================================== */
    
    code, pre,
    .stCodeBlock,
    [data-testid="stCodeBlock"] {
        background-color: #f5f5f5 !important;
        color: #000000 !important;
    }
    
    /* ==========================================
       TOAST / NOTIFICATIONS
       ========================================== */
    
    [data-testid="stToast"],
    .stToast {
        background-color: #ffffff !important;
        color: #000000 !important;
    }
    
    /* ==========================================
       SPINNER
       ========================================== */
    
    .stSpinner,
    .stSpinner > div {
        background-color: transparent !important;
    }
    
    /* ==========================================
       AUDIO PLAYER
       ========================================== */
    
    audio,
    .stAudio,
    [data-testid="stAudio"] {
        background-color: #ffffff !important;
    }
    
    /* ==========================================
       DIVIDER
       ========================================== */
    
    hr {
        border-color: #e0e0e0 !important;
        background-color: #e0e0e0 !important;
    }
    
    /* ==========================================
       LINKS
       ========================================== */
    
    a, a:visited, a:hover, a:active {
        color: #2196F3 !important;
    }
    
    /* ==========================================
       METRICS
       ========================================== */
    
    .stMetric,
    [data-testid="stMetric"],
    [data-testid="stMetricValue"],
    [data-testid="stMetricLabel"] {
        background-color: #ffffff !important;
        color: #000000 !important;
    }
    
    /* ==========================================
       COLUMNS
       ========================================== */
    
    [data-testid="column"],
    [data-testid="stHorizontalBlock"],
    .stHorizontalBlock {
        background-color: #ffffff !important;
    }
    
    /* ==========================================
       TABS
       ========================================== */
    
    .stTabs,
    [data-baseweb="tab-list"],
    [data-baseweb="tab"],
    [data-baseweb="tab-panel"] {
        background-color: #ffffff !important;
        color: #000000 !important;
    }
    
    /* ==========================================
       RADIO BUTTONS
       ========================================== */
    
    .stRadio,
    .stRadio > div,
    .stRadio label,
    [data-testid="stRadio"] {
        background-color: #ffffff !important;
        color: #000000 !important;
    }
    
    /* ==========================================
       DATA EDITOR / TABLE
       ========================================== */
    
    .stDataFrame,
    [data-testid="stDataFrame"],
    table, th, td, tr {
        background-color: #ffffff !important;
        color: #000000 !important;
    }
    
    /* ==========================================
       MARKDOWN
       ========================================== */
    
    .stMarkdown,
    .stMarkdown *,
    [data-testid="stMarkdownContainer"],
    [data-testid="stMarkdownContainer"] * {
        background-color: transparent !important;
        color: #000000 !important;
    }
    
    /* ==========================================
       PROGRESS BAR
       ========================================== */
    
    .stProgress,
    .stProgress > div {
        background-color: #ffffff !important;
    }
    
    /* ==========================================
       CUSTOM COMPONENTS
       ========================================== */
    
    /* Model box */
    .model-box {
        border-radius: 15px;
        padding: 15px;
        text-align: center;
        margin: 10px 0;
    }
    
    .model-box.shiva01 {
        background: linear-gradient(135deg, #ff9933, #ff6600) !important;
    }
    
    .model-box.shiva02 {
        background: linear-gradient(135deg, #2196F3, #1565C0) !important;
    }
    
    .model-box p {
        color: #ffffff !important;
        background: transparent !important;
    }
    
    .model-name {
        font-size: 18px;
        font-weight: bold;
        margin: 0;
    }
    
    .model-desc {
        font-size: 12px;
        margin: 5px 0 0 0;
        opacity: 0.9;
    }
    
    /* Chat model badge */
    .chat-badge {
        display: inline-block;
        padding: 6px 15px;
        border-radius: 20px;
        font-size: 14px;
        font-weight: 600;
        margin-bottom: 10px;
    }
    
    .chat-badge.b01 {
        background: linear-gradient(135deg, #ff9933, #ff6600) !important;
        color: #ffffff !important;
    }
    
    .chat-badge.b02 {
        background: linear-gradient(135deg, #2196F3, #1565C0) !important;
        color: #ffffff !important;
    }
    
    .chat-badge p, .chat-badge span {
        color: #ffffff !important;
        background: transparent !important;
    }
    
    /* Welcome */
    .welcome-box {
        display: flex;
        justify-content: center;
        align-items: center;
        min-height: 50vh;
        text-align: center;
    }
    
    .welcome-title {
        font-size: 1.8rem;
        font-weight: 300;
        color: #000000 !important;
    }
    
    /* ==========================================
       MOBILE RESPONSIVE
       ========================================== */
    
    @media (max-width: 768px) {
        .main .block-container {
            padding: 1rem 0.5rem !important;
        }
        
        .stButton > button,
        .stDownloadButton > button {
            padding: 12px !important;
            font-size: 14px !important;
            min-height: 50px !important;
        }
        
        h1 { font-size: 1.4rem !important; }
        h2 { font-size: 1.2rem !important; }
        h3 { font-size: 1.1rem !important; }
        
        /* Force white on mobile file uploader */
        [data-testid="stFileUploader"],
        [data-testid="stFileUploader"] *,
        .stFileUploader,
        .stFileUploader * {
            background-color: #ffffff !important;
            background: #ffffff !important;
            color: #000000 !important;
        }
    }
    
    /* ==========================================
       DARK MODE OVERRIDE - BLOCK COMPLETELY
       ========================================== */
    
    @media (prefers-color-scheme: dark) {
        html, body, .stApp, [data-testid="stAppViewContainer"],
        [data-testid="stFileUploader"], [data-testid="stFileUploader"] *,
        .stFileUploader, .stFileUploader *,
        *, *::before, *::after {
            background-color: #ffffff !important;
            background: #ffffff !important;
            color: #000000 !important;
            color-scheme: light only !important;
        }
    }
    
    /* Hide any dark theme elements */
    [data-theme="dark"],
    .dark,
    [class*="dark"] {
        background-color: #ffffff !important;
        color: #000000 !important;
    }
</style>
""", unsafe_allow_html=True)

# ----------------------
# API Config
# ----------------------
SARVAM_KEY = os.getenv("CHATBOT_API_KEY", "sk_h4gsam68_z6e2xo8u9aaleUaBshwjVyDk")
SARVAM_URL = "https://api.sarvam.ai/v1/chat/completions"
GROQ_KEY = "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"
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
PRES_KEY = "sk_u0xsaah7_pxzQfsbxtI4S7SsXlLLIsjaa"

SYSTEM = "You are Shiva AI, created by Shivansh Mahajan. Be helpful and professional."
LANGS = {'en': 'English', 'de': 'German', 'fr': 'French', 'es': 'Spanish'}
STORAGE = Path("shiva_data")
STORAGE.mkdir(exist_ok=True)


# ----------------------
# Functions
# ----------------------
def transcribe(audio):
    if not SR_OK:
        return None, "Not available"
    try:
        r = sr.Recognizer()
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as f:
            f.write(audio)
            p = f.name
        with sr.AudioFile(p) as s:
            a = r.record(s)
        try:
            t = r.recognize_google(a)
            os.unlink(p)
            return t, None
        except:
            os.unlink(p)
            return None, "Could not understand"
    except Exception as e:
        return None, str(e)


def ai_shiva01(msgs):
    """Shiva0.1 = Sarvam"""
    try:
        r = requests.post(SARVAM_URL, headers={"Authorization": f"Bearer {SARVAM_KEY}", "Content-Type": "application/json"},
                         json={"model": "sarvam-m", "messages": msgs, "max_tokens": 4096}, timeout=120)
        if r.status_code == 200:
            return r.json()["choices"][0]["message"]["content"]
        return f"Error {r.status_code}"
    except Exception as e:
        return f"Error: {e}"


def ai_shiva02(msgs):
    """Shiva0.2 = Groq"""
    try:
        r = requests.post(GROQ_URL, headers={"Authorization": f"Bearer {GROQ_KEY}", "Content-Type": "application/json"},
                         json={"model": "llama-3.1-8b-instant", "messages": msgs, "max_tokens": 4096}, timeout=60)
        if r.status_code == 200:
            return r.json()["choices"][0]["message"]["content"]
        return f"Error {r.status_code}"
    except Exception as e:
        return f"Error: {e}"


def ai_response(msgs, model):
    return ai_shiva01(msgs) if model == "shiva01" else ai_shiva02(msgs)


def make_flashcards(text, n=10):
    prompt = f"Generate {n} flashcards. Return ONLY JSON: [{{\"front\":\"Q\",\"back\":\"A\"}}]\n\nText: {text}"
    try:
        r = requests.post(GROQ_URL, headers={"Authorization": f"Bearer {GROQ_KEY}", "Content-Type": "application/json"},
                         json={"model": "llama-3.1-8b-instant", "messages": [{"role": "user", "content": prompt}], "max_tokens": 4000}, timeout=120)
        c = r.json()["choices"][0]["message"]["content"]
        if "```" in c:
            c = c.split("```")[1].replace("json", "")
        s, e = c.find("["), c.rfind("]") + 1
        return json.loads(c[s:e]) if s >= 0 else []
    except:
        return []


def cards_txt(cards):
    return "FLASHCARDS - Shiva AI\n" + "="*30 + "\n\n" + "\n\n".join([f"Q: {c['front']}\nA: {c['back']}" for c in cards])


def cards_word(cards):
    if not DOCX_OK:
        return None
    try:
        d = Document()
        d.add_heading("Flashcards - Shiva AI", 0)
        for i, c in enumerate(cards, 1):
            d.add_paragraph(f"{i}. Q: {c['front']}")
            d.add_paragraph(f"   A: {c['back']}")
        b = io.BytesIO()
        d.save(b)
        b.seek(0)
        return b
    except:
        return None


def cards_pdf(cards):
    if not FPDF_OK:
        return None
    try:
        p = FPDF()
        p.add_page()
        p.set_font('Arial', 'B', 14)
        p.cell(0, 10, 'Flashcards - Shiva AI', 0, 1, 'C')
        p.set_font('Arial', '', 11)
        for i, c in enumerate(cards, 1):
            if p.get_y() > 250:
                p.add_page()
            q = c['front'].encode('latin-1', 'replace').decode('latin-1')
            a = c['back'].encode('latin-1', 'replace').decode('latin-1')
            p.multi_cell(0, 6, f"{i}. Q: {q}")
            p.multi_cell(0, 6, f"   A: {a}")
            p.ln(3)
        b = io.BytesIO()
        b.write(p.output(dest='S').encode('latin-1'))
        b.seek(0)
        return b
    except:
        return None


def make_pres(topic, n):
    prompt = f"Generate {n} slides for '{topic}'. Return JSON: [{{\"title\":\"...\",\"content\":\"...\"}}]"
    try:
        r = requests.post(SARVAM_URL, headers={"Authorization": f"Bearer {PRES_KEY}", "Content-Type": "application/json"},
                         json={"model": "sarvam-m", "messages": [{"role": "user", "content": prompt}], "max_tokens": 4096}, timeout=120)
        c = r.json()["choices"][0]["message"]["content"]
        if "```" in c:
            c = c.split("```")[1].replace("json", "")
        s, e = c.find("["), c.rfind("]") + 1
        return json.loads(c[s:e]) if s >= 0 else []
    except:
        return []


def translate(t, lang):
    if not t or lang == 'en' or not TRANS_OK:
        return t
    try:
        return GoogleTranslator(source='en', target=lang).translate(t)
    except:
        return t


def make_pptx(slides, topic):
    from pptx import Presentation
    from pptx.util import Inches, Pt
    from pptx.enum.text import PP_ALIGN
    
    prs = Presentation()
    prs.slide_width, prs.slide_height = Inches(13.333), Inches(7.5)
    
    # Title
    s = prs.slides.add_slide(prs.slide_layouts[6])
    tb = s.shapes.add_textbox(Inches(0.5), Inches(3), Inches(12.333), Inches(1.5))
    p = tb.text_frame.paragraphs[0]
    p.text, p.font.size, p.font.bold, p.alignment = topic, Pt(44), True, PP_ALIGN.CENTER
    
    # Slides
    for sl in slides:
        cs = prs.slides.add_slide(prs.slide_layouts[6])
        t = cs.shapes.add_textbox(Inches(0.4), Inches(0.4), Inches(12), Inches(1))
        t.text_frame.paragraphs[0].text = sl['title']
        t.text_frame.paragraphs[0].font.size = Pt(28)
        t.text_frame.paragraphs[0].font.bold = True
        
        c = cs.shapes.add_textbox(Inches(0.4), Inches(1.3), Inches(12), Inches(5.5))
        cf = c.text_frame
        cf.word_wrap = True
        for i, ln in enumerate(sl.get('content', '').split('\n')):
            ln = ln.strip().lstrip('•-* ')
            if ln:
                para = cf.paragraphs[0] if i == 0 else cf.add_paragraph()
                para.text, para.font.size = f"• {ln}", Pt(16)
    
    # Thanks
    ts = prs.slides.add_slide(prs.slide_layouts[6])
    tb = ts.shapes.add_textbox(Inches(0.5), Inches(3), Inches(12.333), Inches(1.5))
    p = tb.text_frame.paragraphs[0]
    p.text, p.font.size, p.font.bold, p.alignment = "Thank You!", Pt(50), True, PP_ALIGN.CENTER
    
    b = io.BytesIO()
    prs.save(b)
    b.seek(0)
    return b


def uid():
    if "uid" not in st.session_state:
        st.session_state.uid = str(uuid.uuid4())
    return st.session_state.uid


def save():
    try:
        with open(STORAGE / f"{uid()}.pkl", 'wb') as f:
            pickle.dump({k: {x: y for x, y in v.items() if x != "audio"} for k, v in st.session_state.chats.items()}, f)
    except:
        pass


def load():
    try:
        p = STORAGE / f"{uid()}.pkl"
        if p.exists():
            with open(p, 'rb') as f:
                return pickle.load(f)
    except:
        pass
    return None


def speak(t):
    if not TTS_OK:
        return None
    try:
        tts = gTTS(t[:1000], lang="en")
        f = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
        tts.save(f.name)
        return f.name
    except:
        return None


def new_chat():
    nid = str(uuid.uuid4())
    st.session_state.chats[nid] = {"msgs": [{"role": "system", "content": SYSTEM}], "files": [], "title": "New Chat", "created": datetime.now().strftime("%Y-%m-%d %H:%M")}
    st.session_state.cid = nid
    save()


def del_chat(sid):
    if len(st.session_state.chats) > 1:
        del st.session_state.chats[sid]
        if sid == st.session_state.cid:
            st.session_state.cid = list(st.session_state.chats.keys())[0]
        save()
        return True
    return False


def extract(data, name):
    ext = Path(name).suffix.lower()
    try:
        if ext == '.pdf' and PDF_OK:
            return "\n".join([p.extract_text() or "" for p in PyPDF2.PdfReader(io.BytesIO(data)).pages])
        elif ext == '.docx' and DOCX_OK:
            return "\n".join([p.text for p in Document(io.BytesIO(data)).paragraphs])
        elif ext in ['.txt', '.py', '.js', '.json', '.md']:
            return data.decode('utf-8', errors='ignore')
    except:
        pass
    return f"[{name}]"


# ----------------------
# Init State
# ----------------------
uid()

for k, v in [("mode", "chat"), ("ppt_st", "enter"), ("fc_st", "enter"), ("cards", []), ("model", "shiva02"), ("pfiles", [])]:
    if k not in st.session_state:
        st.session_state[k] = v

if "chats" not in st.session_state:
    ld = load()
    if ld:
        st.session_state.chats = ld
        st.session_state.cid = list(ld.keys())[0]
    else:
        st.session_state.chats = {}
        new_chat()

if "cid" not in st.session_state:
    st.session_state.cid = list(st.session_state.chats.keys())[0]


# ----------------------
# Sidebar
# ----------------------
with st.sidebar:
    st.markdown("## 🔱 Shiva AI")
    st.markdown("*By Shivansh Mahajan*")
    st.markdown("---")
    
    # Model Selection
    st.markdown("### 🧠 Model")
    
    if st.session_state.model == "shiva01":
        st.markdown('<div class="model-box shiva01"><p class="model-name">🔱 Shiva0.1</p><p class="model-desc">Sarvam - Good for Hindi</p></div>', unsafe_allow_html=True)
        if st.button("🔄 Switch to Shiva0.2", use_container_width=True):
            st.session_state.model = "shiva02"
            st.rerun()
    else:
        st.markdown('<div class="model-box shiva02"><p class="model-name">🚀 Shiva0.2</p><p class="model-desc">Fast & multilingual</p></div>', unsafe_allow_html=True)
        if st.button("🔄 Switch to Shiva0.1", use_container_width=True):
            st.session_state.model = "shiva01"
            st.rerun()
    
    st.markdown("---")
    
    if st.button("✨ New Chat", use_container_width=True):
        st.session_state.mode = "chat"
        new_chat()
        st.rerun()
    
    if st.button("📊 Presentation", use_container_width=True):
        st.session_state.mode = "pres"
        st.session_state.ppt_st = "enter"
        st.rerun()
    
    if st.button("📚 Flashcards", use_container_width=True):
        st.session_state.mode = "flash"
        st.session_state.fc_st = "enter"
        st.rerun()
    
    st.markdown("---")
    
    if st.session_state.mode == "chat":
        st.markdown("### 💬 Chats")
        for sid, s in sorted(st.session_state.chats.items(), key=lambda x: x[1].get("created", ""), reverse=True):
            c1, c2 = st.columns([5, 1])
            lbl = ("▶ " if sid == st.session_state.cid else "") + s["title"][:20]
            if c1.button(lbl, key=f"c_{sid}", use_container_width=True):
                st.session_state.cid = sid
                st.rerun()
            if c2.button("🗑️", key=f"d_{sid}"):
                del_chat(sid)
                st.rerun()


# ----------------------
# Main
# ----------------------

# FLASHCARDS
if st.session_state.mode == "flash":
    st.markdown("# 📚 Flashcards")
    st.markdown("*Made by Shiva AI*")
    st.markdown("---")
    
    if st.session_state.fc_st == "enter":
        txt = st.text_area("📝 Text:", height=180)
        num = st.slider("Cards", 5, 20, 10)
        
        if st.button("🚀 Generate", type="primary", use_container_width=True):
            if txt and len(txt) >= 50:
                with st.spinner("Creating..."):
                    cards = make_flashcards(txt, num)
                    if cards:
                        st.session_state.cards = cards
                        st.session_state.fc_st = "view"
                        st.rerun()
            else:
                st.error("Need 50+ characters")
        
        if st.button("🏠 Back"):
            st.session_state.mode = "chat"
            st.rerun()
    
    else:
        cards = st.session_state.cards
        st.success(f"✅ {len(cards)} cards!")
        
        for i, c in enumerate(cards, 1):
            with st.expander(f"{i}. {c.get('front', '')[:40]}..."):
                st.info(f"**Q:** {c.get('front', '')}")
                st.success(f"**A:** {c.get('back', '')}")
        
        st.markdown("### 📥 Download")
        c1, c2, c3 = st.columns(3)
        c1.download_button("📄 TXT", cards_txt(cards), "cards.txt", use_container_width=True)
        w = cards_word(cards)
        if w:
            c2.download_button("📘 WORD", w, "cards.docx", use_container_width=True)
        p = cards_pdf(cards)
        if p:
            c3.download_button("📕 PDF", p, "cards.pdf", use_container_width=True)
        
        if st.button("🔄 More"):
            st.session_state.fc_st = "enter"
            st.rerun()
        if st.button("🏠 Back"):
            st.session_state.mode = "chat"
            st.rerun()


# PRESENTATION
elif st.session_state.mode == "pres":
    st.markdown("# 📊 Presentation")
    st.markdown("*Made by Shiva AI*")
    st.markdown("---")
    
    if st.session_state.ppt_st == "enter":
        topic = st.text_input("📝 Topic:")
        lang = st.selectbox("🌐 Language", list(LANGS.keys()), format_func=lambda x: LANGS[x])
        n = st.slider("📊 Slides", 3, 10, 5)
        
        if st.button("🚀 Create", type="primary", use_container_width=True):
            if topic:
                with st.spinner("Creating..."):
                    try:
                        slides = make_pres(topic, n)
                        t_topic = translate(topic, lang)
                        t_slides = [{"title": translate(s["title"], lang), "content": translate(s["content"], lang)} for s in slides]
                        st.session_state.ppt = make_pptx(t_slides, t_topic)
                        st.session_state.ppt_name = f"{topic}.pptx"
                        st.session_state.ppt_st = "done"
                        st.rerun()
                    except Exception as e:
                        st.error(str(e))
        
        if st.button("🏠 Back"):
            st.session_state.mode = "chat"
            st.rerun()
    
    else:
        st.balloons()
        st.success("✅ Ready!")
        st.download_button("📥 Download", st.session_state.ppt, st.session_state.ppt_name, use_container_width=True)
        
        if st.button("🔄 Another"):
            st.session_state.ppt_st = "enter"
            st.rerun()
        if st.button("🏠 Back"):
            st.session_state.mode = "chat"
            st.rerun()


# CHAT
else:
    chat = st.session_state.chats[st.session_state.cid]
    
    # Badge
    if st.session_state.model == "shiva01":
        st.markdown('<span class="chat-badge b01">🔱 Shiva0.1</span>', unsafe_allow_html=True)
    else:
        st.markdown('<span class="chat-badge b02">🚀 Shiva0.2</span>', unsafe_allow_html=True)
    
    # Messages
    user_msgs = [m for m in chat["msgs"] if m["role"] == "user"]
    
    if not user_msgs:
        st.markdown('<div class="welcome-box"><h1 class="welcome-title">🔱 How can Shiva AI help?</h1></div>', unsafe_allow_html=True)
    else:
        for m in chat["msgs"]:
            if m["role"] == "system":
                continue
            with st.chat_message(m["role"]):
                st.markdown(m["content"])
                if m["role"] == "assistant" and m.get("audio"):
                    st.audio(m["audio"])
    
    st.markdown("---")
    
    # Voice
    if AR_OK:
        st.markdown("### 🎤 Voice")
        c1, c2 = st.columns([1, 4])
        with c1:
            aud = audio_recorder(text="", recording_color="#e74c3c", neutral_color="#2196F3", icon_size="2x")
        with c2:
            if aud:
                with st.spinner("Processing..."):
                    txt, err = transcribe(aud)
                    if txt:
                        st.success(f"📝 {txt}")
                        if st.button("📤 Send"):
                            if chat["title"] == "New Chat":
                                chat["title"] = txt[:25] + "..."
                            chat["msgs"].append({"role": "user", "content": txt})
                            save()
                            msgs = [{"role": "system", "content": SYSTEM}] + [{"role": m["role"], "content": m["content"]} for m in chat["msgs"][-10:] if m["role"] in ["user", "assistant"]]
                            resp = ai_response(msgs, st.session_state.model)
                            chat["msgs"].append({"role": "assistant", "content": resp, "audio": speak(resp)})
                            save()
                            st.rerun()
                    elif err:
                        st.error(err)
        st.markdown("---")
    
    # Files
    files = st.file_uploader("📎 Files", accept_multiple_files=True, type=['pdf', 'docx', 'txt', 'py', 'json', 'md'])
    
    if files:
        names = [f.name for f in files]
        if names != st.session_state.pfiles:
            st.session_state.pfiles = names
            for f in files:
                data = f.read()
                content = extract(data, f.name)
                if "files" not in chat:
                    chat["files"] = []
                if not any(x["name"] == f.name for x in chat["files"]):
                    chat["files"].append({"name": f.name, "content": content, "size": len(data)})
            save()
            st.rerun()
    
    if chat.get("files"):
        for i, f in enumerate(chat["files"]):
            c1, c2 = st.columns([6, 1])
            c1.write(f"📎 {f['name']}")
            if c2.button("❌", key=f"rf_{i}"):
                chat["files"] = [x for x in chat["files"] if x["name"] != f["name"]]
                save()
                st.rerun()
        st.markdown("---")
    
    # Input
    inp = st.chat_input("Ask Shiva AI...")
    
    if inp:
        if chat["title"] == "New Chat":
            chat["title"] = inp[:25] + "..."
        
        chat["msgs"].append({"role": "user", "content": inp})
        save()
        
        with st.chat_message("user"):
            st.markdown(inp)
        
        # Context
        ctx = ""
        if chat.get("files"):
            ctx = "\n[FILES]\n" + "\n".join([f"[{f['name']}]\n{f['content'][:2000]}" for f in chat["files"]]) + "\n[/FILES]\n\n"
        
        with st.chat_message("assistant"):
            ph = st.empty()
            nm = "Shiva0.1" if st.session_state.model == "shiva01" else "Shiva0.2"
            ph.markdown(f"🔱 {nm} thinking...")
            
            try:
                msgs = [{"role": "system", "content": SYSTEM}]
                recent = [m for m in chat["msgs"] if m["role"] in ["user", "assistant"]][-10:]
                for m in recent[:-1]:
                    msgs.append({"role": m["role"], "content": m["content"][:2000]})
                msgs.append({"role": "user", "content": ctx + inp if ctx else inp})
                resp = ai_response(msgs, st.session_state.model)
            except Exception as e:
                resp = f"Error: {e}"
            
            ph.markdown(resp)
            aud = speak(resp) if TTS_OK else None
            chat["msgs"].append({"role": "assistant", "content": resp, "audio": aud})
            save()
            if aud:
                st.audio(aud)
            st.rerun()


# Footer
st.markdown("---")
st.markdown('<div style="text-align:center;padding:15px;"><p><strong>🔱 Shiva AI</strong> - Made by Shivansh Mahajan</p></div>', unsafe_allow_html=True)
