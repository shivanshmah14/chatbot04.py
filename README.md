# Shiva AI — README

> **Shiva AI** is a Streamlit-based chat assistant app with file upload, basic user authentication, file content extraction, optional TTS and image preview support. This README explains the project, how to set it up, run it locally, and walks through the code step-by-step.

---

## Table of contents

1. Project overview
2. Features
3. Requirements
4. Installation & quick start
5. Environment variables
6. Step-by-step code walkthrough
7. File handling and supported types
8. Authentication & session behaviour
9. TTS, PDF and image support
10. Persisting and exporting data
11. Troubleshooting & common errors
12. Security & deployment notes
13. Customization tips
14. License

---

## 1. Project overview

Shiva AI is a chat application built with Streamlit that:

* Lets multiple local users register and log in (in-memory session storage).
* Maintains multiple chat sessions per user.
* Accepts file uploads (text, code, CSV, JSON, PDF, images) and extracts or previews content.
* Sends chat context (including file snippets) to an external API (`https://api.sarvam.ai/v1/chat/completions`).
* Optionally generates TTS audio using `gTTS`.
* Uses custom CSS to enforce a dark, professional theme across the UI.

---

## 2. Features

* Local user registration/login with password hashing (SHA-256).
* Chat history per user and multiple chat sessions.
* File uploader with specialized handling for images and text documents.
* Extract text content from PDFs (if `PyPDF2` available).
* Image preview (if `Pillow` available).
* Optional text-to-speech via `gTTS`.
* UI: sidebar with chat list, search, create/delete chats, logout.
* Automatic generation and update of chat titles from user messages.

---

## 3. Requirements

Minimum Python packages referenced in the code (install as needed):

```bash
pip install streamlit requests
# Optional features
pip install gTTS PyPDF2 pillow
```

> Note: The app gracefully degrades when optional libraries are missing (PDF_SUPPORT, TTS_AVAILABLE, IMAGE_SUPPORT flags).

---

## 4. Installation & quick start

1. Clone or copy the project files into a directory.
2. Create a Python virtual environment and install dependencies.

```bash
python -m venv venv
source venv/bin/activate  # macOS / Linux
# or on Windows: venv\Scripts\activate
pip install streamlit requests
# optional
pip install gTTS PyPDF2 pillow
```

3. Set the environment variable for the API key (recommended):

```bash
export CHATBOT_API_KEY="your_real_api_key_here"
# on Windows PowerShell:
# setx CHATBOT_API_KEY "your_real_api_key_here"
```

4. Run the app:

```bash
streamlit run app.py
```

(Replace `app.py` with the filename you saved the provided code as.)

---

## 5. Environment variables

* `CHATBOT_API_KEY` (optional): API key used in `API_KEY = os.getenv("CHATBOT_API_KEY", "sk_h4gsam68_...")`. **Important**: Do NOT commit real API keys in source code. Set them in your environment.

* `MODEL`: The code sets `MODEL = "sarvam-m"`. Change this to your desired model identifier if needed.

---

## 6. Step-by-step code walkthrough

Below is a stepwise explanation of the main components and flow of the app.

### A. Imports & optional feature detection

* The top imports bring in Streamlit, file handling, HTTP requests, temporary files, JSON handling, UUIDs, hashing, base64, and date/time utilities.
* Optional imports wrap `gtts` (TTS), `PyPDF2` (PDF support), and `PIL.Image` (image processing) in try/except blocks and set flags (`TTS_AVAILABLE`, `PDF_SUPPORT`, `IMAGE_SUPPORT`) depending on availability. This allows the app to run if optional libs are missing.

### B. Streamlit page setup & CSS

* `st.set_page_config(...)` configures the browser tab and layout.
* A large `st.markdown(..., unsafe_allow_html=True)` block injects a custom CSS theme that forces a black/dark UI and changes many Streamlit components (buttons, file uploader, tooltips, etc.).

### C. Configuration constants

* `API_KEY` — loaded from the environment with a fallback token in the code (replace this placeholder in production!).
* `MODEL` — name of the model to send to the external chat API.
* `SYSTEM_PROMPT` — system-level message inserted at the start of each chat session to define assistant behavior.

### D. Authentication helpers

Functions:

* `hash_password(password)` — returns SHA-256 hex digest of the password.
* `save_to_browser_storage` / `load_from_browser_storage` — attempt to store/load session credentials via browser `localStorage` using a small JS snippet embedded via `st.components.v1.html`. (Note: this is a best-effort approach — Streamlit cannot directly return the `postMessage` result reliably in all environments.)
* `init_user_data()` — initializes `st.session_state` keys: `users`, `logged_in`, `current_user`, `session_initialized`, etc.
* `register_user(username, password)` — stores a new user in `st.session_state.users` with password hash and metadata.
* `login_user(username, password, remember=True)` — validates credentials and prepares `st.session_state.chat_sessions`. If the user has no chat sessions a default one is created.
* `auto_login()` — attempts to sign the user in using saved username/password hash in session state.
* `logout_user()` — saves session chat sessions to `st.session_state.users` and clears logged-in flags and saved credentials.

> Note: All user data is kept in Streamlit session state (in-memory). If you restart the server you will lose all user accounts and chats unless you add persistent storage.

### E. Session state initialization & auto-login

* `init_user_data()` is called, then the app tries `auto_login()` once. Several `st.session_state` defaults are set for chat sessions, voice settings, search query and last processed files.

### F. File handlers and helpers

* `process_image(file_bytes, filename)` — if `Pillow` is present, this writes the raw bytes to a temporary file and returns metadata including `base64` encoding and `path` for preview.

* `extract_file_content(file_bytes, filename)` (cached via `@st.cache_data`) — examines file extension and returns a string representation for each supported type: images return a short tag (`[IMAGE: filename]`), `.txt`, `.py`, `.md`, `.csv`, `.json` return decoded text, `.pdf` is parsed with `PyPDF2` page-by-page (if installed). A few fallback heuristics decode bytes with `errors='ignore'`.

* `speak_text(text)` — uses `gTTS` to render the first 500 characters of the assistant response to a temporary `.mp3` file (if `gtts` is installed).

* `generate_chat_title(first_message)` — shortens the first message for use as a chat title.

* Chat session helpers: `create_new_chat`, `switch_chat`, `get_current_session`, `update_chat_title`, `delete_chat`.

### G. UI: Login / Registration

* If the user is not logged in the app displays a centered login/register panel implemented with `st.tabs`.
* Register: collects username/password, validates minimal password length and matching confirmation, then calls `register_user`.
* Login: validates credentials with `login_user` and re-runs the app.

### H. UI: Main App (after login)

**Sidebar**

* Shows current user, logout button, "New Chat" button, search box for chat titles, list of chats (sorted by creation), delete buttons for chats, and a small caption with message count in the current chat.

**Main area**

* Renders chat messages from `current_session["messages"]` with `st.chat_message` blocks.
* If uploaded files exist, an expander shows attached files, with image preview (if available) and option to remove each file.

**File uploader**

* A small circular file uploader is implemented in the input column and accepts many types. On upload, files are processed by `process_image` or `extract_file_content` and appended to the active chat session `files` list. `st.toast()` shows attachment success.

**Chat input**

* `user_message = st.chat_input("Ask anything...")` is used to collect text input.

**On user message submit**

1. The app updates the chat title if necessary and appends the user's message to the current session's `messages`.
2. It constructs `files_context` by concatenating short tags or the first ~3000 characters of each uploaded file's `content`.
3. Builds `messages_for_api` — a list beginning with the `SYSTEM_PROMPT` followed by previous messages; the current user's message gets replaced with `user_content` (the `files_context` + message if files present).
4. Sends a POST request to the external API (`https://api.sarvam.ai/v1/chat/completions`) with `model` and `messages` in the JSON payload. The `API_KEY` is placed in an `Authorization: Bearer` header.
5. Handles HTTP errors and various exceptions and renders the assistant's response into the chat UI.
6. Optionally generates a TTS `.mp3` and calls `st.audio()` to show a player.
7. Appends the assistant response to session messages and saves user chat sessions back into `st.session_state.users`.
8. Calls `st.rerun()` to refresh UI state.

---

## 7. File handling and supported types

Supported file extensions in the uploader are defined in the UI section and include:

```
['txt','json','csv','py','md','html','css','js','htm','pdf','jpg','jpeg','png','gif','bmp','webp']
```

* Images: processed via `process_image` and stored as temporary files for preview; content is summarized as `[IMAGE: filename]` in the chat context.
* PDFs: parsed via `PyPDF2` if installed. If not installed, `extract_file_content` will return a warning string telling the user that PDF support requires `PyPDF2`.
* Large file content is truncated when included in the API context (the code truncates to 3000 characters per file when building `files_context`).

---

## 8. Authentication & session behaviour

* The app stores users in `st.session_state.users`, a dictionary mapping usernames to objects `{ password, chat_sessions, created }`.
* Passwords are hashed with SHA-256 before being stored.
* There is an in-memory "remember" mechanism (`st.session_state.saved_username` and `saved_password_hash`) to auto-login while the server process is alive.
* **Important**: This is not production-grade authentication. For a real app you should store users in a secure database and use salted hashing (bcrypt/argon2) and secure cookies or a token-based session store.

---

## 9. TTS, PDF and image support

* `gTTS` (optional): when installed the app will try to create a small MP3 of assistant responses (first 500 chars). If `gTTS` isn't installed `TTS_AVAILABLE` is `False` and the app will skip audio generation.
* `PyPDF2` (optional): required to extract text from PDF pages.
* `Pillow` (optional): required to process images (open, save to temporary path for preview) and provide `base64` encoding for potential future use.

---

## 10. Persisting and exporting data

Currently: all user accounts and chat session data are kept in-memory in `st.session_state`. To persist data across server restarts you must:

* Save `st.session_state.users` to a file or database at regular points (e.g., on logout or on each message), or
* Replace the in-memory store with a database (SQLite, PostgreSQL, etc.) and update `register_user`, `login_user`, `logout_user`, and other places that read/write `st.session_state.users`.

---

## 11. Troubleshooting & common errors

* **`PyPDF2` not installed**: PDF extraction returns `⚠️ PDF support requires PyPDF2`. Install `pip install PyPDF2`.
* **`gTTS` errors**: TTS may fail if `gTTS` can't reach Google's TTS endpoint — install `gTTS` and ensure network access.
* **API request fails**: check `CHATBOT_API_KEY`, network connectivity, and the external API’s health. The code displays the HTTP status and a slice of the response text when non-200.
* **Session reset on reload**: Streamlit session state is in-memory; server or script restarts will clear sessions and users. Implement persistent storage to fix.
* **File uploader visually broken**: The CSS aggressively hides parts of the uploader for a stylized circular button. If you encounter unexpected behaviour remove or relax the CSS rules.

---

## 12. Security & deployment notes

* **Never commit real API keys**; use environment variables or secrets managers (Streamlit Cloud/Heroku/AWS Secrets Manager).
* Use secure password hashing (bcrypt, argon2) and SSL in production.
* The included default API key string looks like a placeholder — rotate and use your own.
* Validate and sanitize file uploads if you persist them. Avoid executing or importing uploaded code.

---

## 13. Customization tips

* **Persistent storage**: Replace the `st.session_state.users` store with a database. Wrap reads/writes into helper functions.
* **Improve auth**: Use `passlib` or `bcrypt` for hashing, and JWT or server-side sessions to manage auth.
* **API resilience**: Add retry logic (exponential backoff) around the external API call.
* **File size limits**: Add size checks to uploaded files and give clear UI errors.
* **UI tweaks**: If the aggressive CSS causes issues on some components, scope it narrower or make it optional via a toggle.

---

## 14. License

Include a license appropriate for your project. Example (MIT):

```
MIT License

Copyright (c) 2025 Your Name

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction... (add full MIT text)
```

---

## Appendix: Quick checklist before production deploy

* [ ] Remove hard-coded API key from source code.
* [ ] Use a persistent database for users and chats.
* [ ] Replace SHA-256 with a salted hash (bcrypt/argon2).
* [ ] Add input validation and file size limits.
* [ ] Serve Streamlit behind HTTPS in production.
* [ ] Audit third-party CSS for accessibility and layout issues.

---

If you want, I can:

* Produce a `requirements.txt` for this app.
* Suggest a minimal database schema + small migration script to persist users and chats.
* Convert the in-memory auth to a basic token-based login using JWT and SQLite.

*End of README*
