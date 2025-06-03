import streamlit as st
import pandas as pd
import random
from gtts import gTTS
import os
import base64

st.set_page_config(page_title="Croatian Flashcards", layout="centered")

# Load and cache card data
@st.cache_data
def load_cards():
    df = pd.read_csv("translations.csv")
    return df.to_dict(orient="records")

# Helper to auto-play audio via HTML
def autoplay_audio(file_path):
    with open(file_path, "rb") as f:
        data = f.read()
        b64 = base64.b64encode(data).decode()
        return f"""
            <audio autoplay="true">
            <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
            </audio>
        """

# Speak helper
def speak(text, lang="en", save_as="temp.mp3"):
    tts = gTTS(text=text, lang=lang)
    tts.save(save_as)
    return save_as

# Initialize session
if "cards" not in st.session_state:
    st.session_state.cards = random.sample(load_cards(), len(load_cards()))
    st.session_state.index = 0
    st.session_state.flipped = False
    st.session_state.completed = set()
    st.session_state.history = []
    st.session_state.audio_to_play = ""

cards = st.session_state.cards
current_index = st.session_state.index
current_card = cards[current_index]
english = current_card["English"]
croatian = current_card["Croatian"]

# Tabs for core vs advanced
tab1, tab2 = st.tabs(["🧠 Learn", "⚙️ Advanced Options"])

with tab1:
    # Theme
    theme = st.selectbox("Theme", ("Light", "Dark"), index=0)
    card_front_style = "background-color:#333;color:white;" if theme == "Dark" else "background-color:#f0f0f0;color:black;"
    card_back_style = "background-color:white;color:black;"

    st.markdown(f"### Card {current_index + 1} of {len(cards)}")

    # Audio logic on state change
    if "last_card_index" not in st.session_state or st.session_state.last_card_index != current_index:
        st.session_state.audio_to_play = speak(f"How do you say {english}?", lang="en")
        st.session_state.last_card_index = current_index
    elif st.session_state.flipped and "last_flipped" not in st.session_state:
        st.session_state.audio_to_play = speak(croatian, lang="hr")
        st.session_state.last_flipped = True

    if not st.session_state.flipped and "last_flipped" in st.session_state:
        del st.session_state.last_flipped

    # Display clickable card
    card_style = "padding:40px; text-align:center; border-radius:12px; font-size:2em; cursor:pointer;"
    if st.session_state.flipped:
        if st.button("🔊 Click to Repeat Croatian", key="repeat_hr"):
            st.session_state.audio_to_play = speak(croatian, lang="hr")
        st.markdown(f'<div style="{card_style + card_back_style}">{croatian}</div>', unsafe_allow_html=True)
    else:
        if st.button("🔊 Click to Repeat English", key="repeat_en"):
            st.session_state.audio_to_play = speak(f"How do you say {english}?", lang="en")
        st.markdown(f'<div style="{card_style + card_front_style}">{english}</div>', unsafe_allow_html=True)

    # Auto-play stored audio
    if st.session_state.audio_to_play:
        st.markdown(autoplay_audio(st.session_state.audio_to_play), unsafe_allow_html=True)
        st.session_state.audio_to_play = ""

    # Controls
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("🔁 Repeat Both"):
            st.session_state.audio_to_play = speak(f"How do you say {english}?", lang="en")
            if st.session_state.flipped:
                st.session_state.audio_to_play = speak(croatian, lang="hr")
    with col2:
        if st.button("🪞 Flip Card"):
            st.session_state.flipped = not st.session_state.flipped
    with col3:
        if st.button("➡️ Next Card"):
            st.session_state.history.append(current_index)
            st.session_state.index = (current_index + 1) % len(cards)
            st.session_state.flipped = False

with tab2:
    st.markdown("### ✅ Memory Score")
    col4, col5 = st.columns(2)
    with col4:
        if st.button("✅ Got it"):
            st.session_state.completed.add(current_index)
    with col5:
        if st.button("❌ Didn't know"):
            cards.append(cards[current_index])

    st.markdown("---")
    st.markdown("### ➕ Add Your Own Card")
    with st.form("add_card_form"):
        eng = st.text_input("English")
        cro = st.text_input("Croatian")
        submitted = st.form_submit_button("Add Card")
        if submitted and eng and cro:
            cards.append({"English": eng, "Croatian": cro})
            st.success("Card added!")

    st.markdown("### 🔍 Search Cards")
    search = st.text_input("Search")
    if search:
        results = [c for c in cards if search.lower() in c["English"].lower() or search.lower() in c["Croatian"].lower()]
        st.write(f"Found {len(results)} result(s):")
        for r in results:
            st.write(f"- {r['English']} → {r['Croatian']}")
