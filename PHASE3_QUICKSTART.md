# Phase 3 Quick Start – Jutsu Sequence Detection

## ✅ Prerequisites

Before running Phase 3, ensure you have:

1. **Trained gesture classifier** (from Phase 2):
   ```powershell
   # Check if model exists
   Get-ChildItem naruto_jutsu/models/*.pkl
   ```
   
   If no model exists, run:
   ```powershell
   # Collect training data (200+ samples × 12 gestures)
   python naruto_jutsu/src/capture_data.py
   
   # Train classifier
   python naruto_jutsu/src/train_model.py
   ```

---

## 🚀 Running Phase 3

```powershell
# Start application (auto-detects Phase 3 if model exists)
python naruto_jutsu/src/main.py
```

**Keyboard controls:**
- `1` - Phase 1: Hand tracking only
- `2` - Phase 2: Single gesture recognition
- `3` - **Phase 3: Sequence detection** ⭐
- `Q` - Quit

---

## 🔥 Available Jutsus

| Jutsu | Sequence | Time Limit |
|-------|----------|------------|
| **Fire Style: Fireball** | Snake → Ram → Tiger | 5s |
| **Shadow Clone** | Ram → Snake → Tiger | 4s |
| **Water Dragon** | Tiger → Snake → Monkey → Ram | 6s |
| **Earth Wall** | Dog → Boar → Ram | 4s |
| **Summoning** | Boar → Dog → Bird → Monkey → Ram | 7s |
| **Chidori** | Ox → Rabbit → Monkey | 4s |

---

## 🎯 How to Perform a Jutsu

### Step-by-Step Example: Fireball Jutsu

1. **Position hands** clearly in camera view
2. Form **Snake** sign with both hands
   - Hold steady for **0.5 seconds** until recognized
   - UI will show: `Sequence: Snake`
3. Switch to **Ram** sign
   - Hold for **0.5 seconds**
   - UI updates: `Sequence: Snake → Ram`
4. Switch to **Tiger** sign
   - Hold for **0.5 seconds**
   - UI updates: `Sequence: Snake → Ram → Tiger`
5. **🔥 JUTSU DETECTED!** 🔥
   - Large overlay appears with jutsu name
   - Console prints confirmation

### Tips for Success

✅ **DO:**
- Hold each gesture for at least 0.5 seconds
- Keep hands visible and well-lit
- Complete sequence within time limit (check UI countdown)
- Make clear, distinct gestures

❌ **DON'T:**
- Rush through gestures too quickly
- Let confidence drop below 70%
- Perform gestures out of order
- Take too long (sequence will timeout and reset)

---

## 📊 UI Indicators

### Sequence Progress
```
Sequence: Snake → Ram          ← Your current progress
Time: 2.3s                     ← Time elapsed

Possible:
  Fire Style: Fireball Jutsu: Tiger (2.7s)  ← Need Tiger, 2.7s left
  Shadow Clone Jutsu: Tiger (1.7s)          ← Different jutsu, 1.7s left
```

**Color coding:**
- 🟢 Green: Plenty of time (> 2s)
- 🟠 Orange: Running out (1-2s)
- 🔴 Red: Almost timeout (< 1s)

### Jutsu Detection
```
╔════════════════════════════════════╗
║                                    ║
║  Fire Style: Fireball Jutsu        ║  ← English name
║  Katon: Gōkakyū no Jutsu           ║  ← Japanese name
║                                    ║
╚════════════════════════════════════╝
```

---

## 🔧 Troubleshooting

### "Sequence keeps resetting"
**Cause:** Gestures not held long enough or low confidence

**Fix:**
- Hold each gesture for **at least 0.5 seconds**
- Improve lighting conditions
- Make gestures more clearly
- Check Phase 2 mode first to verify gesture accuracy

### "Wrong jutsu detected"
**Cause:** Overlapping sequences (e.g., Fireball vs Shadow Clone)

**Sequences:**
- Fireball: **Snake** → Ram → Tiger
- Shadow Clone: **Ram** → Snake → Tiger

**Fix:** Ensure you start with the **correct first gesture**

### "Timeout before completion"
**Cause:** Too slow

**Fix:**
- Move between gestures faster (but still hold each for 0.5s)
- Check time limit for your jutsu in the table above
- Practice the sequence to build muscle memory

### "Low detection confidence"
**Cause:** Poor camera conditions or unclear gestures

**Fix:**
- Switch to Phase 2 mode (press `2`) to test individual gesture accuracy
- If Phase 2 shows low confidence, improve:
  - Lighting (bright, even lighting)
  - Hand position (centered, both hands visible)
  - Gesture clarity (follow reference images)
- Retrain model if needed

---

## 🧪 Testing

### Test Sequence Detector Standalone
```powershell
# Run built-in test (simulates Fireball jutsu)
python naruto_jutsu/src/sequence_detector.py
```

**Expected output:**
```
=== Sequence Detector Test ===

Loaded 6 jutsus from ...
  - Fire Style: Fireball Jutsu: Snake → Ram → Tiger
  ...

[SEQ] Added: Snake (confidence: 0.90, sequence: ['Snake'])
[SEQ] Added: Ram (confidence: 0.85, sequence: ['Snake', 'Ram'])
[SEQ] Added: Tiger (confidence: 0.92, sequence: ['Snake', 'Ram', 'Tiger'])
[JUTSU DETECTED] Fire Style: Fireball Jutsu (Katon: Gōkakyū no Jutsu)

✓ DETECTED: Fire Style: Fireball Jutsu
```

---

## 📝 Configuration

### Adjust Detection Settings

Edit [jutsus.json](naruto_jutsu/jutsus.json) `settings` section:

```json
"settings": {
  "default_time_window": 5.0,        // Default max duration (seconds)
  "gesture_hold_time": 0.5,          // Min hold per gesture (seconds)
  "confidence_threshold": 0.7,       // Min confidence to accept (0-1)
  "reset_on_invalid": true           // Auto-reset on invalid gesture
}
```

**Recommendations:**
- **Easier detection:** Lower `confidence_threshold` to `0.6`, increase `gesture_hold_time` to `0.3`
- **Stricter detection:** Raise `confidence_threshold` to `0.8`, keep `gesture_hold_time` at `0.5`
- **Longer sequences:** Increase individual jutsu `time_window` values

---

## 📚 Next Steps

1. **Master all jutsus** - Practice each sequence until you can reliably trigger them
2. **Explore Phase 4** - Sound effects and visual animations (coming soon!)
3. **Compete with friends** - Who can perform jutsus fastest?
4. **Add custom jutsus** - Edit `jutsus.json` to add your own sequences!

---

## 📖 Full Documentation

For detailed technical information, see [PHASE3_GUIDE.md](PHASE3_GUIDE.md)

---

**Ready to become a jutsu master! 🥷✨**
