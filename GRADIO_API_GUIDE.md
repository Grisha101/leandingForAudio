# Gradio API Integration Guide

## How Gradio Works

Gradio creates a Python web interface that can be accessed via:
1. **Local URL**: `http://localhost:7860`
2. **Public Share URL**: Auto-generated link for remote access
3. **Direct API**: Use the REST API from JavaScript

---

## Embedding Gradio in Your Website

### Option 1: Direct iframe (Simplest)
```html
<iframe src="http://localhost:7860" 
        width="100%" 
        height="800" 
        frameborder="0">
</iframe>
```

### Option 2: Detect Server & Auto-Embed
```javascript
// Check if server is running
function checkAndEmbed() {
    fetch('http://localhost:7860/api/', { mode: 'no-cors' })
        .then(() => {
            // Server is running, embed it
            const iframe = document.createElement('iframe');
            iframe.src = 'http://localhost:7860';
            iframe.width = '100%';
            iframe.height = '800';
            document.getElementById('container').appendChild(iframe);
        })
        .catch(() => {
            console.log('Gradio server not available');
        });
}
```

### Option 3: Use Gradio API from JavaScript
```javascript
async function generateSpeech(text, voice) {
    const response = await fetch('http://localhost:7860/run/generate_speech', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            data: [text, voice, "en", 1.0, 1.0, null]
        })
    });
    
    const result = await response.json();
    const audioPath = result.data[0]; // Audio file URL
    
    // Play or download
    const audio = new Audio(audioPath);
    audio.play();
}
```

---

## Gradio Function Signature

The main function in `tts_gradio_app.py`:

```python
def generate_speech(
    text: str,           # Input text (max 5000 chars)
    voice: str,          # Voice name: alloy, echo, fable, onyx, nova, shimmer
    language: str,       # Language code: en, es, fr, de, ja, zh, it, pt
    speed: float,        # Speed multiplier: 0.5 to 2.0
    pitch: float,        # Pitch adjustment: 0.5 to 2.0
    voice_file: Audio    # Optional audio sample for cloning
) -> Tuple[tuple, str]: # Returns (sample_rate, audio_data), status_message
```

---

## API Call Examples

### Using cURL
```bash
curl -X POST http://localhost:7860/api/predict -H "Content-Type: application/json" \
  -d '{"data": ["Hello world", "alloy", "en", 1.0, 1.0, null]}'
```

### Using Python
```python
import requests
import json

response = requests.post('http://localhost:7860/api/predict', 
    json={'data': ['Hello world', 'alloy', 'en', 1.0, 1.0, None]}
)
print(response.json())
```

### Using JavaScript/Fetch
```javascript
fetch('http://localhost:7860/api/predict', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
        data: ['Hello world', 'alloy', 'en', 1.0, 1.0, null]
    })
})
.then(r => r.json())
.then(data => {
    // First element of data.data is the audio tuple
    const audioTuple = data.data[0];
    console.log('Audio generated:', audioTuple);
});
```

---

## Available Voices

| Voice | Style | Use Case |
|-------|-------|----------|
| alloy | Neutral | General purpose |
| echo | Deep | Narration, serious tone |
| fable | Warm | Storytelling, friendly |
| onyx | Dark | Documentary, dramatic |
| nova | Bright | Upbeat, energetic |
| shimmer | Clear | Clear, professional |

---

## Language Support

| Code | Language |
|------|----------|
| en | English |
| es | Spanish |
| fr | French |
| de | German |
| ja | Japanese |
| zh | Chinese |
| it | Italian |
| pt | Portuguese |

---

## Response Format

### Success Response
```json
{
    "data": [
        [44100, [0.1, 0.2, -0.1, ...]],  // (sample_rate, audio_array)
        "✓ Generated English speech with alloy voice"
    ]
}
```

### Error Response
```json
{
    "data": [
        null,
        "Error: Text exceeds 5000 characters"
    ]
}
```

---

## Complete HTML Integration Example

```html
<!DOCTYPE html>
<html>
<head>
    <title>TTS Demo</title>
    <style>
        body { font-family: Arial; }
        textarea { width: 100%; height: 100px; }
        button { padding: 10px 20px; cursor: pointer; }
        audio { width: 100%; margin-top: 20px; }
    </style>
</head>
<body>
    <h1>Text to Speech Generator</h1>
    
    <textarea id="textInput" placeholder="Enter text..."></textarea>
    
    <select id="voiceSelect">
        <option value="alloy">Alloy</option>
        <option value="echo">Echo</option>
        <option value="fable">Fable</option>
        <option value="onyx">Onyx</option>
        <option value="nova">Nova</option>
        <option value="shimmer">Shimmer</option>
    </select>
    
    <button onclick="generateSpeech()">Generate</button>
    
    <audio id="audioPlayer" controls style="display:none;"></audio>
    <div id="status"></div>

    <script>
        async function generateSpeech() {
            const text = document.getElementById('textInput').value;
            const voice = document.getElementById('voiceSelect').value;
            
            try {
                const response = await fetch('http://localhost:7860/api/predict', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        data: [text, voice, 'en', 1.0, 1.0, null]
                    })
                });
                
                const result = await response.json();
                const audioData = result.data[0];
                const status = result.data[1];
                
                // Display status
                document.getElementById('status').textContent = status;
                
                if (audioData) {
                    // Convert audio data to playable format
                    // This requires additional processing with Web Audio API
                    console.log('Audio data received:', audioData);
                }
            } catch (error) {
                document.getElementById('status').textContent = 'Error: ' + error.message;
            }
        }
    </script>
</body>
</html>
```

---

## Handling Audio Data

The Gradio API returns audio as `[sample_rate, audio_array]`. To play it:

```javascript
// Convert to WAV blob
function createWaveFile(sampleRate, audioArray) {
    const channels = [new Float32Array(audioArray)];
    const length = audioArray.length * channels.length * 2 + 44;
    const buffer = new ArrayBuffer(length);
    const view = new DataView(buffer);
    
    // WAV header
    const writeString = pos => (s, o) => {
        for (let i = 0; i < s.length; i++) {
            view.setUint8(pos + o + i, s.charCodeAt(i));
        }
    };
    
    writeString(0, 'RIFF');
    view.setUint32(4, length - 8, true);
    writeString(8, 'WAVE');
    writeString(12, 'fmt ');
    view.setUint32(16, 16, true);
    view.setUint16(20, 1, true);
    view.setUint16(22, 1, true);
    view.setUint32(24, sampleRate, true);
    view.setUint32(28, sampleRate * 2, true);
    view.setUint16(32, 2, true);
    view.setUint16(34, 16, true);
    writeString(36, 'data');
    view.setUint32(40, length - 44, true);
    
    // Audio samples
    let pos = 44;
    for (let i = 0; i < audioArray.length; i++) {
        const s = Math.max(-1, Math.min(1, audioArray[i]));
        view.setInt16(pos, s < 0 ? s * 0x8000 : s * 0x7FFF, true);
        pos += 2;
    }
    
    return new Blob([buffer], { type: 'audio/wav' });
}

// Usage
const response = await fetch('http://localhost:7860/api/predict', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
        data: ['Hello', 'alloy', 'en', 1.0, 1.0, null]
    })
});

const result = await response.json();
const [sampleRate, audioArray] = result.data[0];
const wavBlob = createWaveFile(sampleRate, audioArray);
const audioUrl = URL.createObjectURL(wavBlob);

// Play
const audio = new Audio(audioUrl);
audio.play();
```

---

## Advanced: Creating a Custom Wrapper

```python
# tts_wrapper.py
import requests
from typing import Tuple

class GradioTTSClient:
    def __init__(self, server_url: str = 'http://localhost:7860'):
        self.server_url = server_url
        self.api_endpoint = f'{server_url}/api/predict'
    
    def generate(self, text: str, voice: str = 'alloy', 
                 language: str = 'en', speed: float = 1.0) -> Tuple:
        """Generate speech using Gradio backend"""
        payload = {
            'data': [text, voice, language, speed, 1.0, None]
        }
        response = requests.post(self.api_endpoint, json=payload)
        result = response.json()
        return result['data']

# Usage
client = GradioTTSClient()
audio_data, message = client.generate('Hello world', voice='nova')
print(message)
```

---

## Deployment Options

### Option 1: Local Only
```bash
python tts_gradio_app.py
# Access at http://localhost:7860
```

### Option 2: With Public Share
Gradio automatically generates a public URL when you add `share=True`:
Already enabled in the code!

### Option 3: Deploy to Hugging Face Spaces
```bash
# Create a Hugging Face Space and push your code
# Gradio will run automatically on Hugging Face infrastructure
```

### Option 4: Docker
```dockerfile
FROM python:3.9

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY tts_gradio_app.py .

EXPOSE 7860
CMD ["python", "tts_gradio_app.py"]
```

---

## Performance Tips

1. **Caching**: Responses are cached for identical inputs
2. **Batching**: Process multiple requests in batch mode
3. **Async**: Use asyncio for non-blocking operations
4. **GPU**: If available, Gradio will use GPU for faster processing

---

## Security Considerations

1. **Always validate user input** (already done in code)
2. **Limit request rate** when deploying publicly
3. **Use authentication** for production
4. **Keep API keys private** (don't commit to git)
5. **Enable HTTPS** for public deployments

---

## Next Steps

1. Run `python tts_gradio_app.py` in your project directory
2. Open http://localhost:7860 in your browser
3. Test the TTS generation
4. Visit `index.html` to access from the website
5. Integrate with your application using the API

For detailed info, see `SETUP_GUIDE.md`
