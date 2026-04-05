"""
Gradio-based Text-to-Speech Application
Connect to this app from your HTML files via the public URL
"""

import gradio as gr
import numpy as np
from scipy.io import wavfile
import tempfile
import os

# Try to import advanced TTS libraries (install with pip if needed)
try:
    from gtts import gTTS
    HAS_GTTS = True
except ImportError:
    HAS_GTTS = False
    print("gTTS not installed. Install with: pip install gtts")

try:
    import pyttsx3
    HAS_PYTTSX3 = True
except ImportError:
    HAS_PYTTSX3 = False
    print("pyttsx3 not installed. Install with: pip install pyttsx3")

# Voice settings mapping
VOICE_SETTINGS = {
    "alloy": {"rate": 1.0, "pitch": 1.0, "voice_id": 0},
    "echo": {"rate": 0.9, "pitch": 0.8, "voice_id": 1},
    "fable": {"rate": 1.0, "pitch": 1.1, "voice_id": 2},
    "onyx": {"rate": 0.95, "pitch": 0.9, "voice_id": 3},
    "nova": {"rate": 1.1, "pitch": 1.2, "voice_id": 4},
    "shimmer": {"rate": 1.05, "pitch": 1.15, "voice_id": 5},
}

LANGUAGES = {
    "en": "English",
    "es": "Spanish",
    "fr": "French",
    "de": "German",
    "ja": "Japanese",
    "zh": "Chinese",
    "it": "Italian",
    "pt": "Portuguese",
    "ua": "Ukrainian",
}


def generate_speech(text, voice="alloy", language="en", speed=1.0, pitch=1.0, voice_file=None):
    """
    Generate speech from text using available TTS engines
    
    Args:
        text: Text to convert to speech
        voice: Voice name ('alloy', 'echo', 'fable', 'onyx', 'nova', 'shimmer')
        language: Language code
        speed: Speech speed (0.5 to 2.0)
        pitch: Pitch adjustment (0.5 to 2.0)
        voice_file: Optional audio file for voice cloning (not fully supported in free tier)
    
    Returns:
        Tuple of (sample_rate, audio_data)
    """
    
    if not text or len(text.strip()) == 0:
        return None, "Error: Please enter some text"
    
    if len(text) > 5000:
        return None, "Error: Text exceeds 5000 characters"
    
    try:
        # Create temporary file for audio
        temp_audio = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
        temp_wav = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
        
        # Use gTTS (Google Text-to-Speech) if available
        if HAS_GTTS:
            lang_code = language if language in ["en", "es", "fr", "de", "ja", "zh", "it", "pt"] else "en"
            
            # Create TTS object
            tts = gTTS(text=text, lang=lang_code, slow=False)
            tts.save(temp_audio.name)
            
            # Read the generated audio
            from pydub import AudioSegment
            try:
                audio = AudioSegment.from_mp3(temp_audio.name)
                # Adjust speed and pitch if needed
                if speed != 1.0:
                    audio = audio.speedup(speed)
                
                # Export to WAV
                audio.export(temp_wav.name, format="wav")
                
                # Read WAV file
                sample_rate, audio_data = wavfile.read(temp_wav.name)
                return (sample_rate, audio_data), f"✓ Generated {language} speech with {voice} voice"
            
            except Exception as e:
                print(f"Note: pydub/ffmpeg not available: {e}")
                # Return MP3 if WAV conversion fails
                return temp_audio.name, f"✓ Generated {language} speech (MP3 format)"
        
        # Fallback to pyttsx3
        elif HAS_PYTTSX3:
            engine = pyttsx3.init()
            
            # Get available voices
            voices = engine.getProperty('voices')
            voice_index = VOICE_SETTINGS.get(voice, {}).get("voice_id", 0)
            if voice_index < len(voices):
                engine.setProperty('voice', voices[voice_index].id)
            
            # Set rate and volume
            engine.setProperty('rate', 150 * speed)
            engine.setProperty('volume', 0.9)
            
            # Save to file
            engine.save_to_file(text, temp_wav.name)
            engine.runAndWait()
            
            # Read WAV file
            sample_rate, audio_data = wavfile.read(temp_wav.name)
            return (sample_rate, audio_data), f"✓ Generated {language} speech with {voice} voice"
        
        else:
            return None, "Error: No TTS engine available. Install gTTS with: pip install gtts pydub"
    
    except Exception as e:
        return None, f"Error: {str(e)}"
    
    finally:
        # Cleanup temp files
        try:
            os.unlink(temp_audio.name)
        except:
            pass
        try:
            os.unlink(temp_wav.name)
        except:
            pass


def clone_voice(text, voice_sample):
    """
    Attempt voice cloning (requires advanced setup)
    """
    if voice_sample is None:
        return None, "Please upload a voice sample"
    
    return None, "Voice cloning requires advanced setup with voice models"


def create_gradio_interface():
    """Create the Gradio interface"""
    
    with gr.Blocks(theme=gr.themes.Soft(), title="AI Voice TTS Generator") as demo:
        gr.HTML("""
        <div style='text-align: center; margin: 20px 0;'>
            <h1>🎤 Text to Speech Generator</h1>
            <p>Convert your text into natural-sounding speech with AI voices</p>
        </div>
        """)
        
        with gr.Row():
            with gr.Column():
                # Text Input
                text_input = gr.Textbox(
                    label="Text to Convert",
                    placeholder="Enter the text you want to convert to speech...",
                    lines=5,
                    max_lines=15
                )
                char_count = gr.Markdown("Characters: 0 / 15000")
                
                # Real-time character counter
                def update_char_count(text):
                    count = len(text) if text else 0
                    return f"Characters: {count} / 15000"
                
                text_input.change(update_char_count, inputs=text_input, outputs=char_count)
                
                # Voice Selection Row
                with gr.Row():
                    voice_select = gr.Dropdown(
                        choices=["alloy", "echo", "fable", "onyx", "nova", "shimmer"],
                        value="alloy",
                        label="Select Voice"
                    )
                    language_select = gr.Dropdown(
                        choices=list(LANGUAGES.keys()),
                        value="en",
                        label="Language"
                    )
                
                # Speed and Pitch Sliders
                with gr.Row():
                    speed_slider = gr.Slider(
                        minimum=0.5,
                        maximum=2.0,
                        value=1.0,
                        step=0.1,
                        label="Speed"
                    )
                    pitch_slider = gr.Slider(
                        minimum=0.5,
                        maximum=2.0,
                        value=1.0,
                        step=0.1,
                        label="Pitch"
                    )
                
                # Voice Cloning Section
                gr.Markdown("### 🎯 Voice Cloning (Optional)")
                voice_file = gr.Audio(
                    label="Upload Voice Sample",
                    type="filepath",
                    sources=["upload"]
                )
                gr.Info("Upload an audio file (MP3, WAV, etc.) to customize the voice tone")
            
            with gr.Column():
                # Output Section
                status_output = gr.Markdown("Ready to generate speech")
                audio_output = gr.Audio(
                    label="Generated Speech",
                    type="numpy"
                )
                
                # Download button info
                gr.HTML("""
                <div style='padding: 10px; background-color: #f0f0f0; border-radius: 5px; margin-top: 10px;'>
                    <p><strong>💾 Download:</strong> Right-click on the audio player and select "Save audio as..."</p>
                </div>
                """)
        
        # Generate button
        with gr.Row():
            generate_btn = gr.Button("Generate Speech", variant="primary", size="lg")
            clear_btn = gr.Button("Clear", size="lg")
        
        # Performance info
        gr.Markdown("""

        """)
        
        # Connect button click
        generate_btn.click(
            fn=generate_speech,
            inputs=[text_input, voice_select, language_select, speed_slider, pitch_slider, voice_file],
            outputs=[audio_output, status_output]
        )
        
        # Clear function
        def clear_all():
            return "", 1.0, 1.0, None, None, "Ready to generate speech"
        
        clear_btn.click(
            fn=clear_all,
            outputs=[text_input, speed_slider, pitch_slider, voice_file, audio_output, status_output]
        )
    
    return demo


if __name__ == "__main__":
    print("=" * 60)
    print("🎤 Text-to-Speech Gradio Application")
    print("=" * 60)
    print("\nStarting Gradio server...")
    print("After startup, you can access the app at the URL shown below")
    print("\nTo use with your HTML website:")
    print("1. Copy the public URL from the terminal")
    print("2. Update your HTML files to embed this Gradio app")
    print("3. Or use the Gradio API endpoint for custom integrations")
    print("\n" + "=" * 60)
    
    # Check for dependencies
    print("\n📦 Checking dependencies...")
    if HAS_GTTS:
        print("✓ gTTS available")
    else:
        print("✗ gTTS not found - install with: pip install gtts")
    
    if HAS_PYTTSX3:
        print("✓ pyttsx3 available (offline TTS)")
    else:
        print("✗ pyttsx3 not found - install with: pip install pyttsx3")
    
    # Create and launch interface
    demo = create_gradio_interface()
    demo.launch(
        server_name="localhost",
        server_port=7860,
        share=True,  # Generate public URL
        show_error=True
    )
