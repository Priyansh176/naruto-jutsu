# Phase 2: Single Gesture Detection - User Guide

## Overview
Phase 2 implements real-time single gesture recognition for 10 Naruto hand signs using machine learning.

## Supported Gestures
1. **Tiger** - Index and middle fingers extended, crossed in front
2. **Ram** - Index and middle fingers extended upward, others closed  
3. **Snake** - Hands interlocked with fingers extended
4. **Dragon** - Hands overlapped with fingers spread
5. **Boar** - All fingers extended and spread
6. **Dog** - All fingers closed except pinky and thumb
7. **Monkey** - Index and pinky extended, others closed
8. **Rabbit** - Index and middle extended upward, thumb up
9. **Ox** - Index finger pointing upward, others closed
10. **Bird** - Thumb and index forming circle, others extended

## Workflow

### Step 1: Collect Training Data
Run the data capture tool to collect gesture samples:

```powershell
cd naruto_jutsu/src
python capture_data.py
```

**Controls:**
- `SPACE` - Capture sample for current gesture
- `N` - Next gesture
- `P` - Previous gesture  
- `Q` - Quit and save

**Goal:** Collect 200+ samples per gesture for best accuracy.

**Output:** CSV file saved to `naruto_jutsu/data/gesture_data_TIMESTAMP.csv`

### Step 2: Train the Model
Train a Random Forest classifier on the collected data:

```powershell
python train_model.py
```

This will:
- Load the most recent CSV from `data/`
- Split into training (80%) and testing (20%)
- Train a Random Forest classifier  
- Evaluate accuracy (target: ≥90%)
- Save model to `models/gesture_classifier_TIMESTAMP.pkl`

**Output:**
- Trained model: `naruto_jutsu/models/gesture_classifier_TIMESTAMP.pkl`
- Training metadata: `naruto_jutsu/models/training_metadata_TIMESTAMP.json`

### Step 3: Run Real-Time Recognition
Run the main application with gesture recognition:

```powershell
python main.py
```

**Controls:**
- `1` - Switch to Phase 1 mode (hand tracking only)
- `2` - Switch to Phase 2 mode (gesture recognition)
- `Q` - Quit

**Display:**
- Recognized gesture name (large, centered)
- Confidence score (target: ≥70%)
- Latency (target: <300ms)
- FPS (target: ≥15)

## Technical Details

### Feature Extraction
Each hand landmark (21 points, 3D) is converted to a 33-feature vector:
- **10 features:** Finger bend angles (2 per finger)
- **5 features:** Finger tip distances from wrist
- **4 features:** Finger spread angles
- **3 features:** Palm size measurements
- **1 feature:** Thumb-index distance
- **5 features:** Finger orientation relative to palm
- **5 features:** Finger tip z-coordinates (depth)

### Classifier
- **Algorithm:** Random Forest (100 trees, max depth 20)
- **Input:** 33 features per frame
- **Output:** Gesture label + confidence score
- **Training:** Scikit-learn with 5-fold cross-validation

### Performance Targets
- **Accuracy:** ≥90% on test set
- **Latency:** <300ms per prediction
- **FPS:** ≥15 frames per second
- **Samples:** 200+ per gesture recommended

## File Structure
```
naruto_jutsu/
├── data/
│   └── gesture_data_*.csv          # Training data
├── models/
│   ├── gesture_classifier_*.pkl    # Trained model
│   └── training_metadata_*.json    # Training info
├── src/
│   ├── hand_tracker.py             # MediaPipe hand tracking
│   ├── feature_extractor.py        # Feature extraction from landmarks
│   ├── gesture_classifier.py       # ML model wrapper
│   ├── capture_data.py             # Data collection tool
│   ├── train_model.py              # Training script
│   └── main.py                     # Main application
└── gestures.json                   # Gesture definitions
```

## Tips for Good Accuracy

1. **Lighting:** Collect data in consistent, good lighting
2. **Distance:** Keep hand at same distance from camera (arm's length)
3. **Variety:** Vary hand position slightly during capture (rotation, tilt)
4. **Balance:** Collect equal samples for all gestures (~200 each)
5. **Clean data:** Make sure hand sign is correct before capturing

## Troubleshooting

### Model not found
```
⚠ No trained model found. Switching to Phase 1 mode.
```
**Solution:** Run `capture_data.py` to collect data, then `train_model.py` to train.

### Low accuracy (<90%)
**Solutions:**
- Collect more training samples (300+ per gesture)
- Ensure consistent hand signs during capture
- Improve lighting conditions
- Re-train with different hyperparameters

### High latency (>300ms)
**Solutions:**
- Close other applications
- Reduce tracker confidence thresholds
- Use a faster computer

### Low FPS (<15)
**Solutions:**
- Reduce camera resolution in hand tracker
- Close other applications
- Use GPU acceleration if available

## Next Steps
Once Phase 2 is complete with good accuracy:
- Proceed to Phase 3: Sequence Detection
- Implement multi-sign jutsu detection (e.g., Fireball: Snake → Ram → Tiger)
