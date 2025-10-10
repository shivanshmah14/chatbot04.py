import streamlit as st
import uuid
import os
import requests
import tempfile
import speech_recognition as sr
import sounddevice as sd
import wavio
from gtts import gTTS

# --- Streamlit UI setup ---
st.set_page_config(page_title="Shiva AI", layout="wide")
st.title("Shiva AI")

# --- Configuration ---
API_KEY = os.getenv("CHATBOT_API_KEY", "sk_h4gsam68_z6e2xo8u9aaleUaBshwjVyDk")
MODEL = "sarvam-m"
SYSTEM_PROMPT = (
    "You are Shiva AI, a helpful assistant with a calm Indian tone. "
    "You can explain and solve maths and physics problems using clear, neat formatting. "
    "Use simple language, and write x² instead of x^2."
)

# --- Speak function (Indian female via gTTS) ---
def speak_text(text):
    try:
        tts = gTTS(text=text, lang="en", tld="co.in")
        audio_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
        tts.save(audio_file.name)
        st.audio(audio_file.name, format="audio/mp3")
    except Exception as e:
        st.error(f"TTS error: {e}")

# --- Session state ---
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": SYSTEM_PROMPT}]
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

# --- Layout ---
chat_col, meta_col = st.columns((3, 1))

with chat_col:
    st.markdown("### 💬 Chat")

    # Display conversation history
    for msg in st.session_state.messages:
        if msg["role"] == "system":
            continue
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    # --- Input area ---
    col_input, col_rec = st.columns([10, 1])
    with col_input:
        user_message = st.chat_input("Type or record to Shiva...")

    with col_rec:
        if st.button("🎤"):
            fs = 16000
            recording = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype='int16')
            sd.wait()
            
            wav_path = os.path.join(tempfile.gettempdir(), f"voice_{uuid.uuid4()}.wav")
            wavio.write(wav_path, recording, fs, sampwidth=2)

            recognizer = sr.Recognizer()
            try:
                with sr.AudioFile(wav_path) as source:
                    audio = recognizer.record(source)
                    user_message = recognizer.recognize_google(audio, language="en-IN")
                    st.success(f"🎙️ You said: {user_message}")
            except Exception as e:
                st.error(f"Speech recognition error: {e}")

    # --- Process message ---
    if user_message:
        st.session_state.messages.append({"role": "user", "content": user_message})
        with st.chat_message("assistant"):
            placeholder = st.empty()
            placeholder.write("🤔 Thinking...")

        try:
            messages_for_api = [{"role": "system", "content": SYSTEM_PROMPT}]
            for m in st.session_state.messages:
                if m["role"] != "system":
                    messages_for_api.append({"role": m["role"], "content": m["content"]})

            payload = {"model": MODEL, "messages": messages_for_api}
            headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
            url = "https://api.sarvam.ai/v1/chat/completions"

            resp = requests.post(url, headers=headers, json=payload, timeout=60)
            if resp.status_code != 200:
                response_text = f"[Error {resp.status_code}] {resp.text}"
            else:
                data = resp.json()
                response_text = data.get("choices", [{}])[0].get("message", {}).get("content", "No reply.")
        except Exception as e:
            response_text = f"[Error] {e}"

        # Display response
        placeholder.write(response_text)
        st.session_state.messages.append({"role": "assistant", "content": response_text})

        # Speak out the response
        speak_text(response_text)

with meta_col:
    st.markdown("### Conversation Info")
    st.write(f"Messages: {len(st.session_state.messages) - 1}")
    if st.button("🧹 Clear conversation"):
        st.session_state.messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        st.experimental_rerun()

st.caption("Shiva AI — Your personal AI assistance")

