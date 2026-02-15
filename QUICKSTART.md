# Quick Start: Updated Two-Hand System

## What Changed
✅ Updated to support **2 hands** instead of 1  
✅ Expanded to **12 gestures** (added Horse and Rat)  
✅ Added **reference image overlays** in data capture  
✅ Increased window size to **1280x720**  

## Next Steps

### 1. Install Updated Dependencies
```powershell
pip install -r requirements.txt
```

### 2. Add Reference Images (Recommended)
Create or download images for the 12 hand signs and place them in:
```
naruto_jutsu/images/
```

Required filenames:
- tiger.png, ram.png, snake.png, dragon.png
- boar.png, dog.png, monkey.png, rabbit.png
- ox.png, bird.png, horse.png, rat.png

See [naruto_jutsu/images/README.md](naruto_jutsu/images/README.md) for details.

**Note:** The tool works without images, they're just helpful visual references.

### 3. Collect Training Data
```powershell
cd naruto_jutsu\src
python capture_data.py
```

**Important:** 
- Show **BOTH hands** while capturing
- Collect 200+ samples per gesture
- Use SPACE to capture, N/P to navigate gestures

### 4. Train Model
```powershell
python train_model.py
```

This trains on the new 72-feature (2-hand) data.

### 5. Test Recognition
```powershell
python main.py
```

Use key `2` for gesture recognition mode.

## Key Differences from Before

| Feature | Old System | New System |
|---------|-----------|------------|
| Hands | 1 hand | 2 hands |
| Gestures | 10 | 12 |
| Features | 33 | 72 |
| Window | Default | 1280x720 |
| Reference Images | No | Yes |

## Important Notes

⚠ **Old training data is NOT compatible** - you must re-collect  
⚠ Both hands should be visible for best results  
⚠ New CSV format: `gesture_data_2hands_*.csv`  

## Documentation

- **[PHASE2_UPDATES.md](PHASE2_UPDATES.md)** - Complete technical details
- **[PHASE2_GUIDE.md](PHASE2_GUIDE.md)** - Original Phase 2 guide
- **[todo.md](todo.md)** - Project roadmap

Enjoy the enhanced two-hand recognition system! 🥷
