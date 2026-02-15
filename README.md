# 🔥 Naruto Jutsu Recognition System

An interactive computer vision system that recognizes Naruto hand signs (jutsus) in real-time using MediaPipe and OpenCV. Perform hand sign sequences to trigger visual and sound effects!

![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)
![OpenCV](https://img.shields.io/badge/OpenCV-4.8+-green.svg)
![MediaPipe](https://img.shields.io/badge/MediaPipe-0.10+-orange.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

## ✨ Features

- **Real-time Hand Tracking**: Detects up to 2 hands simultaneously with 21 landmarks per hand
- **Gesture Recognition**: Identifies 12 Naruto hand signs (Tiger, Ram, Snake, Dragon, Boar, Dog, Monkey, Rabbit, Ox, Bird, Horse, Rat)
- **Sequence Detection**: Recognizes ordered hand sign sequences to detect jutsus
- **Visual Effects**: Particle systems (fire, water, lightning, smoke, earth) and screen flash effects
- **Sound Effects**: Multi-backend sound system with per-jutsu audio feedback
- **Guided Mode**: Visual sequence progression with highlighting and instant detection
- **Performance**: Runs at ≥15 FPS with <300ms latency on standard webcams

## 🎯 Supported Jutsus

| Jutsu | Sequence | Time Window |
|-------|----------|-------------|
| Fireball Jutsu | Snake → Ram → Tiger | 5s |
| Shadow Clone | Ram → Snake → Tiger | 4s |
| Water Dragon | Ox → Monkey → Dragon → Rat → Boar → Bird | 6s |
| Earth Wall | Snake → Ram → Horse | 4s |
| Summoning | Boar → Dog → Bird → Monkey → Ram | 7s |
| Chidori | Ox → Rabbit → Monkey | 4s |

## 📋 Requirements

### System Requirements
- Python 3.9 or higher
- Webcam
- Windows/Linux/macOS (tested on Windows)

### Python Dependencies
```txt
opencv-python>=4.8.0
mediapipe>=0.10.0
numpy>=1.24.0
pandas>=2.0.0
scikit-learn>=1.3.0
pygame>=2.5.0 (optional, for better sound)
```

## 🚀 Quick Start

### 1. Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/naruto-jutsu-recognition.git
cd naruto-jutsu-recognition

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Run the Application

```bash
# Start in Phase 3 mode (sequence detection with effects)
python naruto_jutsu/src/main.py
```

### Controls
- **Q**: Quit
- **1**: Switch to Phase 1 (Hand tracking only)
- **2**: Switch to Phase 2 (Gesture recognition)
- **3**: Switch to Phase 3 (Sequence detection)
- **M**: Open jutsu selection menu

## 📚 Project Structure

```
naruto-jutsu-recognition/
├── naruto_jutsu/
│   ├── data/                    # Training data (CSV files)
│   ├── effects/                 # Visual effect assets
│   ├── images/                  # Gesture reference images
│   ├── models/                  # Trained ML models
│   ├── sounds/                  # Sound effect files
│   ├── src/                     # Source code
│   │   ├── main.py             # Main application entry point
│   │   ├── hand_tracker.py     # MediaPipe hand tracking
│   │   ├── feature_extractor.py # Feature extraction (72 features)
│   │   ├── gesture_classifier.py # Random Forest classifier
│   │   ├── sequence_detector.py # FSM sequence detection
│   │   ├── effects_engine.py   # Sound and visual effects
│   │   ├── capture_data.py     # Data collection tool
│   │   └── train_model.py      # Model training script
│   ├── tests/                   # Unit and performance tests
│   │   ├── test_feature_extractor.py
│   │   ├── test_sequence_detector.py
│   │   ├── test_effects_engine.py
│   │   ├── run_tests.py        # Test runner
│   │   └── performance_test.py  # Performance validation
│   └── jutsus.json             # Jutsu definitions
├── prd.md                       # Product requirements
├── todo.md                      # Implementation roadmap
├── requirements.txt             # Python dependencies
└── README.md                    # This file
```

## 🎓 Training Your Own Model

### 1. Collect Training Data

```bash
# Launch data collection tool
python naruto_jutsu/src/capture_data.py

# Follow on-screen instructions:
# - Select gesture to capture
# - Perform hand sign for reference image
# - Capture 200+ samples per gesture
# - Data saved to naruto_jutsu/data/
```

### 2. Train the Model

```bash
# Train Random Forest classifier
python naruto_jutsu/src/train_model.py

# Model saved to: naruto_jutsu/models/gesture_classifier.pkl
```

### 3. Test the Model

```bash
# Run in Phase 2 mode to test gesture recognition
python naruto_jutsu/src/main.py
# Press '2' to switch to Phase 2
```

## 🧪 Testing

### Run Unit Tests

```bash
# Run all unit tests
python naruto_jutsu/tests/run_tests.py

# Tests include:
# - Feature extraction (33 single hand + 72 two-hand features)
# - Sequence detection (FSM, time windows, targeting)
# - Effects engine (sounds, particles, flash)
```

### Run Performance Tests

```bash
# Validate FPS and latency
python naruto_jutsu/tests/performance_test.py

# Options:
# --camera 0    # Camera ID
# --duration 30 # Test duration in seconds

# Target metrics:
# - FPS: >= 15 FPS
# - Latency: < 300ms
```

## 🎨 How It Works

### Architecture

```
Webcam Feed
    ↓
MediaPipe Hand Tracking (21 landmarks × 2 hands)
    ↓
Feature Extraction (72-dimensional vector)
    ↓
Random Forest Classifier (12 gestures)
    ↓
Sequence Detector (FSM with time windows)
    ↓
Effects Engine (sound + particles + flash)
    ↓
Display (OpenCV window with UI overlay)
```

### Feature Extraction

**Single Hand (33 features):**
- 20 normalized distances (tip-to-wrist for each finger)
- 8 angles between finger segments
- 5 finger states (open/closed boolean)

**Two Hands (72 features):**
- 33 features for left hand
- 33 features for right hand
- 6 inter-hand features (distance, relative position)

### Sequence Detection

- **FSM-based**: Finite State Machine tracks ordered gestures
- **Time Windows**: Each jutsu has a specific time limit
- **Confidence Filtering**: Only accepts gestures with >70% confidence
- **Instant Detection**: No hold time in guided mode
- **Sound Feedback**: Plays sound on each gesture step (with debounce)

### Effects System

- **Multi-backend Sound**: Auto-detects pygame → playsound → winsound
- **Particle Types**: Fire, water, lightning, smoke, earth
- **Screen Flash**: Color-coded flash effect on jutsu detection
- **Extended Duration**: Effects visible for 3 seconds, name for 10 seconds

## 🔧 Configuration

### Jutsu Definitions (`jutsus.json`)

```json
{
  "jutsus": [
    {
      "id": "fireball",
      "name": "Fire Style: Fireball Jutsu",
      "japanese": "Katon: Gōkakyū no Jutsu",
      "sequence": ["Snake", "Ram", "Tiger"],
      "time_window": 5.0,
      "description": "A large ball of flame.",
      "effects": {
        "sound": "fireball.wav",
        "animation": "fire_burst",
        "color": [255, 100, 0],
        "particle_type": "fire"
      }
    }
  ],
  "settings": {
    "confidence_threshold": 0.7,
    "gesture_hold_time": 0.5,
    "reset_on_invalid": true
  }
}
```

### Adding New Jutsus

1. Add entry to `jutsus.json` with sequence and effects
2. Add corresponding sound file to `naruto_jutsu/sounds/`
3. System will automatically detect new jutsu

## 📊 Performance Metrics

Tested on: Windows 11, Intel i7, 16GB RAM, Built-in webcam (1280x720)

| Metric | Target | Achieved | Status |
|--------|--------|----------|--------|
| FPS (Hand Tracking) | ≥15 FPS | ~30 FPS | ✅ |
| FPS (Full Pipeline) | ≥15 FPS | ~25 FPS | ✅ |
| Latency (Recognition) | <300ms | ~50ms | ✅ |
| Accuracy (Good Lighting) | ≥90% | ~92% | ✅ |

## 🎬 Demo

### Phase 1: Hand Tracking
- Shows 21 landmarks per hand
- FPS counter
- Finger state detection

### Phase 2: Gesture Recognition
- Real-time gesture classification
- Confidence display
- Latency measurement

### Phase 3: Sequence Detection + Effects
- Visual sequence progression
- Guided mode with highlighting
- Particle effects and screen flash
- Sound feedback on each step
- Jutsu name display (10 seconds)

## 🐛 Troubleshooting

### Camera Not Opening
```bash
# Try different camera ID
python naruto_jutsu/src/main.py --camera 1
```

### Low FPS
- Reduce resolution in main.py (default: 1280x720)
- Close other applications
- Ensure good lighting for faster detection

### Classifier Not Found
```bash
# Collect data and train model first
python naruto_jutsu/src/capture_data.py
python naruto_jutsu/src/train_model.py
```

### Sound Not Playing
- Install pygame for better sound: `pip install pygame`
- Check that .wav files exist in `naruto_jutsu/sounds/`
- System will fall back to winsound (Windows) if pygame unavailable

## 📝 Development Phases

- ✅ **Phase 1**: Hand tracking (MediaPipe, 21 landmarks, 2 hands)
- ✅ **Phase 2**: Gesture recognition (Random Forest, 72 features, 12 gestures)
- ✅ **Phase 3**: Sequence detection (FSM, guided mode, visual feedback)
- ✅ **Phase 4**: Effects engine (sound, particles, screen flash)
- 🔄 **Phase 5**: Testing & documentation (unit tests, performance tests, README)

## 🤝 Contributing

Contributions welcome! Areas for improvement:

- **More Jutsu**: Add more hand sign sequences
- **Better Effects**: Enhanced particle systems and animations
- **Mobile Support**: Port to mobile platforms
- **Accuracy**: Improve gesture classification with deep learning
- **UI**: Add Tkinter/PyQt GUI for better UX

## 📄 License

MIT License - see LICENSE file for details.

## 🙏 Acknowledgments

- **MediaPipe**: Google's ML pipeline for hand tracking
- **OpenCV**: Computer vision library
- **Naruto**: Masashi Kishimoto's manga/anime series

## 📧 Contact

Questions? Issues? Feel free to open an issue or reach out!

---

**Made with ❤️ for anime fans and computer vision enthusiasts**

🔥 Believe it! 🔥
