import streamlit as st
from mood_analyzer import MoodAnalyzer
from music_params import MusicParameterProcessor
from musicgen_engine import MusicGenEngine

@st.cache_resource
def load_models():
    """Cache models to avoid reloading"""
    analyzer = MoodAnalyzer()
    processor = MusicParameterProcessor()
    musicgen = MusicGenEngine()
    return analyzer, processor, musicgen

def main():
    st.title("🎵 Whispers of the Wires")
    st.subheader("AI-Powered Music Composition")
    
    # Load models once
    with st.spinner("Loading AI models... (First time may take a moment)"):
        analyzer, processor, musicgen = load_models()
    
    st.markdown("""
        Enter a mood or music description below (e.g. 'I'm feeling happy and energetic', 'I need calm music for studying'):
    """)
    user_input = st.text_input("Describe your mood or music preference:", "I'm feeling happy and energetic")

    if user_input:
        result = analyzer.analyze(user_input)
        st.write(f"**Mood:** {result['mood']}")
        st.write(f"**Sentiment:** {result['sentiment']} ({result['sentiment_score']:.2f})")
        st.write(f"**Energy Level:** {result['energy']}/10")

        # Map to musical parameters
        base_params = {
            "mood_category": result['mood'],
            "energy_level": result['energy'],
            "sentiment": result['sentiment']
        }
        music_params = processor.enhance_parameters(base_params)
        st.write("### Musical Parameters")
        st.json(music_params)

        # Music Generation Section
        st.write("---")
        st.write("## Generate Music")
        duration = st.slider("Select duration (seconds)", min_value=10, max_value=30, value=30)
        if st.button("Generate Music"):
            with st.spinner("Generating music, please wait..."):
                prompt = f"{user_input}, mood: {result['mood']}, energy: {result['energy']}, instruments: guitar, piano, drums"
                audio_tensor = musicgen.generate_music(prompt, duration=duration)
                wav_path = musicgen.tensor_to_wav(audio_tensor, filename="output.wav")
                mp3_path = musicgen.wav_to_mp3(wav_path, mp3_path="output.mp3")
                with open(mp3_path, "rb") as f:
                    audio_bytes = f.read()
                st.audio(audio_bytes, format="audio/mp3")
                st.download_button(
                    label="Download MP3",
                    data=audio_bytes,
                    file_name="music.mp3",
                    mime="audio/mp3"
                )

if __name__ == "__main__":
    main()