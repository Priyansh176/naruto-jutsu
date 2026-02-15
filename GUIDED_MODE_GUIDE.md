# Guided Jutsu Training Mode 🎯

## Overview

The new **Guided Mode** in Phase 3 provides an interactive training experience where you can:
- **Select a specific jutsu** to practice
- **See visual sequence images** with real-time progress
- **Instant gesture detection** - gestures register immediately (no hold time)
- **Visual feedback** - completed gestures are grayed out, current gesture is highlighted

---

## 🚀 How to Use

### Starting Guided Mode

```powershell
# Run Phase 3 (will auto-select first jutsu)
python naruto_jutsu/src/main.py
```

**The system will automatically:**
1. Start in Phase 3 mode
2. Select the first jutsu (Fireball)
3. Display the sequence images on screen
4. Wait for you to perform the sequence

### Selecting a Jutsu

**Press `M` key** during Phase 3 to open the jutsu menu:

```
============================================================
SELECT JUTSU TO PERFORM
============================================================
1. Fire Style: Fireball Jutsu
   Katon: Gōkakyū no Jutsu
   Sequence: Snake → Ram → Tiger
   Time: 5.0s

2. Shadow Clone Jutsu
   Kage Bunshin no Jutsu
   Sequence: Ram → Snake → Tiger
   Time: 4.0s

... (more jutsus)

0. Free Mode (detect all jutsus)
============================================================

Enter number (0-6):
```

**Type a number and press Enter:**
- `1-6` - Select specific jutsu
- `0` - Free mode (detect any jutsu)

---

## 📊 Visual Display

### Sequence Images

The screen shows all gesture images in order:

```
[Snake]  →  [Ram]  →  [Tiger]
  🟢          ⬜         ⬜
```

**Color coding:**
- 🟢 **Green border (thick)** - Current gesture to perform
- ⬜ **White border** - Upcoming gestures
- ⬛ **Grayed out (dimmed)** - Completed gestures

### Example Progress:

**Step 1:** Perform Snake
```
[Snake]  →  [Ram]  →  [Tiger]
  🟢          ⬜         ⬜
```

**Step 2:** Snake completed, now Ram
```
[Snake]  →  [Ram]  →  [Tiger]
  ⬛          🟢         ⬜
```

**Step 3:** Snake & Ram done, now Tiger
```
[Snake]  →  [Ram]  →  [Tiger]
  ⬛          ⬛         🟢
```

**Step 4:** All complete - JUTSU DETECTED!
```
╔════════════════════════════════════╗
║                                    ║
║  Fire Style: Fireball Jutsu        ║
║  Katon: Gōkakyū no Jutsu           ║
║                                    ║
╚════════════════════════════════════╝
```

---

## ⚡ Instant Detection Mode

**Key Feature:** Gestures register **immediately** when detected!

### How It Works:

**Old behavior (Phase 3 free mode):**
- Gesture must be held for 0.5 seconds
- Prevents accidental detection
- Slower to complete sequences

**New behavior (Guided mode):**
- Gesture detected **instantly** (even split-second detection)
- Moves to next step immediately
- Much faster sequence completion
- More forgiving for quick movements

### Why Instant Detection?

✅ **Faster practice** - No waiting between gestures  
✅ **More responsive** - Feels like real jutsu casting  
✅ **Easier for beginners** - Don't need to hold poses perfectly  
✅ **Natural flow** - Move smoothly through sequence

---

## 🎮 Controls

| Key | Action |
|-----|--------|
| `M` | Open jutsu selection menu |
| `3` | Phase 3 mode (sequence detection) |
| `2` | Phase 2 mode (single gesture) |
| `1` | Phase 1 mode (hand tracking only) |
| `Q` | Quit |

---

## 💡 Tips for Success

### 1. **Clear Gestures**
- Make distinct hand shapes
- Keep both hands visible
- Use good lighting

### 2. **Smooth Transitions**
- Don't rush between gestures
- But also don't hold too long
- Natural, fluid movements work best

### 3. **Follow the Highlight**
- Watch for the **green border**
- That's the current gesture to perform
- Grayed-out gestures are done

### 4. **Practice Individual Gestures First**
- Switch to Phase 2 (`2` key) to practice single gestures
- Make sure each gesture is recognized reliably
- Then return to Phase 3 (`3` key) for sequences

### 5. **Use Reference Images**
- Look at the sequence images on screen
- Match your hand position to the image
- Each gesture has a unique configuration

---

## 🔧 Troubleshooting

### "Gesture not detected"
**Problem:** Instant detection not working  
**Fix:**
- Check Phase 2 mode - is the gesture recognized there?
- Improve lighting conditions
- Make hand shapes more clearly
- Ensure both hands are visible

### "Wrong gesture detected"
**Problem:** System registers incorrect gesture  
**Fix:**
- Slow down slightly
- Make gestures more distinct
- Check that hands don't overlap
- Move hands closer to camera

### "Sequence resets unexpectedly"
**Problem:** Sequence resets before completion  
**Fix:**
- Complete within time limit (shown in menu)
- Don't perform gestures out of order
- Stay in camera view throughout sequence

### "Images not showing"
**Problem:** No sequence images on screen  
**Fix:**
- Check that images exist in `naruto_jutsu/images/` folder
- Verify jutsu is selected (press `M`)
- Make sure you're in Phase 3 mode (press `3`)

---

## 📈 Progression Path

### Level 1: Practice Single Gestures
```powershell
# Switch to Phase 2
Press '2' key
```
- Learn each hand sign individually
- Aim for >90% confidence
- Master all 12 gestures

### Level 2: Guided Jutsu Training
```powershell
# Switch to Phase 3
Press '3' key

# Select specific jutsu
Press 'M' key, choose number
```
- Follow visual sequence guide
- Use instant detection
- Build muscle memory

### Level 3: Free Mode Challenge
```powershell
# Switch to Free Mode
Press 'M' key, choose '0'
```
- No visual guide
- Detect any jutsu
- Test your mastery!

---

## 🎯 Available Jutsus in Guided Mode

| # | Jutsu | Sequence | Difficulty |
|---|-------|----------|------------|
| 1 | Fire Style: Fireball | Snake → Ram → Tiger | ⭐⭐ Medium |
| 2 | Shadow Clone | Ram → Snake → Tiger | ⭐⭐ Medium |
| 3 | Water Dragon | Tiger → Snake → Monkey → Ram | ⭐⭐⭐ Hard |
| 4 | Earth Wall | Dog → Boar → Ram | ⭐ Easy |
| 5 | Summoning | Boar → Dog → Bird → Monkey → Ram | ⭐⭐⭐⭐ Very Hard |
| 6 | Chidori | Ox → Rabbit → Monkey | ⭐⭐ Medium |

**Recommended order:** Earth Wall → Fireball → Shadow Clone → Chidori → Water Dragon → Summoning

---

## 🔄 Workflow Example

**Complete training session:**

1. **Start application**
   ```powershell
   python naruto_jutsu/src/main.py
   ```

2. **System auto-selects Fireball Jutsu**
   ```
   [AUTO-SELECTED] Fire Style: Fireball Jutsu
   Perform the sequence shown on screen.
   ```

3. **Perform sequence following visual guide**
   - Snake (green highlight) → detected ✓
   - Ram (green highlight) → detected ✓
   - Tiger (green highlight) → detected ✓

4. **JUTSU DETECTED!** 🔥

5. **Switch to different jutsu**
   - Press `M`
   - Type `4` (Earth Wall)
   - Press Enter

6. **Practice new jutsu**
   - Follow new sequence: Dog → Boar → Ram

7. **Repeat until mastered!**

---

## 📝 Technical Notes

### Instant Detection Implementation

- **No hold time** required in targeted mode
- Confidence threshold still applies (≥70%)
- Single frame detection sufficient
- Gesture transitions are immediate

### Sequence Validation

- Time window still enforced (jutsu-specific)
- Invalid gestures still reset sequence
- Order must be correct
- Duplicate gestures ignored

### Visual Rendering

- Images loaded from `naruto_jutsu/images/`
- 120x120 pixels per gesture
- Real-time border and dimming effects
- Automatic centering and layout

---

**Master the art of Naruto jutsus! 🥷✨**
