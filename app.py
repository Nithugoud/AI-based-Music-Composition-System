import streamlit as st
from mood_analyzer import MoodAnalyzer
from music_params import MusicParameterProcessor
from musicgen_engine import MusicGenEngine
from auth import (
    init_session_state, check_authentication, show_login_form, 
    show_register_form, show_user_profile, require_authentication
)
import json

@st.cache_resource
def load_models():
    """Cache models to avoid reloading"""
    analyzer = MoodAnalyzer()
    processor = MusicParameterProcessor()
    musicgen = MusicGenEngine()
    return analyzer, processor, musicgen

@require_authentication
def generate_music_interface(analyzer, processor, musicgen):
    """Main music generation interface - requires authentication"""
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
                
                # Save to user's music history
                if st.session_state.user_info:
                    st.session_state.auth_manager.save_music_generation(
                        st.session_state.user_info['id'],
                        user_input,
                        result['mood'],
                        result['energy'],
                        result['sentiment'],
                        music_params,
                        mp3_path
                    )
                
                with open(mp3_path, "rb") as f:
                    audio_bytes = f.read()
                st.audio(audio_bytes, format="audio/mp3")
                st.download_button(
                    label="Download MP3",
                    data=audio_bytes,
                    file_name="music.mp3",
                    mime="audio/mp3"
                )
                st.success("Music generated and saved to your history!")

def show_music_history():
    """Display user's music generation history"""
    if not st.session_state.authenticated:
        st.warning("Please login to view your music history")
        return
    
    st.subheader("🎵 Your Music History")
    
    history = st.session_state.auth_manager.get_user_music_history(
        st.session_state.user_info['id'], 
        limit=20
    )
    
    if not history:
        st.info("No music generated yet. Start creating some music!")
        return
    
    for i, record in enumerate(history):
        mood_input, mood_category, energy_level, sentiment, music_params, file_path, created_at = record
        
        with st.expander(f"🎼 {mood_input[:50]}... - {created_at}"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.write(f"**Mood:** {mood_category}")
                st.write(f"**Sentiment:** {sentiment}")
                st.write(f"**Energy Level:** {energy_level}/10")
            
            with col2:
                st.write(f"**Created:** {created_at}")
                try:
                    params = eval(music_params)  # Convert string back to dict
                    st.write("**Musical Parameters:**")
                    st.json(params)
                except:
                    st.write(f"**Parameters:** {music_params}")
            
            # Try to load and play the audio file if it exists
            try:
                import os
                if os.path.exists(file_path):
                    with open(file_path, "rb") as f:
                        audio_bytes = f.read()
                    st.audio(audio_bytes, format="audio/mp3")
                    st.download_button(
                        label=f"Download #{i+1}",
                        data=audio_bytes,
                        file_name=f"music_{i+1}.mp3",
                        mime="audio/mp3",
                        key=f"download_{i}"
                    )
                else:
                    st.warning("Audio file no longer available")
            except Exception as e:
                st.error(f"Error loading audio: {str(e)}")

def main():
    # Configure page
    st.set_page_config(
        page_title="Whispers of the Wires",
        page_icon="🎵",
        layout="wide"
    )
    
    # Initialize authentication
    init_session_state()
    
    st.title("🎵 Whispers of the Wires")
    st.subheader("AI-Powered Music Composition System")
    
    # Check if user is authenticated
    is_authenticated = check_authentication()
    
    # Sidebar for authentication and navigation
    with st.sidebar:
        if is_authenticated:
            show_user_profile()
            
            st.markdown("---")
            page = st.selectbox(
                "Navigation",
                ["🎵 Generate Music", "📚 Music History", "👤 Profile"]
            )
        else:
            st.markdown("### Welcome!")
            st.markdown("Please login or register to start creating music.")
            
            auth_choice = st.radio(
                "Choose an option:",
                ["Login", "Register"]
            )
    
    # Main content area
    if is_authenticated:
        # Load models once for authenticated users
        if 'models_loaded' not in st.session_state:
            with st.spinner("Loading AI models... (First time may take a moment)"):
                analyzer, processor, musicgen = load_models()
                st.session_state.models_loaded = True
                st.session_state.analyzer = analyzer
                st.session_state.processor = processor
                st.session_state.musicgen = musicgen
        
        # Navigation
        if page == "🎵 Generate Music":
            generate_music_interface(
                st.session_state.analyzer, 
                st.session_state.processor, 
                st.session_state.musicgen
            )
        elif page == "📚 Music History":
            show_music_history()
        elif page == "👤 Profile":
            st.subheader("👤 User Profile")
            st.write(f"**Username:** {st.session_state.user_info['username']}")
            st.write(f"**Email:** {st.session_state.user_info['email']}")
            
            # Show some statistics
            history = st.session_state.auth_manager.get_user_music_history(
                st.session_state.user_info['id'], 
                limit=100
            )
            st.write(f"**Total Music Generated:** {len(history)}")
            
            if history:
                # Get most common mood
                moods = [record[1] for record in history if record[1]]
                if moods:
                    most_common_mood = max(set(moods), key=moods.count)
                    st.write(f"**Most Generated Mood:** {most_common_mood}")
    
    else:
        # Show authentication forms
        if auth_choice == "Login":
            show_login_form()
        else:
            show_register_form()
        
        # Show a preview of what's available after login
        st.markdown("---")
        st.markdown("### 🎵 What you can do after logging in:")
        st.markdown("- **Generate AI Music** based on your mood and preferences")
        st.markdown("- **Save Your Creations** to your personal music library")
        st.markdown("- **View Your History** of all generated music")
        st.markdown("- **Download Your Music** anytime")
        st.markdown("- **Track Your Musical Journey** with mood analytics")

if __name__ == "__main__":
    main()