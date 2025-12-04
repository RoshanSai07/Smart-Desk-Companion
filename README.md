# 🌌 NEXUS Quantum Interface

## Smart Desk Companion System

A futuristic AI-powered smart desk companion that provides real-time emotion analysis, intelligent conversation, and ambient lighting control.

![NEXUS Interface](https://img.shields.io/badge/Status-Active-brightgreen)
![Python](https://img.shields.io/badge/Python-3.8+-blue)
![Flask](https://img.shields.io/badge/Flask-3.1.2-red)
![AI](https://img.shields.io/badge/AI-Quantum%20Enhanced-purple)

## ✨ Features

### 🧠 Neural Emotion Engine

- **Real-time emotion analysis** using DeepFace
- **Multiple AI backends** (OpenCV, MTCNN, RetinaFace)
- **Emotional smoothing** and pattern recognition
- **Rate limiting** and performance optimization

### 💫 Quantum AI Companion

- **Intelligent conversation** with emotional context
- **Free AI integration** (Ollama, Hugging Face)
- **Memory persistence** across sessions
- **Sci-fi themed responses** with psychological insights

### 🌈 Cybernetic Interface

- **Emotional lighting** that responds to your mood
- **LED pattern control** with color-coded emotions
- **System diagnostics** and health monitoring
- **Ambient environment** creation

### 🎙️ Neural Text-to-Speech

- **Voice synthesis** with multiple profiles
- **Queue management** for smooth audio
- **Priority-based** speech modulation
- **Background processing**

### 📹 Webcam Integration

- **Real-time emotion capture** from webcam
- **Live frame streaming** for analysis
- **Automatic emotion detection** at intervals
- **Camera status monitoring**

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- Webcam (optional, for real-time analysis)
- 4GB+ RAM recommended
- Windows/Linux/macOS

### Installation

1. **Clone or download** the project files
2. **Install dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

3. **Run the startup script**:

   ```bash
   python start_nexus.py
   ```

4. **Open your browser** to `http://localhost:5000`

### Manual Setup

If you prefer manual setup:

```bash
# Install dependencies
pip install flask deepface opencv-python pillow numpy requests pyttsx3 transformers

# Run the application
python app.py
```

## 🎮 Usage Guide

### 1. System Activation

- Click **"ACTIVATE QUANTUM SYSTEM"** to initialize all components
- Wait for all systems to come online (green indicators)

### 2. Emotion Analysis

- **Upload an image** for emotion analysis
- Or **start webcam** for real-time emotion detection
- View detailed emotion spectrum and confidence levels

### 3. AI Companion

- **Chat with NEXUS** using the conversation interface
- Ask for **quantum insights** based on your emotional state
- Use **neural speech** to hear responses aloud

### 4. Ambient Control

- **Emotional lighting** responds to detected emotions
- **System diagnostics** show component health
- **Dashboard** displays real-time metrics

## 🔧 Configuration

### Environment Variables

```bash
# Optional: Set Hugging Face token for cloud AI
export HUGGINGFACE_TOKEN="your_token_here"

# Optional: Set Flask environment
export FLASK_ENV="development"  # or "production"
```

### AI Backend Options

- **Simulation Mode** (default): Free, works offline
- **Ollama**: Local AI models (install separately)
- **Hugging Face**: Cloud AI with API token

### Camera Settings

- **Default camera**: Index 0
- **Resolution**: 640x480
- **Frame rate**: 30 FPS
- **Analysis interval**: 2 seconds

## 📊 API Endpoints

### Core Endpoints

- `POST /api/quantum_init` - Initialize quantum session
- `POST /api/neural_scan` - Analyze uploaded image
- `POST /api/quantum_chat` - Chat with AI companion
- `POST /api/neural_synthesis` - Text-to-speech synthesis

### Webcam Endpoints

- `POST /api/webcam/start` - Start webcam capture
- `POST /api/webcam/stop` - Stop webcam capture
- `GET /api/webcam/frame` - Get latest frame
- `GET /api/webcam/status` - Camera status

### Monitoring Endpoints

- `GET /api/health` - System health check
- `GET /api/metrics` - Performance metrics
- `GET /api/quantum_dashboard` - Session dashboard

## 🛠️ Troubleshooting

### Common Issues

**1. DeepFace Installation Issues**

```bash
# Try installing TensorFlow first
pip install tensorflow
pip install deepface
```

**2. Camera Not Detected**

- Check camera permissions
- Try different camera index (0, 1, 2)
- Ensure no other apps are using the camera

**3. Memory Issues**

- Reduce `max_concurrent_scans` in emotion engine
- Lower image resolution
- Close other applications

**4. AI Responses Not Working**

- Check internet connection for Hugging Face
- Install Ollama for local AI
- Fallback to simulation mode

### Performance Optimization

**For Better Performance:**

- Use SSD storage
- Increase RAM to 8GB+
- Close unnecessary applications
- Use smaller image sizes

**For Lower Resource Usage:**

- Increase `cooldown_seconds` in emotion engine
- Reduce `rate_limit_max_requests`
- Disable webcam if not needed

## 🔒 Security & Privacy

- **Local Processing**: All emotion analysis happens locally
- **No Data Collection**: No personal data is stored or transmitted
- **Optional Cloud AI**: Only used if you provide API tokens
- **File Cleanup**: Temporary files are automatically removed

## 🎨 Customization

### Adding New Emotions

Edit `emotion.py` to add custom emotion mappings:

```python
emotion_mapping = {
    'your_emotion': 'mapped_emotion',
    # ... existing mappings
}
```

### Custom AI Responses

Modify `spark.py` to add new response patterns:

```python
response_patterns = {
    'your_topic': [
        "Your custom response 1",
        "Your custom response 2",
    ]
}
```

### LED Patterns

Update `pi_control.py` for custom lighting:

```python
cybernetic_patterns = {
    'your_emotion': {
        'color': '#HEXCODE',
        'pattern': 'pattern_name',
        'speed': 'speed_level'
    }
}
```

## 📈 Advanced Features

### Integration Possibilities

- **Smart Home**: Connect to Philips Hue, LIFX
- **Productivity**: Integrate with task managers
- **Health**: Connect to fitness trackers
- **Automation**: Desktop automation scripts

### Development

- **Plugin System**: Add custom modules
- **API Extensions**: Create new endpoints
- **UI Themes**: Customize the interface
- **AI Models**: Integrate other AI services

## 🤝 Contributing

Contributions are welcome! Areas for improvement:

- Additional AI backends
- More emotion detection models
- Enhanced UI/UX
- Performance optimizations
- Documentation improvements

## 📄 License

This project is open source. Feel free to modify and distribute.

## 🙏 Acknowledgments

- **DeepFace** for emotion recognition
- **Flask** for the web framework
- **OpenCV** for computer vision
- **Transformers** for AI capabilities

---

**🌌 Welcome to the future of smart desk companions!**

_"The quantum field between human consciousness and artificial intelligence creates infinite possibilities for growth and understanding."_ - NEXUS
