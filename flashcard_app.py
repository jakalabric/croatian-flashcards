
import streamlit as st
import pandas as pd
import random
from gtts import gTTS
import os

st.set_page_config(page_title="Croatian Flashcards", layout="centered")

# Load and cache card data
@st.cache_data
def load_cards():
    df = pd.read_csv("translations.csv")
    return df.to_dict(orient="records")

# Init session state
if "cards" not in st.session_state:
    st.session_state.cards = random.sample(load_cards(), len(load_cards()))
    st.session_state.index = 0
    st.session_state.flipped = False
    st.session_state.completed = set()
    st.session_state.mode = "light"
    st.session_state.history = []

# Get current card
cards = st.session_state.cards
current_index = st.session_state.index
current_card = cards[current_index]
english = current_card["English"]
croatian = current_card["Croatian"]

# Speak helper
def speak(text, lang="en"):
    tts = gTTS(text=text, lang=lang)
    filename = "temp.mp3"
    tts.save(filename)
    return filename

# Header & theme toggle
st.title("🇭🇷 Croatian Flashcards")
theme = st.radio("Choose mode:", ("light", "dark"))
st.session_state.mode = theme

if theme == "dark":
    card_front_style = "background-color:black;color:white;"
    card_back_style = "background-color:white;color:black;"
else:
    card_front_style = "background-color:#f0f0f0;color:black;"
    card_back_style = "background-color:#fff;color:black;"

# Progress
st.markdown(f"### Card {current_index + 1} of {len(cards)}")

# Card display
card_style = "padding:50px; text-align:center; border-radius:12px; font-size:2em; cursor:pointer;"

if not st.session_state.flipped:
    st.markdown(f'<div style="{card_style + card_front_style}">{english}</div>', unsafe_allow_html=True)
    st.audio(speak(f"How do you say {english}?", lang="en"), format="audio/mp3")
else:
    st.markdown(f'<div style="{card_style + card_back_style}">{croatian}</div>', unsafe_allow_html=True)
    st.audio(speak(croatian, lang="hr"), format="audio/mp3")

# Buttons
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("🔁 Repeat"):
        st.audio(speak(f"How do you say {english}?", lang="en"), format="audio/mp3")
        if st.session_state.flipped:
            st.audio(speak(croatian, lang="hr"), format="audio/mp3")

with col2:
    if st.button("🪞 Flip"):
        st.session_state.flipped = not st.session_state.flipped

with col3:
    if st.button("➡️ Next"):
        st.session_state.history.append(current_index)
        st.session_state.index = (current_index + 1) % len(cards)
        st.session_state.flipped = False

# Spaced repetition (Got it / Didn't know)
st.markdown("### How well did you know it?")
col4, col5 = st.columns(2)
with col4:
    if st.button("✅ Got it"):
        st.session_state.completed.add(current_index)
with col5:
    if st.button("❌ Didn't know"):
        cards.append(cards[current_index])  # re-add card to end

# Add custom card
st.markdown("---")
st.markdown("### ➕ Add Your Own Card")
with st.form("add_card_form"):
    eng = st.text_input("English")
    cro = st.text_input("Croatian")
    submitted = st.form_submit_button("Add Card")
    if submitted and eng and cro:
        new_card = {"English": eng, "Croatian": cro}
        cards.append(new_card)
        st.success("Card added!")

# Search/filter
st.markdown("---")
st.markdown("### 🔍 Search Cards")
search = st.text_input("Search")
if search:
    results = [c for c in cards if search.lower() in c["English"].lower() or search.lower() in c["Croatian"].lower()]
    st.write(f"Found {len(results)} results:")
    for r in results:
        st.write(f"- {r['English']} → {r['Croatian']}")
