import streamlit as st
import pandas as pd
import random
from gtts import gTTS
import io

# --- Helper Functions ---
def speak(text, lang='en'):
    tts = gTTS(text=text, lang=lang)
    fp = io.BytesIO()
    tts.write_to_fp(fp)
    fp.seek(0)
    return fp

# --- App State ---
if 'card_order' not in st.session_state:
    st.session_state.card_order = []
if 'current' not in st.session_state:
    st.session_state.current = 0
if 'show_back' not in st.session_state:
    st.session_state.show_back = False
if 'cards' not in st.session_state:
    st.session_state.cards = []

# --- UI ---
st.title("Translation Memory Card Game 🇬🇧 ➡️ 🇭🇷")

# File upload
uploaded_file = st.file_uploader("Upload your English–Croatian CSV file", type=["csv"])
if uploaded_file:
    df = pd.read_csv(uploaded_file)
    # Expect columns: "English", "Croatian"
    cards = list(df[['English', 'Croatian']].itertuples(index=False, name=None))
    if st.session_state.cards != cards:
        st.session_state.cards = cards
        st.session_state.card_order = random.sample(range(len(cards)), len(cards))
        st.session_state.current = 0
        st.session_state.show_back = False

if st.session_state.cards:
    idx = st.session_state.card_order[st.session_state.current]
    eng, cro = st.session_state.cards[idx]

    st.write(f"Card {st.session_state.current+1} of {len(st.session_state.cards)}")

    # Card display
    card_style = """
    <div style='display:flex;justify-content:center;align-items:center;height:300px;'>
        <div style='width:400px;height:200px;border-radius:16px;box-shadow:0 2px 16px #0002;
                    display:flex;justify-content:center;align-items:center;cursor:pointer;
                    font-size:2em;{bg}{color}'>
            {text}
        </div>
    </div>
    """
    if not st.session_state.show_back:
        # Front: English, black bg, white text
        st.markdown(card_style.format(
            bg="background:black;",
            color="color:white;",
            text=eng
        ), unsafe_allow_html=True)
        if st.button("Flip Card"):
            st.session_state.show_back = True
        # Auto TTS: English prompt
        st.audio(speak(f"How do you say {eng}?", lang='en'), format="audio/mp3")
    else:
        # Back: Croatian, white bg, black text
        st.markdown(card_style.format(
            bg="background:white;",
            color="color:black;",
            text=cro
        ), unsafe_allow_html=True)
        if st.button("Flip Back"):
            st.session_state.show_back = False
        # TTS: Croatian (if supported)
        if st.button("Repeat Croatian"):
            st.audio(speak(cro, lang='hr'), format="audio/mp3")
        if st.button("Repeat English"):
            st.audio(speak(eng, lang='en'), format="audio/mp3")

        # Spaced repetition buttons (optional)
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Got it!"):
                # Implement spaced repetition logic here
                pass
        with col2:
            if st.button("Didn't know"):
                # Implement spaced repetition logic here
                pass

        # Next card
        if st.button("Next Card"):
            st.session_state.current += 1
            st.session_state.show_back = False
            if st.session_state.current >= len(st.session_state.cards):
                st.session_state.current = 0
                st.session_state.card_order = random.sample(range(len(st.session_state.cards)), len(st.session_state.cards))

    # Progress bar
    st.progress((st.session_state.current+1)/len(st.session_state.cards))

# Light/Dark mode toggle (Streamlit handles this in settings or via config.toml)[7][13]

# Optional: Add custom cards, search/filter, local storage (advanced)
