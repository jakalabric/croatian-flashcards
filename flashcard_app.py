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
        b64 = base64.b64encode(f.read()).decode()
    return f"""
        <audio autoplay="true">
        <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
        </audio>
    """

# Initialize session state
if "cards" not in st.session_state:
    st.session_state.cards = random.sample(load_cards(), len(load_cards()))
    st.session_state.index = 0
    st.session_state.flipped = False
    st.session_state.audio = ""
    st.session_state.just_flipped = False
    st.session_state.theme = "Light"
    st.session_state.completed = set()

cards = st.session_state.cards
index = st.session_state.index
card = cards[index]
english = card["English"]
croatian = card["Croatian"]

# Theme styles
theme = st.session_state.theme
light_style = "background-color:#f8f8f8;color:#000;"
dark_style = "background-color:#333;color:#fff;"
card_style = "padding:40px;text-align:center;border-radius:12px;font-size:2em;cursor:pointer;"
style = dark_style if theme == "Dark" else light_style

# Tabs: Learn vs Extras
tab1, tab2 = st.tabs(["🧠 Learn", "⚙️ Extras"])

with tab2:
    st.markdown("### 🌓 Theme")
    st.session_state.theme = st.radio("Choose Theme", ["Light", "Dark"], horizontal=True)

    st.markdown("### ✅ Mark Your Progress")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("✅ Got it"):
            st.session_state.completed.add(index)
    with col2:
        if st.button("❌ Didn't know"):
            cards.append(cards[index])  # Repeat later

    st.markdown("---")
    st.markdown("### ➕ Add Custom Card")
    with st.form("add_card_form"):
        eng = st.text_input("English")
        cro = st.text_input("Croatian")
        if st.form_submit_button("Add"):
            cards.append({"English": eng, "Croatian": cro})
            st.success("Added!")

    st.markdown("### 🔍 Search Cards")
    query = st.text_input("Search")
    if query:
        results = [c for c in cards if query.lower() in c["English"].lower() or query.lower() in c["Croatian"].lower()]
        for c in results:
            st.write(f"- {c['English']} → {c['Croatian']}")

with tab1:
    st.markdown(f"### Card {index + 1} of {len(cards)}")

    # Handle TTS playback
    if "last_index" not in st.session_state or st.session_state.last_index != index:
        st.session_state.audio = speak(f"How do you say {english}?", lang="en")
        st.session_state.flipped = False
        st.session_state.just_flipped = False
        st.session_state.last_index = index

    # Speak Croatian on first flip only
    if st.session_state.flipped and not st.session_state.just_flipped:
        st.session_state.audio = speak(croatian, lang="hr")
        st.session_state.just_flipped = True

    # Card UI
    if st.session_state.flipped:
        st.markdown(f'<div style="{card_style + style}">{croatian}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div style="{card_style + style}">{english}</div>', unsafe_allow_html=True)

    # Play queued audio
    if st.session_state.audio:
        st.markdown(st.session_state.audio, unsafe_allow_html=True)
        st.session_state.audio = ""

    # Controls
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("🪞 Flip"):
            st.session_state.flipped = not st.session_state.flipped
    with col2:
        if st.button("🔁 Repeat"):
            if st.session_state.flipped:
                st.session_state.audio = speak(croatian, lang="hr")
            else:
                st.session_state.audio = speak(f"How do you say {english}?", lang="en")
    with col3:
        if st.button("➡️ Next"):
            st.session_state.index = (index + 1) % len(cards)
            st.session_state.flipped = False
            st.session_state.just_flipped = False
