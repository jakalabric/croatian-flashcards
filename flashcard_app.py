
import streamlit as st
import pandas as pd
from gtts import gTTS
import random
import os

@st.cache_data
def load_data():
    df = pd.read_csv("translations.csv")
    return df.to_dict(orient="records")

flashcards = load_data()

if "current_card" not in st.session_state:
    st.session_state.current_card = random.choice(flashcards)
if "show_answer" not in st.session_state:
    st.session_state.show_answer = False

def speak(text, lang="hr"):
    tts = gTTS(text=text, lang=lang)
    tts.save("croatian.mp3")
    audio_file = open("croatian.mp3", "rb")
    st.audio(audio_file.read(), format="audio/mp3")

st.title("🇭🇷 Croatian Flashcards")

st.markdown("### Phrase in Croatian:")
st.markdown(f"**{st.session_state.current_card['Croatian']}**")

if st.button("🔁 Repeat"):
    speak(st.session_state.current_card['Croatian'])

if st.button("🪞 Show Answer"):
    st.session_state.show_answer = True

if st.session_state.show_answer:
    st.markdown("### Translation:")
    st.success(st.session_state.current_card['English'])

if st.button("➡️ Next"):
    st.session_state.current_card = random.choice(flashcards)
    st.session_state.show_answer = False
