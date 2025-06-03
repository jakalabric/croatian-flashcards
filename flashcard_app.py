import streamlit as st
import pandas as pd
import random
from gtts import gTTS
import base64
import os

st.set_page_config(page_title="Croatian Flashcards", layout="centered")

# Load CSV cards
@st.cache_data
def load_cards():
    df = pd.read_csv("translations.csv")
    return df.to_dict(orient="records")

# Generate audio and return HTML to autoplay
def speak(text, lang="en", filename="temp.mp3"):
    tts = gTTS(text=text, lang=lang)
    tts.save(filename)
    with open(filename, "rb") as f:
