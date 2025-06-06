import streamlit as st
import pandas as pd
import random
from gtts import gTTS
import base64
import time

st.set_page_config(page_title="Croatian Flashcards", layout="centered")

# --- Load and cache translations
@st.cache_data
def load_cards():
    df = pd.read_csv("translations.csv")
    return df.to_dict(orient="records")

def speak(text, lang="en", filename="temp.mp3"):
    tts = gTTS(text=text, lang=lang)
    tts.save(filename)
    with open(filename, "rb") as f:
        b64 = base64.b64encode(f.read()).decode()
    return f"""
        <audio autoplay="true">
        <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
        </audio>
    """

# --- Session state init
if "cards" not in st.session_s_
