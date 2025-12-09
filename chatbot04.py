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
    'deep_translator': 'deep-translator',
    'fpdf': 'fpdf',
    'speech_recognition': 'SpeechRecognition',
    'audio_recorder_streamlit': 'audio-recorder-streamlit'
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
    from docx.shared import Pt
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    DOCX_SUPPORT = True
except ImportError:
    DOCX_SUPPORT = False

try:
    import pptx
    PPTX_SUPPORT = True
except ImportError:
    install_package('python-pptx')
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

# FPDF for PDF generation
try:
    from fpdf import FPDF
    FPDF_AVAILABLE = True
except ImportError:
    install_package('fpdf')
    try:
        from fpdf import FPDF
        FPDF_AVAILABLE = True
    except ImportError:
        FPDF_AVAILABLE = False

# Speech Recognition
try:
    import speech_recognition as sr
    SPEECH_RECOGNITION_AVAILABLE = True
except ImportError:
    install_package('SpeechRecognition')
    try:
        import speech_recognition as sr
        SPEECH_RECOGNITION_AVAILABLE = True
    except ImportError:
        SPEECH_RECOGNITION_AVAILABLE = False

# Audio Recorder for Streamlit
try:
    from audio_recorder_streamlit import audio_recorder
    AUDIO_RECORDER_AVAILABLE = True
except ImportError:
    install_package('audio-recorder-streamlit')
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
    initial_sidebar_state="expanded"
)

# ----------------------
# Custom CSS
# ----------------------
st.markdown("""
<style>
    :root { color-scheme: light !important; }
    .stApp, .main, [data-testid="stAppViewContainer"] { background-color: #ffffff !important; }
    .stApp, .stApp * { color: #000000 !important; }
    [data-testid="stSidebar"], [data-testid="stSidebar"] > div, [data-testid="stSidebar"] * {
        background-color: #f8f9fa !important; color: #000000 !important;
    }
    h1, h2, h3, h4, h5, h6 { color: #000000 !important; }
    p, span, div, label, li, a { color: #000000 !important; }
    .stButton > button { background-color: #ffffff !important; color: #000000 !important; border: 1px solid #cccccc !important; }
    .stButton > button:hover { background-color: #f0f0f0 !important; }
    .stTextInput > div > div > input, .stTextArea > div > div > textarea {
        background-color: #ffffff !important; color: #000000 !important; border: 1px solid #cccccc !important;
    }
    .stSelectbox > div > div, [data-baseweb="select"] { background-color: #ffffff !important; color: #000000 !important; }
    [data-baseweb="menu"] li, [role="option"] { background-color: #ffffff !important; color: #000000 !important; }
    [data-baseweb="menu"] li:hover, [role="option"]:hover { background-color: #e8e8e8 !important; }
    .stChatMessage, [data-testid="stChatMessage"] { background-color: #f9f9f9 !important; border: 1px solid #e0e0e0 !important; }
    .stChatMessage *, [data-testid="stChatMessage"] * { color: #000000 !important; }
    .welcome-container { display: flex; justify-content: center; align-items: center; height: 60vh; }
    .welcome-title { font-size: 2.5rem; font-weight: 300; color: #000000 !important; text-align: center; }
    code, pre { background-color: #f5f5f5 !important; color: #000000 !important; }
    .stDownloadButton > button { background-color: #ffffff !important; color: #000000 !important; border: 1px solid #cccccc !important; }
    .streamlit-expanderHeader, [data-testid="stExpander"] * { background-color: #ffffff !important; color: #000000 !important; }
    .stCheckbox label, .stCheckbox span { color: #000000 !important; }
    .stSlider label, .stSlider p { color: #000000 !important; }
    .stRadio label { color: #000000 !important; }
    
    /* Model badge styling */
    .model-badge {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 15px;
        font-size: 12px;
        font-weight: bold;
        margin-bottom: 10px;
    }
    .model-shiva01 {
        background: linear-gradient(135deg, #ff9933, #ff6600);
        color: white !important;
    }
    .model-shiva02 {
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: white !important;
    }
</style>
""", unsafe_allow_html=True)

# ----------------------
# API Configuration
# ----------------------
# Sarvam API (Shiva0.1)
SARVAM_API_KEY = os.getenv("CHATBOT_API_KEY", "sk_h4gsam68_z6e2xo8u9aaleUaBshwjVyDk")
SARVAM_API_URL = "https://api.sarvam.ai/v1/chat/completions"
SARVAM_MODEL = "sarvam-m"

# Groq API (Shiva0.2)
GROQ_API_KEY = "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"
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL = "llama-3.1-8b-instant"

# Presentation API
PRESENTATION_API_KEY = "sk_u0xsaah7_pxzQfsbxtI4S7SsXlLLIsjaa"
PEXELS_API_KEY = "3Y3jiJZ6WAL49N6lPsdlRbRZ6IZBfHZFHP86dr9yZfxFYoxedLLlDKAC"

SYSTEM_PROMPT = (
    "You are Shiva AI, an advanced intelligent assistant created by Shivansh Mahajan. "
    "Provide helpful, accurate, and detailed responses. "
    "When files are provided, analyze them thoroughly and reference specific details. "
    "Be professional, clear, and comprehensive in your answers. "
    "Always provide complete responses - never cut off mid-sentence."
)

# Supported languages
SUPPORTED_LANGUAGES = {
    'en': 'English',
    'de': 'German',
    'fr': 'French',
    'es': 'Spanish'
}

# Flashcard Style Hints
FLASHCARD_STYLE_HINTS = {
    "qa": "Create Q&A flashcards with a clear question (front) and concise answer (back).",
    "cloze": "Create cloze deletion cards: wrap missing terms as {{term}} on the front; full sentence on the back.",
    "term-def": "Create term-definition pairs: single term on front, one-sentence definition on the back.",
    "mixed": "Mix Q&A, cloze, and term-definition styles appropriately."
}

# Model Display Names
MODEL_NAMES = {
    "shiva01": "🔱 Shiva0.1",
    "shiva02": "🚀 Shiva0.2 (better for languages)"
}

# Storage directory
STORAGE_DIR = Path("shiva_ai_data")
STORAGE_DIR.mkdir(exist_ok=True)


# ----------------------
# Speech Recognition Function
# ----------------------
def transcribe_audio(audio_bytes):
    """Convert audio bytes to text using speech recognition"""
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
            return None, "Could not understand audio. Please try again."
        except sr.RequestError as e:
            os.unlink(temp_audio_path)
            return None, f"Speech recognition service error: {str(e)}"
    
    except Exception as e:
        return None, f"Error processing audio: {str(e)}"


# ----------------------
# AI Chat Functions
# ----------------------
def get_ai_response_sarvam(messages, max_retries=3):
    """Get AI response using Sarvam API (Shiva0.1)"""
    headers = {
        "Authorization": f"Bearer {SARVAM_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": SARVAM_MODEL,
        "messages": messages,
        "max_tokens": 4096,
        "temperature": 0.7
    }
    
    for attempt in range(max_retries):
        try:
            response = requests.post(
                SARVAM_API_URL,
                headers=headers,
                json=payload,
                timeout=120
            )
            
            if response.status_code == 200:
                data = response.json()
                if "choices" in data and len(data["choices"]) > 0:
                    content = data["choices"][0].get("message", {}).get("content", "")
                    return content if content else "No response received."
                return "No response content found."
            
            elif response.status_code == 429:
                import time
                time.sleep(2 ** attempt)
                continue
            else:
                return f"⚠️ Shiva0.1 API Error {response.status_code}"
        
        except requests.exceptions.Timeout:
            if attempt < max_retries - 1:
                continue
            return "⚠️ Request timed out. Please try again."
        except Exception as e:
            return f"❌ Error: {str(e)}"
    
    return "⚠️ Failed after multiple attempts."


def get_ai_response_groq(messages, max_retries=3):
    """Get AI response using Groq API (Shiva0.2)"""
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": GROQ_MODEL,
        "messages": messages,
        "max_tokens": 4096,
        "temperature": 0.7
    }
    
    for attempt in range(max_retries):
        try:
            response = requests.post(
                GROQ_API_URL,
                headers=headers,
                json=payload,
                timeout=60
            )
            
            if response.status_code == 200:
                data = response.json()
                if "choices" in data and len(data["choices"]) > 0:
                    content = data["choices"][0].get("message", {}).get("content", "")
                    return content if content else "No response received."
                return "No response content found."
            
            elif response.status_code == 429:
                import time
                time.sleep(2 ** attempt)
                continue
            else:
                return f"⚠️ Shiva0.2 API Error {response.status_code}"
        
        except requests.exceptions.Timeout:
            if attempt < max_retries - 1:
                continue
            return "⚠️ Request timed out. Please try again."
        except Exception as e:
            return f"❌ Error: {str(e)}"
    
    return "⚠️ Failed after multiple attempts."


def get_ai_response(messages, model_choice="shiva02"):
    """Get AI response based on selected model"""
    if model_choice == "shiva01":
        return get_ai_response_sarvam(messages)
    else:
        return get_ai_response_groq(messages)


# ----------------------
# Flashcard Generator Function
# ----------------------
def generate_flashcards_from_text(
    text: str,
    n_cards: int = 20,
    style: str = "qa",
    focus: str = "balanced",
    include_mnemonics: bool = True,
    auto_tags: bool = True
):
    """Generate flashcards using Shiva0.2 (fast & reliable)"""
    
    system_prompt = f"""You are Shiva AI's flashcard creator, made by Shivansh Mahajan. Extract concepts using a {focus} focus.

Rules:
- Return ONLY a valid JSON array (no extra text)
- Each object must have: front, back, tags (array), mnemonic (string)
- Limit answers to 25 words or less
- Style: {FLASHCARD_STYLE_HINTS.get(style, FLASHCARD_STYLE_HINTS['qa'])}

Return format:
[
  {{"front": "Question?", "back": "Answer", "tags": ["tag1"], "mnemonic": "Memory tip"}}
]"""

    user_prompt = f"Generate exactly {n_cards} flashcards from this text. Return ONLY JSON:\n\n{text}"

    payload = {
        "model": GROQ_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "max_tokens": 4000,
        "temperature": 0.7
    }

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    response = requests.post(GROQ_API_URL, headers=headers, json=payload, timeout=120)
    response.raise_for_status()

    content = response.json()["choices"][0]["message"]["content"].strip()

    # Clean JSON
    if "```json" in content:
        content = content.split("```json")[1]
    if "```" in content:
        content = content.split("```")[0]
    content = content.strip()

    start_idx = content.find("[")
    end_idx = content.rfind("]") + 1
    if start_idx != -1 and end_idx > start_idx:
        content = content[start_idx:end_idx]

    data = json.loads(content)

    cards = []
    for card_data in data:
        front = str(card_data.get("front", "")).strip()
        back = str(card_data.get("back", "")).strip()
        tags = card_data.get("tags") or []
        mnemonic = str(card_data.get("mnemonic", "")).strip()
        
        if front and back:
            cards.append({
                "front": front,
                "back": back,
                "tags": tags if isinstance(tags, list) else [tags],
                "mnemonic": mnemonic
            })

    return cards


# ----------------------
# Flashcard Export Functions
# ----------------------
def create_flashcard_text_file(cards):
    """Create text file from flashcards."""
    text_content = "=" * 60 + "\n"
    text_content += "        FLASHCARDS - Made by Shiva AI\n"
    text_content += "        Created by Shivansh Mahajan\n"
    text_content += "=" * 60 + "\n\n"
    
    for i, card in enumerate(cards, start=1):
        text_content += f"CARD {i}\n"
        text_content += "-" * 40 + "\n"
        text_content += f"FRONT: {card['front']}\n\n"
        text_content += f"BACK: {card['back']}\n\n"
        if card['tags']:
            text_content += f"TAGS: {', '.join(card['tags'])}\n"
        if card['mnemonic']:
            text_content += f"MNEMONIC: {card['mnemonic']}\n"
        text_content += "\n" + "=" * 60 + "\n\n"
    
    text_content += f"Total Cards: {len(cards)}\n"
    text_content += "Made by Shiva AI - Created by Shivansh Mahajan\n"
    
    return text_content


def create_flashcard_word_file(cards):
    """Create Word document from flashcards."""
    if not DOCX_SUPPORT:
        return None
    
    try:
        doc = Document()
        
        title = doc.add_heading("Flashcards - Made by Shiva AI", 0)
        title.alignment = WD_ALIGN_PARAGRAPH.CENTER
        
        subtitle = doc.add_paragraph("Created by Shivansh Mahajan")
        subtitle.alignment = WD_ALIGN_PARAGRAPH.CENTER
        
        doc.add_paragraph()
        
        for i, card in enumerate(cards, start=1):
            doc.add_heading(f"Card {i}", level=1)
            
            doc.add_heading("Front (Question):", level=2)
            doc.add_paragraph(card['front'])
            
            doc.add_heading("Back (Answer):", level=2)
            doc.add_paragraph(card['back'])
            
            if card['tags']:
                tags_para = doc.add_paragraph()
                tags_para.add_run("Tags: ").bold = True
                tags_para.add_run(", ".join(card['tags']))
            
            if card['mnemonic']:
                mnemonic_para = doc.add_paragraph()
                mnemonic_para.add_run("Mnemonic: ").bold = True
                mnemonic_para.add_run(card['mnemonic'])
            
            doc.add_paragraph("_" * 50)
            doc.add_paragraph()
        
        footer = doc.add_paragraph()
        footer.add_run(f"Total Cards: {len(cards)}").bold = True
        doc.add_paragraph("Made by Shiva AI - Created by Shivansh Mahajan")
        
        buffer = io.BytesIO()
        doc.save(buffer)
        buffer.seek(0)
        return buffer
    except Exception:
        return None


def create_flashcard_pdf_file(cards):
    """Create PDF from flashcards."""
    if not FPDF_AVAILABLE:
        return None
    
    try:
        class FlashcardPDF(FPDF):
            def header(self):
                self.set_font('Arial', 'B', 14)
                self.cell(0, 10, 'Flashcards - Made by Shiva AI', 0, 1, 'C')
                self.set_font('Arial', 'I', 10)
                self.cell(0, 5, 'Created by Shivansh Mahajan', 0, 1, 'C')
                self.ln(5)
            
            def footer(self):
                self.set_y(-15)
                self.set_font('Arial', 'I', 8)
                self.cell(0, 10, f'Page {self.page_no()} | Made by Shiva AI', 0, 0, 'C')
        
        pdf = FlashcardPDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()
        pdf.set_font('Arial', '', 11)
        
        for i, card in enumerate(cards, start=1):
            if pdf.get_y() > 240:
                pdf.add_page()
            
            pdf.set_font('Arial', 'B', 14)
            pdf.set_fill_color(230, 230, 230)
            pdf.cell(0, 10, f'Card {i}', 0, 1, 'L', True)
            pdf.ln(2)
            
            pdf.set_font('Arial', 'B', 11)
            pdf.cell(0, 8, 'Front (Question):', 0, 1)
            pdf.set_font('Arial', '', 11)
            
            front_text = card['front']
            try:
                front_text = front_text.encode('latin-1', 'replace').decode('latin-1')
            except:
                front_text = ''.join(c if ord(c) < 256 else '?' for c in front_text)
            pdf.multi_cell(0, 6, front_text)
            pdf.ln(3)
            
            pdf.set_font('Arial', 'B', 11)
            pdf.cell(0, 8, 'Back (Answer):', 0, 1)
            pdf.set_font('Arial', '', 11)
            
            back_text = card['back']
            try:
                back_text = back_text.encode('latin-1', 'replace').decode('latin-1')
            except:
                back_text = ''.join(c if ord(c) < 256 else '?' for c in back_text)
            pdf.multi_cell(0, 6, back_text)
            pdf.ln(3)
            
            if card['tags']:
                pdf.set_font('Arial', 'B', 10)
                pdf.cell(15, 6, 'Tags: ', 0, 0)
                pdf.set_font('Arial', '', 10)
                tags_text = ", ".join(card['tags'])
                try:
                    tags_text = tags_text.encode('latin-1', 'replace').decode('latin-1')
                except:
                    pass
                pdf.cell(0, 6, tags_text, 0, 1)
            
            if card['mnemonic']:
                pdf.set_font('Arial', 'B', 10)
                pdf.cell(22, 6, 'Mnemonic: ', 0, 0)
                pdf.set_font('Arial', 'I', 10)
                mnemonic_text = card['mnemonic']
                try:
                    mnemonic_text = mnemonic_text.encode('latin-1', 'replace').decode('latin-1')
                except:
                    pass
                pdf.multi_cell(0, 6, mnemonic_text)
            
            pdf.ln(3)
            pdf.set_draw_color(180, 180, 180)
            pdf.line(10, pdf.get_y(), 200, pdf.get_y())
            pdf.ln(8)
        
        pdf.ln(5)
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(0, 10, f'Total Cards: {len(cards)}', 0, 1, 'C')
        
        buffer = io.BytesIO()
        pdf_output = pdf.output(dest='S').encode('latin-1')
        buffer.write(pdf_output)
        buffer.seek(0)
        return buffer
    
    except Exception as e:
        st.error(f"PDF Error: {e}")
        return None


# ----------------------
# Pexels Image Functions
# ----------------------
def search_pexels_image(query):
    """Search for an image on Pexels."""
    try:
        url = "https://api.pexels.com/v1/search"
        headers = {"Authorization": PEXELS_API_KEY}
        params = {"query": query, "per_page": 1, "orientation": "landscape"}
        
        response = requests.get(url, headers=headers, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get("photos") and len(data["photos"]) > 0:
                return data["photos"][0]["src"].get("large")
        return None
    except:
        return None


def download_image(url):
    """Download image from URL."""
    try:
        response = requests.get(url, timeout=15)
        if response.status_code == 200:
            img_data = io.BytesIO(response.content)
            if PIL_AVAILABLE:
                from PIL import Image as PILImage
                img = PILImage.open(img_data)
                if img.mode in ('RGBA', 'P'):
                    img = img.convert('RGB')
                output = io.BytesIO()
                img.save(output, format='JPEG', quality=90)
                output.seek(0)
                return output
            return img_data
        return None
    except:
        return None


def generate_image_keywords(title):
    """Generate search keywords from slide title."""
    stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'from', 'is', 'are'}
    words = title.lower().split()
    keywords = [w for w in words if w not in stop_words and len(w) > 2]
    return ' '.join(keywords[:3]) if keywords else title


# ----------------------
# Presentation Generator Functions
# ----------------------
def generate_english_presentation(topic, slide_count):
    """Generate presentation content using Shiva0.1."""
    headers = {"Authorization": f"Bearer {PRESENTATION_API_KEY}", "Content-Type": "application/json"}
    prompt = f"""You are Shiva AI. Generate a {slide_count}-slide presentation for: '{topic}'.
Return a JSON array with "title" and "content" (3-4 bullet points separated by newlines).
Only return the JSON array."""
    
    payload = {
        "model": "sarvam-m",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 4096
    }
    
    response = requests.post(SARVAM_API_URL, headers=headers, json=payload, timeout=120)
    response.raise_for_status()
    response_text = response.json()["choices"][0]["message"]["content"]
    
    # Clean JSON
    if "```json" in response_text:
        response_text = response_text.split("```json")[1]
    if "```" in response_text:
        response_text = response_text.split("```")[0]
    response_text = response_text.strip()
    
    start_idx = response_text.find("[")
    end_idx = response_text.rfind("]") + 1
    if start_idx != -1 and end_idx > start_idx:
        response_text = response_text[start_idx:end_idx]
    
    return json.loads(response_text)


def translate_content(text, target_lang):
    """Translate text using Google Translate."""
    if not text.strip() or target_lang == 'en' or not TRANSLATE_SUPPORT:
        return text
    try:
        translator = GoogleTranslator(source='en', target=target_lang)
        return translator.translate(text)
    except:
        return text


def create_powerpoint_presentation(slides, topic, target_lang_name, include_images=True, progress_callback=None):
    """Create PowerPoint presentation."""
    from pptx import Presentation
    from pptx.util import Inches, Pt
    from pptx.dml.color import RGBColor
    from pptx.enum.text import PP_ALIGN
    
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    
    # Title slide
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    
    if include_images:
        img_url = search_pexels_image(topic)
        if img_url:
            img_data = download_image(img_url)
            if img_data:
                try:
                    slide.shapes.add_picture(img_data, Inches(0), Inches(0), width=prs.slide_width, height=prs.slide_height)
                except:
                    pass
    
    # Overlay
    overlay = slide.shapes.add_shape(1, Inches(0), Inches(0), prs.slide_width, prs.slide_height)
    overlay.fill.solid()
    overlay.fill.fore_color.rgb = RGBColor(0, 0, 0)
    overlay.line.fill.background()
    
    # Title text
    title_box = slide.shapes.add_textbox(Inches(0.5), Inches(2.5), Inches(12.333), Inches(1.5))
    title_para = title_box.text_frame.paragraphs[0]
    title_para.text = topic
    title_para.font.size = Pt(54)
    title_para.font.bold = True
    title_para.font.color.rgb = RGBColor(255, 255, 255)
    title_para.alignment = PP_ALIGN.CENTER
    
    # Subtitle
    subtitle_box = slide.shapes.add_textbox(Inches(0.5), Inches(4.2), Inches(12.333), Inches(0.8))
    subtitle_para = subtitle_box.text_frame.paragraphs[0]
    subtitle_para.text = f"Made by Shiva AI in {target_lang_name}"
    subtitle_para.font.size = Pt(24)
    subtitle_para.font.color.rgb = RGBColor(200, 200, 200)
    subtitle_para.alignment = PP_ALIGN.CENTER
    
    # Content slides
    for idx, slide_data in enumerate(slides):
        if progress_callback:
            progress_callback(f"Creating slide {idx + 1}...")
        
        content_slide = prs.slides.add_slide(prs.slide_layouts[6])
        
        # Left bar
        left_bar = content_slide.shapes.add_shape(1, Inches(0), Inches(0), Inches(0.15), prs.slide_height)
        left_bar.fill.solid()
        left_bar.fill.fore_color.rgb = RGBColor(0, 120, 215)
        left_bar.line.fill.background()
        
        # Title
        title_box = content_slide.shapes.add_textbox(Inches(0.4), Inches(0.5), Inches(12), Inches(1))
        title_para = title_box.text_frame.paragraphs[0]
        title_para.text = slide_data['title']
        title_para.font.size = Pt(36)
        title_para.font.bold = True
        title_para.font.color.rgb = RGBColor(0, 0, 0)
        
        # Content
        content_box = content_slide.shapes.add_textbox(Inches(0.4), Inches(1.7), Inches(12), Inches(5.3))
        content_frame = content_box.text_frame
        content_frame.word_wrap = True
        
        content_lines = slide_data.get('content', '').split('\n')
        for i, line in enumerate(content_lines):
            line = line.strip().lstrip('•-*● ')
            if not line:
                continue
            para = content_frame.paragraphs[0] if i == 0 else content_frame.add_paragraph()
            para.text = f"● {line}"
            para.font.size = Pt(20)
            para.font.color.rgb = RGBColor(50, 50, 50)
    
    # Thank you slide
    thank_slide = prs.slides.add_slide(prs.slide_layouts[6])
    thank_box = thank_slide.shapes.add_textbox(Inches(0.5), Inches(2.5), Inches(12.333), Inches(1.5))
    thank_para = thank_box.text_frame.paragraphs[0]
    thank_para.text = "Thank You!"
    thank_para.font.size = Pt(72)
    thank_para.font.bold = True
    thank_para.alignment = PP_ALIGN.CENTER
    
    footer_box = thank_slide.shapes.add_textbox(Inches(0.5), Inches(4.5), Inches(12.333), Inches(0.8))
    footer_para = footer_box.text_frame.paragraphs[0]
    footer_para.text = "Made by Shiva AI"
    footer_para.font.size = Pt(28)
    footer_para.alignment = PP_ALIGN.CENTER
    
    ppt_stream = io.BytesIO()
    prs.save(ppt_stream)
    ppt_stream.seek(0)
    return ppt_stream


# ----------------------
# Helper Functions
# ----------------------
def get_user_id():
    if "user_id" not in st.session_state:
        st.session_state.user_id = str(uuid.uuid4())
    return st.session_state.user_id


def get_user_sessions_file():
    return STORAGE_DIR / f"user_{get_user_id()}_sessions.pkl"


def save_sessions():
    try:
        with open(get_user_sessions_file(), 'wb') as f:
            sessions_to_save = {}
            for sid, sdata in st.session_state.chat_sessions.items():
                sessions_to_save[sid] = {
                    "messages": [{k: v for k, v in m.items() if k != "audio_file"} for m in sdata["messages"]],
                    "files": sdata.get("files", []),
                    "title": sdata["title"],
                    "created": sdata["created"]
                }
            pickle.dump(sessions_to_save, f)
    except:
        pass


def load_sessions():
    try:
        sessions_file = get_user_sessions_file()
        if sessions_file.exists():
            with open(sessions_file, 'rb') as f:
                return pickle.load(f)
    except:
        pass
    return None


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
        tts = gTTS(text[:1000], lang="en")
        audio_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
        tts.save(audio_file.name)
        return audio_file.name
    except:
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
        '.pdf': '📕', '.doc': '📘', '.docx': '📘', '.xls': '📊', '.xlsx': '📊',
        '.ppt': '📊', '.pptx': '📊', '.txt': '📄', '.csv': '📊', '.json': '🔧',
        '.py': '🐍', '.js': '💛', '.html': '🌐', '.css': '🎨',
        '.png': '🖼️', '.jpg': '🖼️', '.jpeg': '🖼️', '.gif': '🖼️'
    }
    return icons.get(ext.lower(), '📎')


# ----------------------
# File Processing Functions
# ----------------------
def extract_text_from_pdf(file_bytes):
    try:
        pdf = PyPDF2.PdfReader(io.BytesIO(file_bytes))
        text = [page.extract_text() for page in pdf.pages if page.extract_text()]
        return "\n".join(text) or "PDF is empty."
    except Exception as e:
        return f"PDF error: {e}"


def extract_text_from_docx(file_bytes):
    try:
        doc = Document(io.BytesIO(file_bytes))
        text = [p.text for p in doc.paragraphs if p.text.strip()]
        return "\n".join(text) or "Document is empty."
    except Exception as e:
        return f"DOCX error: {e}"


@st.cache_data
def extract_file_content(file_bytes, filename):
    ext = Path(filename).suffix.lower()
    try:
        if ext == '.pdf' and PDF_SUPPORT:
            return extract_text_from_pdf(file_bytes)
        elif ext in ['.docx', '.doc'] and DOCX_SUPPORT:
            return extract_text_from_docx(file_bytes)
        elif ext in ['.txt', '.py', '.js', '.html', '.css', '.json', '.md', '.csv']:
            return file_bytes.decode('utf-8', errors='ignore')
        else:
            return f"[File: {filename}]"
    except:
        return f"[File: {filename}]"


# ----------------------
# Session State Initialization
# ----------------------
get_user_id()

if "app_mode" not in st.session_state:
    st.session_state.app_mode = "chat"

if "ppt_stage" not in st.session_state:
    st.session_state.ppt_stage = 'enter_details'

if "flashcard_stage" not in st.session_state:
    st.session_state.flashcard_stage = 'enter_text'

if "generated_flashcards" not in st.session_state:
    st.session_state.generated_flashcards = []

if "selected_model" not in st.session_state:
    st.session_state.selected_model = "shiva02"

if "chat_sessions" not in st.session_state:
    loaded_sessions = load_sessions()
    if loaded_sessions:
        st.session_state.chat_sessions = loaded_sessions
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
    st.session_state.current_session_id = list(st.session_state.chat_sessions.keys())[0]

if "last_processed_files" not in st.session_state:
    st.session_state.last_processed_files = []


# ----------------------
# Sidebar
# ----------------------
with st.sidebar:
    st.markdown("## 🔱 Shiva AI")
    st.markdown("*Made by Shivansh Mahajan*")
    st.markdown("---")
    
    # Model Selection
    st.markdown("### 🧠 Select Model")
    model_choice = st.radio(
        "Choose AI Model:",
        ["shiva01", "shiva02"],
        format_func=lambda x: "🔱 Shiva0.1" if x == "shiva01" else "🚀 Shiva0.2 (better for languages)",
        key="model_selector",
        index=1 if st.session_state.selected_model == "shiva02" else 0
    )
    st.session_state.selected_model = model_choice
    
    # Model description
    if model_choice == "shiva01":
        st.caption("🇮🇳 Indian AI model - Good for Hindi & regional languages")
    else:
        st.caption("⚡ Fast & powerful - Best for multiple languages")
    
    st.markdown("---")
    
    if st.button("✨ New Chat", key="new_chat", use_container_width=True):
        st.session_state.app_mode = "chat"
        create_new_chat()
        st.rerun()
    
    if st.button("📊 Create Presentation", key="create_ppt", use_container_width=True):
        st.session_state.app_mode = "presentation"
        st.session_state.ppt_stage = 'enter_details'
        st.rerun()
    
    if st.button("📚 Create Flashcards", key="create_flashcards", use_container_width=True):
        st.session_state.app_mode = "flashcards"
        st.session_state.flashcard_stage = 'enter_text'
        st.rerun()
    
    st.markdown("---")
    
    if st.session_state.app_mode == "chat":
        st.markdown("### 💬 Chats")
        
        sorted_sessions = sorted(
            st.session_state.chat_sessions.items(),
            key=lambda x: x[1].get("created", ""),
            reverse=True
        )
        
        for session_id, session_data in sorted_sessions:
            col1, col2 = st.columns([5, 1])
            with col1:
                btn_label = session_data["title"]
                if session_id == st.session_state.current_session_id:
                    btn_label = f"▶ {btn_label}"
                if st.button(btn_label, key=f"chat_{session_id}", use_container_width=True):
                    st.session_state.current_session_id = session_id
                    st.session_state.app_mode = "chat"
                    st.rerun()
            with col2:
                if st.button("🗑️", key=f"del_{session_id}"):
                    if delete_chat(session_id):
                        st.rerun()
    
    elif st.session_state.app_mode == "presentation":
        st.markdown("### 📊 Presentation")
        st.markdown("*Made by Shiva AI*")
    
    elif st.session_state.app_mode == "flashcards":
        st.markdown("### 📚 Flashcards")
        st.markdown("*Made by Shiva AI*")


# ----------------------
# Main Content Area
# ----------------------

# FLASHCARD MODE
if st.session_state.app_mode == "flashcards":
    st.title("📚 AI Flashcard Generator")
    st.markdown("*Made by Shiva AI - Created by Shivansh Mahajan*")
    st.markdown("---")
    
    if st.session_state.flashcard_stage == 'enter_text':
        text_input = st.text_area("📝 Paste your text here:", height=250, key="flashcard_text_input")
        
        col1, col2 = st.columns(2)
        with col1:
            num_cards = st.slider("Number of Flashcards", 5, 30, 10)
            style = st.selectbox("Card Style", ["qa", "cloze", "term-def", "mixed"])
        with col2:
            focus = st.selectbox("Focus", ["balanced", "key-concepts", "definitions"])
            include_mnemonics = st.checkbox("💡 Include Mnemonics", True)
        
        col_btn1, col_btn2 = st.columns([3, 1])
        with col_btn1:
            if st.button("🚀 Generate Flashcards", type="primary", use_container_width=True):
                if not text_input or len(text_input.strip()) < 50:
                    st.error("Please enter at least 50 characters.")
                else:
                    with st.spinner("🔱 Generating flashcards with Shiva0.2..."):
                        try:
                            cards = generate_flashcards_from_text(text_input, num_cards, style, focus, include_mnemonics)
                            if cards:
                                st.session_state.generated_flashcards = cards
                                st.session_state.flashcard_stage = 'view_cards'
                                st.rerun()
                        except Exception as e:
                            st.error(f"Error: {e}")
        with col_btn2:
            if st.button("🏠 Back", use_container_width=True):
                st.session_state.app_mode = "chat"
                st.rerun()
    
    elif st.session_state.flashcard_stage == 'view_cards':
        cards = st.session_state.generated_flashcards
        st.balloons()
        st.success(f"✅ Generated {len(cards)} flashcards!")
        
        for i, card in enumerate(cards, 1):
            with st.expander(f"📝 Card {i}: {card['front'][:50]}..."):
                col_a, col_b = st.columns(2)
                with col_a:
                    st.info(f"**Front:** {card['front']}")
                with col_b:
                    st.success(f"**Back:** {card['back']}")
                if card['tags']:
                    st.write(f"**Tags:** {', '.join(card['tags'])}")
                if card['mnemonic']:
                    st.write(f"**Mnemonic:** {card['mnemonic']}")
        
        st.markdown("### 📥 Download")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.download_button("📄 TEXT", create_flashcard_text_file(cards), "flashcards.txt", use_container_width=True)
        
        with col2:
            word_file = create_flashcard_word_file(cards)
            if word_file:
                st.download_button("📘 WORD", word_file, "flashcards.docx", 
                                   mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                                   use_container_width=True)
        
        with col3:
            pdf_file = create_flashcard_pdf_file(cards)
            if pdf_file:
                st.download_button("📕 PDF", pdf_file, "flashcards.pdf", mime="application/pdf", use_container_width=True)
            else:
                st.button("📕 PDF (error)", disabled=True, use_container_width=True)
        
        col_a, col_b = st.columns(2)
        with col_a:
            if st.button("🔄 Create More", use_container_width=True):
                st.session_state.flashcard_stage = 'enter_text'
                st.rerun()
        with col_b:
            if st.button("🏠 Back to Chat", use_container_width=True):
                st.session_state.app_mode = "chat"
                st.rerun()


# PRESENTATION MODE
elif st.session_state.app_mode == "presentation":
    st.title("📊 AI Presentation Generator")
    st.markdown("*Made by Shiva AI*")
    
    if st.session_state.ppt_stage == 'enter_details':
        topic = st.text_input("Presentation topic:")
        language = st.selectbox("Language", list(SUPPORTED_LANGUAGES.keys()), format_func=lambda x: SUPPORTED_LANGUAGES[x])
        slide_count = st.slider("Slides", 2, 10, 5)
        include_images = st.checkbox("🖼️ Include images", True)
        
        col1, col2 = st.columns([3, 1])
        with col1:
            if st.button("🚀 Build Presentation", type="primary", use_container_width=True):
                if topic:
                    with st.spinner("Creating presentation with Shiva0.1..."):
                        try:
                            slides = generate_english_presentation(topic, slide_count)
                            translated_topic = translate_content(topic, language)
                            translated_slides = [
                                {'title': translate_content(s['title'], language),
                                 'content': translate_content(s['content'], language)}
                                for s in slides
                            ]
                            ppt = create_powerpoint_presentation(translated_slides, translated_topic, SUPPORTED_LANGUAGES[language], include_images)
                            st.session_state.ppt_file = ppt
                            st.session_state.ppt_file_name = f"{topic}_shiva_ai.pptx"
                            st.session_state.ppt_stage = 'download'
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error: {e}")
        with col2:
            if st.button("🏠 Back", use_container_width=True):
                st.session_state.app_mode = "chat"
                st.rerun()
    
    elif st.session_state.ppt_stage == 'download':
        st.balloons()
        st.success("✅ Presentation ready!")
        st.download_button("📥 Download PPTX", st.session_state.ppt_file, st.session_state.ppt_file_name,
                          mime="application/vnd.openxmlformats-officedocument.presentationml.presentation")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Create Another", use_container_width=True):
                st.session_state.ppt_stage = 'enter_details'
                st.rerun()
        with col2:
            if st.button("🏠 Back to Chat", use_container_width=True):
                st.session_state.app_mode = "chat"
                st.rerun()


# CHAT MODE
else:
    current_session = get_current_session()
    user_messages = [m for m in current_session["messages"] if m["role"] == "user"]

    # Show model indicator
    if st.session_state.selected_model == "shiva01":
        st.markdown('<span class="model-badge model-shiva01">🔱 Shiva0.1</span>', unsafe_allow_html=True)
    else:
        st.markdown('<span class="model-badge model-shiva02">🚀 Shiva0.2</span>', unsafe_allow_html=True)

    if not user_messages:
        st.markdown("""
            <div class="welcome-container">
                <h1 class="welcome-title">🔱 What can Shiva AI help with?</h1>
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

    # Voice Input Section
    if AUDIO_RECORDER_AVAILABLE:
        st.markdown("### 🎤 Voice Input")
        col_voice1, col_voice2 = st.columns([1, 4])
        
        with col_voice1:
            audio_bytes = audio_recorder(
                text="",
                recording_color="#e74c3c",
                neutral_color="#3498db",
                icon_name="microphone",
                icon_size="2x",
                pause_threshold=2.0,
                sample_rate=16000
            )
        
        with col_voice2:
            if audio_bytes:
                with st.spinner("🔊 Transcribing..."):
                    transcribed_text, error = transcribe_audio(audio_bytes)
                    
                    if transcribed_text:
                        st.success(f"📝 **{transcribed_text}**")
                        
                        if st.button("📤 Send Voice Message", key="send_voice"):
                            if current_session["title"] == "New Chat":
                                current_session["title"] = generate_chat_title(transcribed_text)
                            
                            current_session["messages"].append({"role": "user", "content": transcribed_text})
                            save_sessions()
                            
                            # Get AI response
                            messages_for_api = [{"role": "system", "content": SYSTEM_PROMPT}]
                            recent = [m for m in current_session["messages"] if m["role"] in ["user", "assistant"]][-10:]
                            messages_for_api.extend([{"role": m["role"], "content": m["content"]} for m in recent])
                            
                            response = get_ai_response(messages_for_api, st.session_state.selected_model)
                            
                            current_session["messages"].append({
                                "role": "assistant",
                                "content": response,
                                "audio_file": speak_text(response)
                            })
                            save_sessions()
                            st.rerun()
                    elif error:
                        st.error(f"❌ {error}")
        
        st.markdown("---")

    # File Upload
    col1, col2 = st.columns([3, 1])
    with col1:
        uploaded_files = st.file_uploader(
            "📎 Attach files", 
            accept_multiple_files=True,
            type=['pdf', 'docx', 'txt', 'py', 'js', 'html', 'css', 'json', 'md', 'csv', 'png', 'jpg', 'jpeg']
        )
    with col2:
        if current_session.get("files"):
            if st.button("🗑️ Clear Files", use_container_width=True):
                current_session["files"] = []
                st.session_state.last_processed_files = []
                st.rerun()

    if uploaded_files:
        current_file_names = [f.name for f in uploaded_files]
        if current_file_names != st.session_state.last_processed_files:
            st.session_state.last_processed_files = current_file_names
            
            with st.spinner("Processing..."):
                for f in uploaded_files:
                    file_bytes = f.read()
                    content = extract_file_content(file_bytes, f.name)
                    
                    if not any(x['filename'] == f.name for x in current_session.get("files", [])):
                        if "files" not in current_session:
                            current_session["files"] = []
                        current_session["files"].append({
                            'filename': f.name,
                            'content': content,
                            'size': len(file_bytes),
                            'type': Path(f.name).suffix.upper()[1:] or 'FILE',
                            'icon': get_file_icon(Path(f.name).suffix)
                        })
            save_sessions()
            st.rerun()

    if current_session.get("files"):
        st.markdown("#### 📁 Files")
        for idx, f in enumerate(current_session["files"]):
            col1, col2, col3 = st.columns([0.5, 4, 0.5])
            with col1:
                st.write(f.get('icon', '📎'))
            with col2:
                st.write(f"**{f['filename']}** ({format_file_size(f['size'])})")
            with col3:
                if st.button("❌", key=f"rm_{idx}"):
                    remove_file(f['filename'])
                    st.rerun()
        st.markdown("---")

    # Chat Input
    user_message = st.chat_input("Ask Shiva AI anything...")

    if user_message:
        if current_session["title"] == "New Chat":
            current_session["title"] = generate_chat_title(user_message)
        
        current_session["messages"].append({"role": "user", "content": user_message})
        save_sessions()
        
        with st.chat_message("user"):
            st.markdown(user_message)
        
        # Build context
        files_context = ""
        if current_session.get("files"):
            files_context = "\n\n=== FILES ===\n"
            for f in current_session["files"]:
                files_context += f"\n[{f['filename']}]\n{f['content'][:5000]}\n"
            files_context += "=== END ===\n\n"
        
        with st.chat_message("assistant"):
            placeholder = st.empty()
            model_name = "Shiva0.1" if st.session_state.selected_model == "shiva01" else "Shiva0.2"
            placeholder.markdown(f"🔱 {model_name} is thinking...")
            
            try:
                messages_for_api = [{"role": "system", "content": SYSTEM_PROMPT}]
                recent = [m for m in current_session["messages"] if m["role"] in ["user", "assistant"]][-10:]
                
                for m in recent[:-1]:
                    messages_for_api.append({"role": m["role"], "content": m["content"][:2000]})
                
                user_content = files_context + user_message if files_context else user_message
                messages_for_api.append({"role": "user", "content": user_content})
                
                response_text = get_ai_response(messages_for_api, st.session_state.selected_model)
                
            except Exception as e:
                response_text = f"❌ Error: {str(e)}"
            
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


# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; padding: 20px;'>"
    "<p>🔱 <strong>Shiva AI</strong> - Made by Shivansh Mahajan</p>"
    "</div>",
    unsafe_allow_html=True
)

