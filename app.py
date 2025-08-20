import streamlit as st
from mood_analyzer import MoodAnalyzer
from music_parameters import MusicParameterProcessor

@st.cache_resource
def load_models():
    """Cache models to avoid reloading"""
    analyzer = MoodAnalyzer()
    processor = MusicParameterProcessor()
    return analyzer, processor

def main():
    st.title("🎵 Whispers of the Wires")
    st.subheader("AI-Powered Music Composition (Hugging Face)")
    
    # Load models once
    with st.spinner("Loading AI models... (First time may take a moment)"):
        analyzer, processor = load_models()
    
    # Rest of the app remains similar...
    # [Previous app.py code with analyzer and processor calls]

if __name__ == "__main__":
    main()