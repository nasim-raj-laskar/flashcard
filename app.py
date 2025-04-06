import streamlit as st
import requests
from gtts import gTTS
from io import BytesIO
from datetime import datetime
import warnings
warnings.filterwarnings("ignore", message=".*ScriptRunContext.*")

# ---- CONFIG ----
GROQ_API_KEY = "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"
GROQ_MODEL = "llama3-8b-8192"

# ---- SETUP ----
st.set_page_config(page_title="Groq Flashcard Generator", layout="centered")
st.title("📚 Flashcard Generator with Groq 🧠")
st.caption("Drop your notes fella")

# ---- SESSION STATE FOR HISTORY ----
if "history" not in st.session_state:
    st.session_state.history = []

# ---- UI ----
user_input = st.text_area("✍️ Paste your study notes below", height=300)
flashcard_count = st.slider("🧾 Number of Flashcards", 3, 10, 5)
lang = st.selectbox("🌐 Language", ["English", "Hindi", "Bengali", "Spanish"], index=0)
generate_btn = st.button("🚀 Generate Flashcards")

# ---- LANGUAGE MAP FOR TTS ----
lang_map = {
    "English": "en",
    "Hindi": "hi",
    "Bengali": "bn",
    "Spanish": "es"
}

# ---- API FUNCTION ----
def get_flashcards(text, count=5, language="English"):
    prompt = f"""
    Create {count} flashcards in {language} from the following study notes:\n\n{text}\n\n
    Format:\nQ1: ...\nA1: ...\nQ2: ...\nA2: ...
    """

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": GROQ_MODEL,
        "messages": [
            {"role": "user", "content": prompt}
        ]
    }

    res = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=payload)
    return res.json()['choices'][0]['message']['content']

# ---- EXPORT FUNCTION ----
def convert_to_txt(flashcards):
    return BytesIO(flashcards.encode("utf-8"))

# ---- TEXT-TO-SPEECH ----
def speak_flashcards(text, lang_code):
    try:
        tts = gTTS(text=text, lang=lang_code)
        mp3_fp = BytesIO()
        tts.write_to_fp(mp3_fp)
        mp3_fp.seek(0)
        return mp3_fp
    except Exception as e:
        st.error(f"🔇 Text-to-Speech Error: {e}")
        return None

# ---- OUTPUT ----
if generate_btn and user_input.strip() != "":
    with st.spinner("🌀 Thinking..."):
        try:
            flashcards = get_flashcards(user_input, flashcard_count, lang)

            st.subheader("📋 Your Flashcards")
            st.code(flashcards, language="markdown")

            # Save to history
            st.session_state.history.append((datetime.now().strftime("%H:%M:%S"), flashcards))

            # Download button
            txt_file = convert_to_txt(flashcards)
            st.download_button(
                label="⬇️ Download Flashcards as .txt",
                data=txt_file,
                file_name="flashcards.txt",
                mime="text/plain"
            )

            # Text-to-Speech
            if st.button("🔊 Read Aloud"):
                st.info("📢 Generating audio...")
                lang_code = lang_map[lang]
                audio_fp = speak_flashcards(flashcards, lang_code)
                if audio_fp:
                    st.audio(audio_fp, format="audio/mp3")

        except Exception as e:
            st.error(f"❌ Error: {e}")

# ---- HISTORY ----
with st.expander("📜 View Flashcard History"):
    for time_str, item in reversed(st.session_state.history):
        st.markdown(f"**🕘 {time_str}**")
        st.code(item, language="markdown")
