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
# Custom CSS for White Theme with Black Text
# ----------------------
st.markdown("""
<style>
    /* Force light theme */
    :root {
        color-scheme: light !important;
    }
    
    /* Main app background */
    .stApp, .main, [data-testid="stAppViewContainer"] {
        background-color: #ffffff !important;
    }
    
    /* All text black */
    .stApp, .stApp * {
        color: #000000 !important;
    }
    
    /* Sidebar */
    [data-testid="stSidebar"], 
    [data-testid="stSidebar"] > div,
    [data-testid="stSidebar"] * {
        background-color: #f8f9fa !important;
        color: #000000 !important;
    }
    
    /* Headers */
    h1, h2, h3, h4, h5, h6,
    .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
        color: #000000 !important;
    }
    
    /* Paragraphs and text */
    p, span, div, label, li, a {
        color: #000000 !important;
    }
    
    /* Buttons */
    .stButton > button,
    button[kind="primary"],
    button[kind="secondary"],
    [data-testid="stSidebar"] button {
        background-color: #ffffff !important;
        color: #000000 !important;
        border: 1px solid #cccccc !important;
    }
    
    .stButton > button:hover,
    button:hover {
        background-color: #f0f0f0 !important;
        color: #000000 !important;
        border: 1px solid #999999 !important;
    }
    
    /* Text inputs */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    input[type="text"],
    textarea {
        background-color: #ffffff !important;
        color: #000000 !important;
        border: 1px solid #cccccc !important;
    }
    
    /* SELECT BOXES / DROPDOWNS - Main fix */
    .stSelectbox > div > div,
    .stSelectbox > div > div > div,
    .stSelectbox [data-baseweb="select"],
    .stSelectbox [data-baseweb="select"] > div,
    [data-baseweb="select"],
    [data-baseweb="popover"],
    [data-baseweb="menu"],
    [role="listbox"],
    [role="option"] {
        background-color: #ffffff !important;
        color: #000000 !important;
    }
    
    /* Dropdown selected value */
    .stSelectbox > div > div > div > div,
    [data-baseweb="select"] > div > div > div {
        background-color: #ffffff !important;
        color: #000000 !important;
    }
    
    /* Dropdown menu items */
    [data-baseweb="menu"] li,
    [data-baseweb="menu"] div,
    [role="option"],
    [role="option"] div,
    ul[role="listbox"] li {
        background-color: #ffffff !important;
        color: #000000 !important;
    }
    
    /* Dropdown hover state */
    [data-baseweb="menu"] li:hover,
    [role="option"]:hover,
    [data-highlighted="true"] {
        background-color: #e8e8e8 !important;
        color: #000000 !important;
    }
    
    /* Dropdown arrow/icon */
    .stSelectbox svg,
    [data-baseweb="select"] svg {
        fill: #000000 !important;
        color: #000000 !important;
    }
    
    /* Slider */
    .stSlider > div > div > div,
    .stSlider label,
    .stSlider p {
        color: #000000 !important;
    }
    
    /* Checkbox */
    .stCheckbox label,
    .stCheckbox span {
        color: #000000 !important;
    }
    
    /* Chat messages */
    .stChatMessage,
    [data-testid="stChatMessage"] {
        background-color: #f9f9f9 !important;
        border: 1px solid #e0e0e0 !important;
        color: #000000 !important;
    }
    
    .stChatMessage *,
    [data-testid="stChatMessage"] * {
        color: #000000 !important;
    }
    
    /* Chat input */
    .stChatInputContainer,
    .stChatInputContainer > div,
    .stChatInputContainer input,
    .stChatInputContainer textarea,
    [data-testid="stChatInput"],
    [data-testid="stChatInput"] * {
        background-color: #ffffff !important;
        color: #000000 !important;
        border-color: #cccccc !important;
    }
    
    /* File uploader */
    .stFileUploader,
    [data-testid="stFileUploader"],
    [data-testid="stFileUploader"] * {
        background-color: #f8f9fa !important;
        color: #000000 !important;
    }
    
    .stFileUploader label,
    .stFileUploader section {
        background-color: #f8f9fa !important;
        color: #000000 !important;
        border: 1px dashed #cccccc !important;
    }
    
    /* Expander */
    .streamlit-expanderHeader,
    .streamlit-expanderContent,
    [data-testid="stExpander"],
    [data-testid="stExpander"] * {
        background-color: #ffffff !important;
        color: #000000 !important;
    }
    
    /* Code blocks */
    code, pre, .stCodeBlock {
        background-color: #f5f5f5 !important;
        color: #000000 !important;
    }
    
    /* Info, warning, error, success boxes */
    .stAlert,
    [data-testid="stAlert"],
    .stInfo, .stWarning, .stError, .stSuccess {
        color: #000000 !important;
    }
    
    .stAlert p,
    [data-testid="stAlert"] p {
        color: #000000 !important;
    }
    
    /* Download button */
    .stDownloadButton > button {
        background-color: #ffffff !important;
        color: #000000 !important;
        border: 1px solid #cccccc !important;
    }
    
    .stDownloadButton > button:hover {
        background-color: #f0f0f0 !important;
    }
    
    /* Spinner */
    .stSpinner > div {
        border-top-color: #000000 !important;
    }
    
    /* Toast */
    [data-testid="stToast"],
    .stToast {
        background-color: #ffffff !important;
        color: #000000 !important;
    }
    
    /* Header */
    header,
    [data-testid="stHeader"] {
        background-color: #ffffff !important;
    }
    
    /* Metric */
    .stMetric,
    .stMetric label,
    .stMetric [data-testid="stMetricValue"] {
        color: #000000 !important;
    }
    
    /* Welcome container */
    .welcome-container {
        display: flex;
        justify-content: center;
        align-items: center;
        height: 60vh;
        background-color: #ffffff !important;
    }
    
    .welcome-title {
        font-size: 2.5rem;
        font-weight: 300;
        color: #000000 !important;
        text-align: center;
    }
    
    /* Popover/Modal backgrounds */
    [data-baseweb="popover"] > div,
    [data-baseweb="popover"] > div > div {
        background-color: #ffffff !important;
        color: #000000 !important;
    }
    
    /* Multi-select */
    .stMultiSelect > div > div,
    .stMultiSelect [data-baseweb="tag"] {
        background-color: #e8e8e8 !important;
        color: #000000 !important;
    }
    
    /* Table */
    .stTable, .stDataFrame,
    table, th, td {
        background-color: #ffffff !important;
        color: #000000 !important;
    }
    
    /* Progress bar text */
    .stProgress > div > div > div {
        color: #000000 !important;
    }
    
    /* Hide dark theme elements */
    [data-theme="dark"] {
        display: none !important;
    }
    
    /* Markdown */
    .stMarkdown, .stMarkdown * {
        color: #000000 !important;
    }
    
    /* Links */
    a, a:visited, a:hover {
        color: #0066cc !important;
    }
    
    /* Divider */
    hr {
        border-color: #e0e0e0 !important;
    }
    
    /* Number input */
    .stNumberInput > div > div > input {
        background-color: #ffffff !important;
        color: #000000 !important;
    }
    
    /* Date input */
    .stDateInput > div > div > input {
        background-color: #ffffff !important;
        color: #000000 !important;
    }
    
    /* Radio buttons */
    .stRadio label,
    .stRadio > div {
        color: #000000 !important;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"],
    .stTabs [data-baseweb="tab"] {
        background-color: #ffffff !important;
        color: #000000 !important;
    }
    
    /* Columns */
    [data-testid="column"] {
        background-color: transparent !important;
    }
    
    /* Ensure SVG icons are visible */
    svg {
        fill: currentColor !important;
    }
    
    /* Placeholder text */
    ::placeholder {
        color: #888888 !important;
        opacity: 1 !important;
    }
</style>
""", unsafe_allow_html=True)

# ----------------------
# Configuration
# ----------------------
API_KEY = os.getenv("CHATBOT_API_KEY", "sk_h4gsam68_z6e2xo8u9aaleUaBshwjVyDk")
PRESENTATION_API_KEY = "sk_u0xsaah7_pxzQfsbxtI4S7SsXlLLIsjaa"
PEXELS_API_KEY = "3Y3jiJZ6WAL49N6lPsdlRbRZ6IZBfHZFHP86dr9yZfxFYoxedLLlDKAC"
MODEL = "sarvam-m"
SYSTEM_PROMPT = (
    "You are Shiva AI, an advanced intelligent assistant. "
    "Provide helpful, accurate, and detailed responses. "
    "When files are provided, analyze them thoroughly and reference specific details. "
    "When image files are uploaded but OCR is not available, acknowledge the image was received "
    "and ask the user to describe what's in the image or provide any text from it if they need analysis. "
    "Be professional, clear, and comprehensive in your answers. "
    "Always provide complete responses - never cut off mid-sentence."
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
# AI Chat Function with Better Response Handling
# ----------------------
def get_ai_response(messages, max_retries=3):
    """
    Get AI response with retry logic and better error handling.
    Handles long responses and potential truncation.
    """
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": MODEL,
        "messages": messages,
        "max_tokens": 4096,  # Request more tokens for longer responses
        "temperature": 0.7
    }
    
    for attempt in range(max_retries):
        try:
            response = requests.post(
                CHAT_API_URL,
                headers=headers,
                json=payload,
                timeout=120  # Increased timeout for longer responses
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Extract the response text
                if "choices" in data and len(data["choices"]) > 0:
                    message = data["choices"][0].get("message", {})
                    content = message.get("content", "")
                    
                    # Check if response was truncated
                    finish_reason = data["choices"][0].get("finish_reason", "")
                    
                    if finish_reason == "length":
                        # Response was truncated, try to continue
                        content += "\n\n[Response was long. Continuing...]\n\n"
                        
                        # Make a follow-up request to continue
                        continuation_messages = messages.copy()
                        continuation_messages.append({"role": "assistant", "content": content})
                        continuation_messages.append({"role": "user", "content": "Please continue from where you left off."})
                        
                        continuation_payload = {
                            "model": MODEL,
                            "messages": continuation_messages,
                            "max_tokens": 4096,
                            "temperature": 0.7
                        }
                        
                        cont_response = requests.post(
                            CHAT_API_URL,
                            headers=headers,
                            json=continuation_payload,
                            timeout=120
                        )
                        
                        if cont_response.status_code == 200:
                            cont_data = cont_response.json()
                            if "choices" in cont_data and len(cont_data["choices"]) > 0:
                                continuation = cont_data["choices"][0].get("message", {}).get("content", "")
                                content += continuation
                    
                    return content if content else "No response received."
                else:
                    return "No response content found."
            
            elif response.status_code == 429:
                # Rate limited, wait and retry
                import time
                time.sleep(2 ** attempt)
                continue
            
            else:
                return f"⚠️ API Error {response.status_code}: {response.text[:500]}"
        
        except requests.exceptions.Timeout:
            if attempt < max_retries - 1:
                continue
            return "⚠️ Request timed out. Please try again with a shorter question."
        
        except requests.exceptions.RequestException as e:
            if attempt < max_retries - 1:
                continue
            return f"⚠️ Connection error: {str(e)}"
        
        except Exception as e:
            return f"❌ Error: {str(e)}"
    
    return "⚠️ Failed to get response after multiple attempts. Please try again."


# ----------------------
# Pexels Image Functions
# ----------------------
def search_pexels_image(query):
    """Search for an image on Pexels and return the image URL."""
    try:
        url = "https://api.pexels.com/v1/search"
        headers = {"Authorization": PEXELS_API_KEY}
        params = {
            "query": query,
            "per_page": 1,
            "orientation": "landscape",
            "size": "large"
        }
        
        response = requests.get(url, headers=headers, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get("photos") and len(data["photos"]) > 0:
                return data["photos"][0]["src"].get("large") or data["photos"][0]["src"].get("medium")
        return None
    except Exception:
        return None


def download_image(url):
    """Download image from URL and return as BytesIO."""
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers, timeout=15)
        
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
            else:
                img_data.seek(0)
                return img_data
        return None
    except Exception:
        return None


def generate_image_keywords(title):
    """Generate search keywords from slide title."""
    stop_words = {
        'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
        'of', 'with', 'by', 'from', 'is', 'are', 'was', 'were', 'be', 'been',
        'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would',
        'could', 'should', 'may', 'might', 'must', 'shall', 'can', 'need',
        'introduction', 'conclusion', 'overview', 'summary', 'key', 'points'
    }
    
    words = title.lower().split()
    keywords = [w for w in words if w not in stop_words and len(w) > 2]
    
    if keywords:
        return ' '.join(keywords[:3])
    return title


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
    payload = {
        "model": "sarvam-m", 
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 4096
    }
    response = requests.post(CHAT_API_URL, headers=headers, json=payload, timeout=120)
    response.raise_for_status()
    response_text = response.json()["choices"][0]["message"]["content"]
    
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


def create_powerpoint_presentation(slides, topic, target_lang_name, include_images=True, progress_callback=None):
    """Creates a PowerPoint presentation with images from Pexels."""
    
    # Import pptx modules
    from pptx import Presentation
    from pptx.util import Inches, Pt
    from pptx.dml.color import RGBColor
    from pptx.enum.text import PP_ALIGN
    
    prs = Presentation()
    
    # Set slide dimensions (16:9 widescreen)
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    
    # ----------------------
    # Title Slide
    # ----------------------
    if progress_callback:
        progress_callback("Creating title slide...")
    
    title_slide_layout = prs.slide_layouts[6]  # Blank layout
    slide = prs.slides.add_slide(title_slide_layout)
    
    # Add background image for title slide
    if include_images:
        if progress_callback:
            progress_callback("Finding title image...")
        img_url = search_pexels_image(topic)
        if img_url:
            img_data = download_image(img_url)
            if img_data:
                try:
                    slide.shapes.add_picture(
                        img_data, 
                        Inches(0), Inches(0),
                        width=prs.slide_width, 
                        height=prs.slide_height
                    )
                except Exception:
                    pass
    
    # Add dark overlay for text readability
    overlay = slide.shapes.add_shape(
        1,  # Rectangle
        Inches(0), Inches(0),
        prs.slide_width, prs.slide_height
    )
    overlay.fill.solid()
    overlay.fill.fore_color.rgb = RGBColor(0, 0, 0)
    overlay.line.fill.background()
    
    # Set overlay transparency
    try:
        from pptx.oxml.ns import qn
        from pptx.oxml import parse_xml
        spPr = overlay._sp.spPr
        fill = spPr.find(qn('a:solidFill'))
        if fill is not None:
            srgbClr = fill.find(qn('a:srgbClr'))
            if srgbClr is not None:
                alpha = parse_xml('<a:alpha xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" val="50000"/>')
                srgbClr.append(alpha)
    except Exception:
        pass
    
    # Add title text
    title_box = slide.shapes.add_textbox(Inches(0.5), Inches(2.5), Inches(12.333), Inches(1.5))
    title_frame = title_box.text_frame
    title_frame.word_wrap = True
    title_para = title_frame.paragraphs[0]
    title_para.text = topic
    title_para.font.size = Pt(54)
    title_para.font.bold = True
    title_para.font.color.rgb = RGBColor(255, 255, 255)
    title_para.alignment = PP_ALIGN.CENTER
    
    # Add subtitle
    subtitle_box = slide.shapes.add_textbox(Inches(0.5), Inches(4.2), Inches(12.333), Inches(0.8))
    subtitle_frame = subtitle_box.text_frame
    subtitle_para = subtitle_frame.paragraphs[0]
    subtitle_para.text = f"Generated by Shiva AI in {target_lang_name}"
    subtitle_para.font.size = Pt(24)
    subtitle_para.font.color.rgb = RGBColor(200, 200, 200)
    subtitle_para.alignment = PP_ALIGN.CENTER
    
    # ----------------------
    # Content Slides
    # ----------------------
    for idx, slide_data in enumerate(slides):
        if progress_callback:
            progress_callback(f"Creating slide {idx + 1} of {len(slides)}...")
        
        content_slide = prs.slides.add_slide(prs.slide_layouts[6])
        
        # Search for relevant image
        img_added = False
        if include_images:
            keywords = generate_image_keywords(slide_data['title'])
            if progress_callback:
                progress_callback(f"Finding image for: {keywords}...")
            
            img_url = search_pexels_image(keywords)
            if img_url:
                img_data = download_image(img_url)
                if img_data:
                    try:
                        content_slide.shapes.add_picture(
                            img_data,
                            Inches(7.0), Inches(0),
                            width=Inches(6.333),
                            height=prs.slide_height
                        )
                        img_added = True
                    except Exception:
                        pass
        
        # Add accent bar on left
        left_bar = content_slide.shapes.add_shape(
            1,
            Inches(0), Inches(0),
            Inches(0.15), prs.slide_height
        )
        left_bar.fill.solid()
        left_bar.fill.fore_color.rgb = RGBColor(0, 120, 215)
        left_bar.line.fill.background()
        
        # Add slide title
        title_width = Inches(6.0) if img_added else Inches(12)
        title_box = content_slide.shapes.add_textbox(Inches(0.4), Inches(0.5), title_width, Inches(1))
        title_frame = title_box.text_frame
        title_frame.word_wrap = True
        title_para = title_frame.paragraphs[0]
        title_para.text = slide_data['title']
        title_para.font.size = Pt(36)
        title_para.font.bold = True
        title_para.font.color.rgb = RGBColor(0, 0, 0)
        
        # Add underline
        underline = content_slide.shapes.add_shape(
            1,
            Inches(0.4), Inches(1.4),
            Inches(2), Inches(0.04)
        )
        underline.fill.solid()
        underline.fill.fore_color.rgb = RGBColor(0, 120, 215)
        underline.line.fill.background()
        
        # Add content
        content_width = Inches(6.0) if img_added else Inches(12)
        content_box = content_slide.shapes.add_textbox(Inches(0.4), Inches(1.7), content_width, Inches(5.3))
        content_frame = content_box.text_frame
        content_frame.word_wrap = True
        
        content_text = slide_data.get('content', '')
        content_lines = content_text.split('\n')
        
        for i, line in enumerate(content_lines):
            line = line.strip()
            if not line:
                continue
            
            line = line.lstrip('•-*●→▪ ')
            
            if i == 0:
                para = content_frame.paragraphs[0]
            else:
                para = content_frame.add_paragraph()
            
            para.text = f"● {line}"
            para.font.size = Pt(20)
            para.font.color.rgb = RGBColor(50, 50, 50)
            para.space_before = Pt(12)
            para.space_after = Pt(6)
    
    # ----------------------
    # Thank You Slide
    # ----------------------
    if progress_callback:
        progress_callback("Creating thank you slide...")
    
    thank_slide = prs.slides.add_slide(prs.slide_layouts[6])
    
    # Add background image
    if include_images:
        img_url = search_pexels_image("thank you success celebration")
        if img_url:
            img_data = download_image(img_url)
            if img_data:
                try:
                    thank_slide.shapes.add_picture(
                        img_data,
                        Inches(0), Inches(0),
                        width=prs.slide_width,
                        height=prs.slide_height
                    )
                except Exception:
                    pass
    
    # Add dark overlay
    overlay = thank_slide.shapes.add_shape(
        1, Inches(0), Inches(0),
        prs.slide_width, prs.slide_height
    )
    overlay.fill.solid()
    overlay.fill.fore_color.rgb = RGBColor(0, 0, 0)
    overlay.line.fill.background()
    
    try:
        from pptx.oxml.ns import qn
        from pptx.oxml import parse_xml
        spPr = overlay._sp.spPr
        fill = spPr.find(qn('a:solidFill'))
        if fill is not None:
            srgbClr = fill.find(qn('a:srgbClr'))
            if srgbClr is not None:
                alpha = parse_xml('<a:alpha xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" val="55000"/>')
                srgbClr.append(alpha)
    except Exception:
        pass
    
    # Add thank you text
    thank_box = thank_slide.shapes.add_textbox(Inches(0.5), Inches(2.5), Inches(12.333), Inches(1.5))
    thank_frame = thank_box.text_frame
    thank_para = thank_frame.paragraphs[0]
    thank_para.text = "Thank You!"
    thank_para.font.size = Pt(72)
    thank_para.font.bold = True
    thank_para.font.color.rgb = RGBColor(255, 255, 255)
    thank_para.alignment = PP_ALIGN.CENTER
    
    # Add questions text
    questions_box = thank_slide.shapes.add_textbox(Inches(0.5), Inches(4.5), Inches(12.333), Inches(0.8))
    questions_frame = questions_box.text_frame
    questions_para = questions_frame.paragraphs[0]
    questions_para.text = "Questions?"
    questions_para.font.size = Pt(28)
    questions_para.font.color.rgb = RGBColor(180, 180, 180)
    questions_para.alignment = PP_ALIGN.CENTER
    
    # Save presentation
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
        from pptx import Presentation
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
            return extract_text_from_pptx(file_bytes)
        
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
        # Limit TTS to first 1000 characters
        tts = gTTS(text[:1000], lang="en")
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
        st.markdown("✅ HD Images from Pexels")
        st.markdown("✅ Professional layouts")


# ----------------------
# Main Content Area
# ----------------------

if st.session_state.app_mode == "presentation":
    # ----------------------
    # Presentation Generator Mode
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
        
        include_images = st.checkbox("🖼️ Include HD images from Pexels", value=True)

        if st.button("Build My Presentation"):
            if not topic:
                st.warning("Please provide a topic for your presentation.")
            else:
                status_text = st.empty()
                
                def update_status(message):
                    status_text.info(message)
                
                with st.spinner("The AI is architecting your presentation... This may take a moment."):
                    try:
                        update_status("🤖 Generating content...")
                        english_slides = generate_english_presentation(topic, slide_count)
                        
                        target_lang_name = SUPPORTED_LANGUAGES[language]
                        update_status(f"🌐 Translating to {target_lang_name}...")
                        
                        translated_topic = translate_content(topic, language)
                        translated_slides = []
                        for s in english_slides:
                            translated_slide = {
                                'title': translate_content(s['title'], language),
                                'content': translate_content(s['content'], language)
                            }
                            translated_slides.append(translated_slide)
                        
                        update_status("📊 Building PowerPoint with images...")
                        ppt_file_stream = create_powerpoint_presentation(
                            translated_slides, 
                            translated_topic, 
                            target_lang_name,
                            include_images=include_images,
                            progress_callback=update_status
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
            label="📥 Download Presentation (.pptx)",
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
        
        # Build context from files
        files_context = ""
        if current_session["files"]:
            files_context = "\n\n=== UPLOADED FILES ===\n"
            for fdata in current_session["files"]:
                files_context += f"\n[FILE: {fdata['filename']} ({fdata.get('type', 'FILE')})]\n"
                # Limit file content to prevent context overflow
                file_content = fdata['content'][:8000]
                files_context += file_content
                if len(fdata['content']) > 8000:
                    files_context += "\n... (content truncated)\n"
            files_context += "\n=== END FILES ===\n\n"
        
        with st.chat_message("assistant"):
            placeholder = st.empty()
            placeholder.markdown("🤔 Thinking...")
            
            try:
                # Build messages for API
                messages_for_api = [{"role": "system", "content": SYSTEM_PROMPT}]
                
                # Get conversation history (limit to last 10 messages to prevent context overflow)
                conversation_messages = [
                    m for m in current_session["messages"][1:] 
                    if m["role"] in ["user", "assistant"]
                ][-10:]
                
                for m in conversation_messages[:-1]:  # Exclude the current message
                    messages_for_api.append({"role": m["role"], "content": m["content"][:2000]})
                
                # Add current message with file context
                user_content = files_context + user_message if files_context else user_message
                messages_for_api.append({"role": "user", "content": user_content})
                
                # Get AI response using the improved function
                response_text = get_ai_response(messages_for_api)
                
            except Exception as e:
                response_text = f"❌ Error: {str(e)}"
            
            placeholder.markdown(response_text)
            
            # Generate audio for first part of response
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
    "<div style='text-align: center; color: #000000 !important; padding: 20px;'>"
    "<p style='color: #000000 !important;'>Shiva AI by Shivansh Mahajan</p>"
    "</div>",
    unsafe_allow_html=True
)
