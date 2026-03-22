# 🎤 AI Voice Generator - Gradio TTS Setup Guide

## Quick Start

### 1. Install Dependencies
```bash
# Navigate to your project directory
cd c:\Users\wise\Documents\projects\leandingForAudio

# Install all required packages
pip install -r requirements.txt
```

### 2. Start the Gradio Server
```bash
python tts_gradio_app.py
```

You will see output like:
```
Running on local URL:  http://localhost:7860
Running on public URL: https://[your-public-url].gradio.live
```

### 3. Access the Interface
- **Local**: http://localhost:7860
- **Website**: Open index.html and click "Start Free" on the TTS Demo page

### 4. Optional: Deploy to Public URL
The Gradio app automatically generates a public share URL that you can use to embed in your website. Look for the `Running on public URL` line in the terminal.

---

## 📦 What's Included

### Files
- **tts_gradio_app.py** - Main Gradio application with TTS functionality
- **requirements.txt** - Python dependencies
- **tts-demo.html** - Website page with Gradio integration
- **index.html** - Main landing page
- **voice-library.html** - Voice selection interface

### Features
✓ Multiple AI voices (6 options)
✓ 8+ languages
✓ Speed/pitch control
✓ Voice cloning support
✓ Free Google TTS backend
✓ Premium API integration support

---

## 🔌 Integrating Premium APIs

### ElevenLabs (Recommended)
```bash
pip install elevenlabs
```

In `tts_gradio_app.py`, modify the `generate_speech()` function:
```python
def generate_speech(text, voice="alloy", language="en", speed=1.0, pitch=1.0, voice_file=None):
    from elevenlabs import client, Voice
    
    client.api_key = "YOUR_API_KEY_HERE"
    audio = client.generate(
        text=text,
        voice=Voice(voice_id="adam"),
        model="eleven_monolingual_v1"
    )
    return audio
```

### OpenAI Text-to-Speech
```bash
pip install openai
```

```python
from openai import OpenAI

client = OpenAI(api_key="YOUR_API_KEY")
response = client.audio.speech.create(
    model="tts-1-hd",
    voice="alloy",
    input=text
)
response.stream_to_file("output.mp3")
```

### Azure Speech Services
```bash
pip install azure-cognitiveservices-speech
```

---

## 🔧 Troubleshooting

### Port 7860 already in use
Edit `tts_gradio_app.py`, find the `launch()` call, and change:
```python
demo.launch(
    server_port=7861,  # Use different port
    ...
)
```

### FFmpeg not installed
For Windows:
```bash
# Using conda
conda install -c conda-forge ffmpeg

# Using choco
choco install ffmpeg

# Or download from: https://ffmpeg.org/download.html
```

### gTTS not generating audio
Check your internet connection. gTTS requires online access to Google's servers.

### Gradio server won't start
Make sure no other instance is running:
```bash
# Kill any Python processes using port 7860
netstat -ano | findstr :7860
taskkill /PID [PID_NUMBER] /F
```

---

## 📱 Using the Web Interface

1. **Text Input**: Enter up to 5000 characters
2. **Voice Selection**: Choose from 6 AI voices
3. **Language**: Select from 8+ languages
4. **Speed**: Adjust from 0.5x to 2x
5. **Pitch**: Modify tone from 0.5 to 2.0
6. **Voice Sample** (Optional): Upload audio for voice cloning
7. **Generate**: Click to create speech
8. **Download**: Save the audio file

---

## 📡 Embedding in Your Website

The HTML page automatically detects if the Gradio server is running and embeds it as an iframe.

To use on a different port:
```html
<iframe src="http://localhost:7861"></iframe>
```

To use the public share URL:
```html
<iframe src="https://[public-url].gradio.live"></iframe>
```

---

## 🚀 Advanced: Custom Implementation

Use the Gradio API directly:
```javascript
fetch('http://localhost:7860/api/predict/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
        data: ["Hello world", "alloy", "en", 1.0, 1.0, null]
    })
})
.then(r => r.json())
.then(data => {
    // data.data[0] contains the audio URL
    document.getElementById('audio').src = data.data[0];
});
```

---

## 📞 Support

For issues:
1. Check the troubleshooting section above
2. Review Gradio docs: https://www.gradio.app
3. Check gTTS docs: https://gtts.readthedocs.io
4. API documentation:
   - ElevenLabs: https://elevenlabs.io/docs
   - OpenAI: https://platform.openai.com/docs
   - Azure: https://learn.microsoft.com/azure/cognitive-services/speech-service/

---

**Created**: March 2026
**Project**: AI Voice Generator
**Tech Stack**: Python, Gradio, HTML5, CSS3, JavaScript
