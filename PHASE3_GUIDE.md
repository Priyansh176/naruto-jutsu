# Phase 3: Sequence Detection – Implementation Guide

## 🎯 Overview

Phase 3 adds **jutsu sequence detection** to the Naruto Jutsu Recognition System. Instead of recognizing individual hand signs, the system now detects ordered sequences of gestures to recognize complete jutsus!

**Example:** Perform Snake → Ram → Tiger gestures in order to execute the **Fire Style: Fireball Jutsu**!

---

## 🔥 Implemented Features

### 1. **Jutsu Definitions** (`jutsus.json`)

Six jutsus are now supported, each with:
- **Sequence**: Ordered array of hand signs
- **Time Window**: Maximum allowed duration (3-7 seconds)
- **Effects**: Sound, animation, color, particle type
- **Names**: English and Japanese

| Jutsu | Sequence | Time Window |
|-------|----------|-------------|
| Fire Style: Fireball Jutsu | Snake → Ram → Tiger | 5.0s |
| Shadow Clone Jutsu | Ram → Snake → Tiger | 4.0s |
| Water Style: Water Dragon Jutsu | Tiger → Snake → Monkey → Ram | 6.0s |
| Earth Style: Earth Wall | Dog → Boar → Ram | 4.0s |
| Summoning Jutsu | Boar → Dog → Bird → Monkey → Ram | 7.0s |
| Chidori | Ox → Rabbit → Monkey | 4.0s |

### 2. **Sequence Detector** (`sequence_detector.py`)

Finite State Machine (FSM) implementation with:
- **Time Window Validation**: Sequences must complete within the jutsu's time limit
- **Confidence Filtering**: Only gestures with ≥70% confidence are accepted
- **Hold Time**: Each gesture must be held for 0.5s to prevent noise
- **Partial Match Detection**: Shows possible completions as you perform sequences
- **Auto-Reset**: Resets on invalid gestures or timeout

#### Key Methods:

```python
# Initialize detector
detector = SequenceDetector()

# Update with gesture prediction
result = detector.update(gesture="Snake", confidence=0.92)

# Get current progress
progress = detector.get_current_progress()
# Returns: {'active': True, 'gestures': ['Snake', 'Ram'], 'elapsed': 2.1, 'possible_jutsus': [...]}

# Reset sequence
detector.reset()
```

### 3. **Phase 3 Mode in Main App**

Enhanced UI displays:
- **Jutsu Detection**: Large overlay with jutsu name (English + Japanese) and color
- **Sequence Progress**: Shows current gesture sequence and elapsed time
- **Possible Completions**: Lists matching jutsus and next required gestures
- **Time Remaining**: Color-coded countdown for each possible jutsu

**Keyboard Controls:**
- `1`: Phase 1 (Hand tracking only)
- `2`: Phase 2 (Single gesture recognition)
- `3`: **Phase 3 (Sequence detection)** ← NEW!
- `Q`: Quit

---

## 🚀 How to Use

### Prerequisites

1. **Complete Phase 2 first:**
   ```powershell
   # Collect training data (200+ samples × 12 gestures)
   python naruto_jutsu/src/capture_data.py
   
   # Train classifier
   python naruto_jutsu/src/train_model.py
   ```

2. **Verify model exists:**
   ```powershell
   Get-ChildItem naruto_jutsu/models/*.pkl
   ```

### Running Phase 3

```powershell
# Start application (defaults to Phase 3 if model exists)
python naruto_jutsu/src/main.py

# Or explicitly specify Phase 3
python -c "from naruto_jutsu.src.main import run_hand_tracking; run_hand_tracking(start_mode='phase3')"
```

### Performing Jutsus

1. **Start with clean hands** in camera view
2. **Perform each gesture clearly**, holding for ~0.5 seconds
3. **Move to next gesture** in the sequence
4. **Complete within time window** (check UI for countdown)
5. **See jutsu detection** when sequence completes!

**Example: Fireball Jutsu**
1. Form **Snake** sign → hold for 0.5s
2. Switch to **Ram** → hold for 0.5s
3. Switch to **Tiger** → hold for 0.5s
4. 🔥 **JUTSU DETECTED!** 🔥

---

## 📊 Technical Details

### Architecture

```
Webcam → MediaPipe → Feature Extraction (72 features) →
Gesture Classifier → Sequence Detector (FSM) → Jutsu Event
```

### Sequence Detector State Machine

```
State: IDLE
  ├─ Gesture detected (high confidence) → Add to sequence
  │
State: TRACKING SEQUENCE
  ├─ Next gesture matches expected → Continue
  ├─ Sequence completes → JUTSU DETECTED! → Reset to IDLE
  ├─ Invalid gesture → Reset to IDLE (if reset_on_invalid=true)
  └─ Timeout exceeded → Reset to IDLE
```

### Configuration (`jutsus.json` settings)

```json
"settings": {
  "default_time_window": 5.0,        // Default max duration
  "gesture_hold_time": 0.5,          // Min hold time per gesture
  "confidence_threshold": 0.7,       // Min confidence to accept
  "reset_on_invalid": true           // Reset on invalid gesture
}
```

### Performance Targets

- **Sequence Detection Latency**: < 100 ms per gesture update
- **False Positive Rate**: < 5% (invalid sequences rejected)
- **Completion Rate**: ≥ 90% for correctly performed sequences
- **FPS**: ≥ 15 FPS (maintained from Phase 2)

---

## 🎨 UI Visualization

### Sequence Progress Display

When performing a sequence, the UI shows:

```
Sequence: Snake → Ram
Time: 2.3s

Possible:
  Fire Style: Fireball Jutsu: Tiger (2.7s)  ← Green (plenty of time)
  Shadow Clone Jutsu: Tiger (1.7s)          ← Orange (running out)
```

### Jutsu Detection Display

When a jutsu is completed:

```
┌────────────────────────────────────┐
│                                    │
│   Fire Style: Fireball Jutsu       │  ← Large, centered
│   Katon: Gōkakyū no Jutsu          │  ← Japanese name
│                                    │
└────────────────────────────────────┘
        (with jutsu-specific color)
```

---

## 🧪 Testing

### Test Sequence Detector Standalone

```powershell
# Run built-in test
python naruto_jutsu/src/sequence_detector.py
```

**Expected output:**
```
=== Sequence Detector Test ===

Loaded 6 jutsus from ...
  - Fire Style: Fireball Jutsu: Snake → Ram → Tiger
  - Shadow Clone Jutsu: Ram → Snake → Tiger
  ...

--- Testing Fireball Jutsu ---
Expected: Snake → Ram → Tiger

[SEQ] Added: Snake (confidence: 0.90, sequence: ['Snake'])
[SEQ] Added: Ram (confidence: 0.85, sequence: ['Snake', 'Ram'])
[SEQ] Added: Tiger (confidence: 0.92, sequence: ['Snake', 'Ram', 'Tiger'])
[JUTSU DETECTED] Fire Style: Fireball Jutsu (Katon: Gōkakyū no Jutsu)

✓ DETECTED: Fire Style: Fireball Jutsu
```

### Integration Testing

1. **Test time windows:**
   - Perform sequence slower than time_window → Should timeout
   - Perform quickly → Should detect

2. **Test invalid sequences:**
   - Dog → Bird → Tiger (invalid) → Should reset
   - Ram → Ram → Ram (duplicate) → Should not advance

3. **Test confidence filtering:**
   - Perform gestures with poor form → Should ignore low confidence

4. **Test partial sequences:**
   - Snake → Ram (incomplete) → Should show "Fire Style: Fireball Jutsu: Tiger (Xs)"

---

## 🔧 Troubleshooting

### "No jutsus loaded"
- Check `naruto_jutsu/jutsus.json` exists
- Verify JSON syntax (use a JSON validator)

### "Sequence keeps resetting"
- **Gestures not held long enough**: Hold each gesture for ≥0.5s
- **Low confidence**: Improve lighting and hand clarity
- **Time window too short**: Edit `time_window` in `jutsus.json`

### "Jutsu not detecting"
- Ensure **exact gesture order** (Snake → Ram → Tiger, not Tiger → Ram → Snake)
- Check **time window**: Complete sequence faster
- Verify **gesture classifier accuracy** in Phase 2 mode first

### "Wrong jutsu detected"
- **Overlapping sequences**: Shadow Clone and Fireball differ only in order
  - Shadow Clone: **Ram** → Snake → Tiger
  - Fireball: **Snake** → Ram → Tiger
- Ensure first gesture is correct

---

## 🚀 Next Steps (Phase 4)

Phase 3 detects sequences and emits events. Next up:

1. **Effects Engine**: Play sounds and animations when jutsus are detected
2. **Visual Effects**: Particle systems, overlays, screen flashes
3. **Audio Feedback**: Per-jutsu sound effects from `sounds/` folder
4. **Advanced Jutsus**: Motion-based detection (Rasengan, Sharingan)

---

## 📁 Files Created/Modified

- ✅ `naruto_jutsu/jutsus.json` - Jutsu definitions
- ✅ `naruto_jutsu/src/sequence_detector.py` - FSM implementation
- ✅ `naruto_jutsu/src/main.py` - Phase 3 integration
- ✅ `PHASE3_GUIDE.md` - This guide

---

## 🎓 Key Learnings

1. **FSM for sequence detection**: Clean, maintainable, extensible
2. **Time windows prevent false positives**: Users must perform sequences quickly
3. **Gesture hold time reduces noise**: Prevents accidental gesture transitions
4. **Partial match detection**: Provides real-time feedback to users
5. **Confidence thresholding**: Critical for accuracy in noisy environments

---

## 📝 PRD Alignment

✅ **Phase 3 Requirements Met:**
- [x] Implement sequence detector (FSM) ✓
- [x] Load sequences from `jutsus.json` ✓
- [x] Add time window (3-5s) for valid sequence ✓
- [x] Handle partial/cancel sequences ✓
- [x] Integrate with hand-tracking pipeline ✓
- [x] Emit "jutsu detected" event ✓
- [x] Add at least 4 jutsus (implemented 6) ✓

**Exit Criteria:** ✅ Performing a full hand-sign sequence triggers a jutsu event.

---

**Ready to perform some jutsus! 🔥⚡💧**
