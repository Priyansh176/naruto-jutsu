# Phase 2 Updates: Two-Hand Recognition (12 Gestures)

## Summary of Changes

The system has been updated to support **TWO HANDS** for complete Naruto hand sign recognition with **12 gestures** (up from 10) and **reference image overlays**.

## What's New

### 1. Expanded Gesture Set (12 Signs)
Added 2 new hand signs:
- **Horse** (Uma) - Index and pinky raised, middle and ring bent
- **Rat** (Ne) - Hands together, fingers interlocked

Complete gesture list:
1. Tiger, 2. Ram, 3. Snake, 4. Dragon, 5. Boar, 6. Dog, 7. Monkey, 8. Rabbit, 9. Ox, 10. Bird, 11. Horse, 12. Rat

### 2. Two-Hand Support
- Hand tracker now detects **up to 2 hands** simultaneously
- Feature extractor extracts features from **both left and right hands**
- Feature vector expanded:
  - Single hand: 33 features
  - Two hands: **72 features** (33 left + 33 right + 6 inter-hand)
- Inter-hand features include:
  - Distance between wrists
  - Distance between index tips
  - Relative position (x, y, z difference)

### 3. Reference Image Overlays
- Data capture tool displays **reference images** for each hand sign
- Images shown in top-right corner with green border
- Helps users form correct hand positions
- Images should be placed in `naruto_jutsu/images/` folder

### 4. Larger Window Size
- Default window size increased to **1280x720** (from smaller default)
- Better visibility for hand tracking
- More space for UI elements and reference images

## Updated Files

### Core Modules
1. **[gestures.json](naruto_jutsu/gestures.json)** - Added Horse and Rat gestures with image filenames
2. **[feature_extractor.py](naruto_jutsu/src/feature_extractor.py)** - New `extract_two_hands()` method
3. **[capture_data.py](naruto_jutsu/src/capture_data.py)** - Two hands + reference images + larger window
4. **[main.py](naruto_jutsu/src/main.py)** - Updated for two-hand recognition
5. **[requirements.txt](requirements.txt)** - Enabled pandas and scikit-learn

### Documentation
6. **[images/README.md](naruto_jutsu/images/README.md)** - Guide for reference images

## Migration Guide

### For Existing Users

If you already collected data with the old system (single hand, 10 gestures):
1. Your old data is **not compatible** with the new two-hand system
2. You need to **re-collect training data** using the updated `capture_data.py`
3. Then **re-train** the model with `train_model.py`

### Setting Up Reference Images

1. Add hand sign images to `naruto_jutsu/images/` folder
2. Use these filenames (see [images/README.md](naruto_jutsu/images/README.md)):
   - tiger.png, ram.png, snake.png, dragon.png, boar.png, dog.png
   - monkey.png, rabbit.png, ox.png, bird.png, horse.png, rat.png
3. Recommended size: 300x300 pixels (PNG or JPG)

## How to Use

### Step 1: Install Dependencies
```powershell
pip install -r requirements.txt
```

### Step 2: Add Reference Images (Optional but Recommended)
Place images in `naruto_jutsu/images/` following the naming convention.

### Step 3: Collect Training Data
```powershell
cd naruto_jutsu/src
python capture_data.py
```

**Important Changes:**
- Show **BOTH hands** when capturing
- Window is larger (1280x720)
- Reference image shown in top-right corner
- Left/Right hand status displayed at bottom
- Target: 200+ samples per gesture (12 gestures = 2400+ total samples)

Controls:
- `SPACE` - Capture sample
- `N` - Next gesture
- `P` - Previous gesture
- `Q` - Quit and save

### Step 4: Train Model
```powershell
python train_model.py
```

This will:
- Load the two-hand training data (72 features per sample)
- Train Random Forest classifier
- Evaluate accuracy (target: ≥90%)
- Save model to `models/` folder

### Step 5: Run Real-Time Recognition
```powershell
python main.py
```

Controls:
- `1` - Phase 1 mode (hand tracking only)
- `2` - Phase 2 mode (gesture recognition)
- `Q` - Quit

## Technical Details

### Feature Extraction
Each sample now contains 72 features:

**Left Hand (33 features):**
- 10: Finger bend angles
- 5: Tip-to-wrist distances
- 4: Finger spread angles
- 3: Palm size measurements
- 1: Thumb-index distance
- 5: Finger orientations
- 5: Depth (z-coordinates)

**Right Hand (33 features):**
- Same as left hand

**Inter-hand (6 features):**
- Wrist-to-wrist distance
- Index-to-index distance
- Relative position (x, y, z)

### Data Format
CSV files now have:
- 72 feature columns (`feature_0` to `feature_71`)
- 1 label column (`gesture_label`)
- 1 timestamp column

New CSV files are named: `gesture_data_2hands_YYYYMMDD_HHMMSS.csv`

## Benefits of Two-Hand System

1. **More Accurate**: Many Naruto hand signs require both hands
2. **Complete Gestures**: Can recognize signs like Snake, Dragon, Rat that need both hands
3. **Better Context**: Inter-hand features capture spatial relationships
4. **Future-Ready**: Enables advanced jutsus in Phase 3 (sequences)

## Known Limitations

1. **More Data Required**: 12 gestures × 200 samples = 2400+ samples to collect
2. **Both Hands Needed**: Some gestures may work with one hand but won't be recognized optimally
3. **Reference Images**: Manual setup required (not included in repo)
4. **Backward Incompatible**: Old single-hand models won't work with new system

## Next Steps

After completing Phase 2 with the updated system:
1. Achieve ≥90% accuracy on all 12 gestures
2. Move to **Phase 3: Sequence Detection** for multi-sign jutsus
3. Implement jutsu sequences like:
   - Fireball: Snake → Ram → Tiger
   - Water Dragon: Tiger → Snake → Monkey → Ram
   - Summoning: Boar → Dog → Bird → Monkey → Ram

## Troubleshooting

### "No hands detected"
- Ensure good lighting
- Both hands visible in frame
- Hands at arm's length from camera

### "Image not found" warnings
- Add reference images to `naruto_jutsu/images/`
- Check filename matches (lowercase, .png extension)
- Tool will work without images, just won't show references

### Low accuracy after training
- Collect more samples (300+ per gesture recommended)
- Ensure both hands visible during capture
- Try different hand positions and angles
- Improve lighting conditions

## Support

For issues or questions:
1. Check [PHASE2_GUIDE.md](PHASE2_GUIDE.md) for original Phase 2 documentation
2. Review [images/README.md](naruto_jutsu/images/README.md) for image setup
3. Verify all dependencies installed: `pip install -r requirements.txt`
