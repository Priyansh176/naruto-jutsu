# Sound Files for Jutsu Effects

This folder contains sound effects for each jutsu. When a jutsu is detected, the corresponding sound will play.

## Required Sound Files

The system expects the following sound files (WAV or MP3 format):

| Jutsu | Sound File | Description |
|-------|-----------|-------------|
| Fire Style: Fireball | `fireball.wav` | Whooshing flame sound |
| Shadow Clone | `shadow_clone.wav` | Poof/smoke sound |
| Water Style: Water Dragon | `water_dragon.wav` | Rushing water sound |
| Earth Style: Earth Wall | `earth_wall.wav` | Rumbling/rock sound |
| Summoning | `summoning.wav` | Mystical/portal sound |
| Chidori | `chidori.wav` | Electric crackling sound |

## Finding Sound Effects

### Free Sound Resources

1. **Freesound.org** (https://freesound.org/)
   - Search for: "fire whoosh", "water splash", "electric zap", etc.
   - Requires free account
   - CC licensed sounds

2. **Zapsplat** (https://www.zapsplat.com/)
   - Free sound effects
   - Search by category

3. **Mixkit** (https://mixkit.co/free-sound-effects/)
   - Royalty-free sounds
   - No attribution required

### Recommended Search Terms

- Fireball: "fire whoosh", "flame burst", "fireball"
- Shadow Clone: "smoke poof", "disappear", "teleport"
- Water Dragon: "water rush", "wave", "splash"
- Earth Wall: "rock slide", "rumble", "stone"
- Summoning: "magic", "portal", "mystical"
- Chidori: "electric", "lightning", "zap", "crackle"

## File Format

- **Preferred:** WAV (uncompressed, better quality)
- **Supported:** WAV, OGG, MP3
- **Recommended length:** 1-3 seconds
- **Sample rate:** 22050 Hz or 44100 Hz

## How to Add Sounds

1. Download sound files from the resources above
2. Rename them to match the expected filenames (e.g., `fireball.wav`)
3. Place them in this folder: `naruto_jutsu/sounds/`
4. The system will automatically load and play them

## Creating Your Own Sounds

### Using Audacity (Free)

1. Download Audacity: https://www.audacityteam.org/
2. Record or import sounds
3. Edit and trim to 1-3 seconds
4. Export as WAV:
   - File → Export → Export Audio
   - Format: WAV (Microsoft)
   - Sample Rate: 22050 Hz

### Tips for Better Sounds

- Keep volume consistent across all files
- Trim silence at start and end
- Normalize audio levels
- Add fade-in/fade-out for smoother playback

## Placeholder Sounds

If a sound file is missing, the system will:
- Print a warning message
- Continue without sound (visual effects still work)
- You can add the file later without code changes

## Testing Sounds

Run the effects engine test:

```powershell
python naruto_jutsu/src/effects_engine.py
```

This will test sound loading and playback.

## Volume Control

Default volume is 80%. To adjust:
- Edit `effects_engine.py`
- Modify the `volume` parameter in `play_sound()` calls
- Range: 0.0 (silent) to 1.0 (maximum)

## Troubleshooting

### "Sound file not found"
- Check filename matches exactly (case-sensitive on some systems)
- Verify file is in the correct folder
- Ensure file format is supported (WAV, OGG, MP3)

### "No sound playing"
- Check system volume
- Verify speakers/headphones connected
- Test with the effects_engine.py test script
- Check for pygame initialization errors in console

### "Sound cuts off early"
- File might be too short
- Increase `duration` in `trigger_jutsu_effects()`
- Check for buffer size issues

---

**Note:** This project uses placeholder information. You'll need to download actual sound files from free resources to hear effects.
