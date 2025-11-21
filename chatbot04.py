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
    
    /* Search input - BLACK with WHITE text */
    /* Search input - White with Black text */
    .stTextInput > div > div > input {
        background-color: #000000 !important;
        color: #ffffff !important;
        background-color: #ffffff !important;
        color: #000000 !important;
        border: 1px solid #ffffff !important;
        border-radius: 8px !important;
        padding: 0.5rem 0.75rem !important;
@@ -638,3 +638,4 @@ def delete_chat(session_id):
            st.audio(audio_file, format="audio/mp3")

        st.rerun()
