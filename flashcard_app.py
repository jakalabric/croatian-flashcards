import streamlit as st
import pandas as pd
import random
from gtts import gTTS
import base64
import os
import time

st.set_page_config(page_title="Croatian Flashcards", layout="centered")

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

# --- Init session state
if "cards" not in st.session_state:
    st.session_state.cards = random.sample(load_cards(), len(load_cards()))
    st.session_state.index = 0
    st.session_state.flipped = False
    st.session_state.last_flip_time = None

cards = st.session_state.cards
index = st.session_state.index
card = cards[index]
english = card["English"]
croatian = card["Croatian"]

# Theme & style
card_style = "padding:60px;text-align:center;border-radius:12px;font-size:2em;cursor:pointer;"
background = "#111" if st.get_option("theme.base") == "dark" else "#fafafa"
text_color = "#fff" if st.get_option("theme.base") == "dark" else "#000"
style = f"background-color:{background};color:{text_color};" + card_style

# --- Logic: Auto play English TTS when showing front
if not st.session_state.flipped:
    st.markdown(speak(f"How do you say {english}?", lang="en"), unsafe_allow_html=True)

# --- Handle auto-advance after flip
if st.session_state.flipped:
    if st.session_state.last_flip_time is None:
        st.session_state.last_flip_time = time.time()
        st.markdown(speak(croatian, lang="hr"), unsafe_allow_html=True)
    elif time.time() - st.session_state.last_flip_time > 4:
        st.session_state.index = (index + 1) %_
