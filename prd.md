
# Naruto Jutsu Recognition System – Product Requirements Document (PRD)

## 1. Project Overview
**Project Name:** Naruto Jutsu Recognition System  
**Objective:** Build a Python-based real-time application using OpenCV and MediaPipe to detect Naruto hand signs (jutsus) from webcam input and trigger visual/audio effects when a jutsu is recognized.

---

## 2. Problem Statement
Anime fans and computer vision learners lack an engaging way to explore gesture recognition concepts. This project provides an interactive system that recognizes Naruto hand signs using computer vision and machine learning techniques.

---

## 3. Goals & Success Metrics
### Goals
- Detect hand signs using MediaPipe
- Recognize multiple Naruto jutsu signs
- Detect multi-step jutsu sequences
- Display animation/sound feedback

### Success Metrics
- ≥ 90% accuracy in good lighting
- ≥ 15 FPS real-time detection
- Latency < 300ms
- Successful demo recognition of all target jutsus

---

## 4. Target Users
- Computer Science students learning CV
- Anime fans
- Hackathon teams
- Developers building gesture-recognition systems

---

## 5. Scope

### In Scope
- Hand landmark detection
- Gesture classification
- Jutsu sequence detection
- UI feedback (text, sound, animation)

### Out of Scope
- VR immersive Naruto world
- Full-body combat system
- Mobile deployment (initial version)

---

## 6. Features

### 6.1 Hand Tracking
- Detect up to 2 hands
- Track 21 hand landmarks
- Extract finger positions and angles

### 6.2 Gesture Recognition
Detect predefined Naruto signs such as:
Tiger, Ram, Snake, Dragon, Boar, Dog, Monkey, Rabbit, Ox, Bird.

### 6.3 Sequence Detection
Example:
Snake → Ram → Tiger → Fireball Jutsu

System must track ordered gestures within a time window.

### 6.4 Feedback System
- Display jutsu name
- Play sound effect
- Show animation or visual effect

---

## 7. Tech Stack
Python, OpenCV, MediaPipe Hands, NumPy, Pandas, Scikit-learn/TensorFlow (optional), Tkinter/PyQt/Streamlit, pygame/playsound.

---

## 8. System Architecture
Webcam → MediaPipe → Feature Extraction → Gesture Classifier → Sequence Detector → Effects Engine → UI.

---

## 9. Functional Requirements
- Detect hand landmarks in real time.
- Classify at least 10 hand signs.
- Detect ordered gesture sequences.
- Trigger animation + sound.

---

## 10. Non-Functional Requirements
Real-time processing, works on laptop webcam, easy to add new gestures, minimal CPU usage.

---

## 11. Dataset Requirements
Capture 200+ samples per gesture, store landmarks in CSV, label data, train classifier.

---

## 12. Algorithm Design
Landmark extraction → Feature engineering → Gesture classification → Sequence FSM detection.

---

## 13. Milestones
Week 1 Hand tracking  
Week 2 Single gesture detection  
Week 3 Sequence detection  
Week 4 Effects & UI  
Week 5 Testing  

---

# 🔥 14. Advanced Jutsus To Be Implemented

## 14.1 Shadow Clone Jutsu
Sequence: Ram → Snake → Tiger  
Effects:
- Multiple cloned faces
- Smoke animation
- Echo sound

---

## 14.2 Rasengan
Detection:
- Both hands close together
- Circular hand motion tracking
Effects:
- Blue spinning energy ball
- Glow around hands
- Charging sound

---

## 14.3 Chidori
Sequence: Ox → Rabbit → Monkey  
Effects:
- Lightning animation
- Electric crackling sound
- Screen flash

---

## 14.4 Sharingan Eyes
Detection:
- Face mesh + eye tracking
- Trigger via gesture
Effects:
- Red eye overlay
- Rotating tomoe animation
- Background blur

---

## 14.5 Other Sequence-Based Jutsus

| Jutsu | Sequence |
|------|-----------|
| Fireball | Snake → Ram → Tiger |
| Water Dragon | Tiger → Snake → Monkey → Ram |
| Earth Wall | Dog → Boar → Ram |
| Summoning | Boar → Dog → Bird → Monkey → Ram |

Sequences stored in **jutsus.json** for easy extension.

---

# 🔊 15. Sound & Visual Effects Requirements
Each jutsu must trigger:
- Unique sound
- Animation overlay
- Particle effects
- Jutsu name text

Libraries: pygame, playsound, OpenCV overlays.

---

# ⚙️ 16. Motion-Based Jutsu Detection
Some jutsus require motion tracking:
- Rasengan → circular trajectory
- Chidori → fast forward thrust
- Sharingan → face + gesture combo

Use landmark velocity, optical flow, trajectory tracking.

---

# 📁 17. Folder Structure

naruto_jutsu/
data/
models/
effects/
sounds/
src/
main.py

---

# 18. Demo Requirement
User performs sequence → System detects → Sound + animation instantly.

---

# 19. Future Enhancements
Mobile app, AR effects, multiplayer ninja battle, more jutsus.

---

End of PRD
