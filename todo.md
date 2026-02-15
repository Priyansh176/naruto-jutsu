# Naruto Jutsu Recognition System – Phase-wise Implementation

Implementation plan aligned with [prd.md](prd.md). Each phase builds on the previous one.

---

## Phase 0: Project Setup

- [ ] Create folder structure:
  - `naruto_jutsu/`
  - `naruto_jutsu/data/` (raw samples, CSV exports)
  - `naruto_jutsu/models/` (saved classifiers)
  - `naruto_jutsu/effects/` (images, overlays, animations)
  - `naruto_jutsu/sounds/` (per-jutsu audio)
  - `naruto_jutsu/src/`
- [ ] Set up Python env (venv/conda) and `requirements.txt`:
  - opencv-python, mediapipe, numpy, pandas, scikit-learn
  - Optional: tensorflow, pygame/playsound
  - UI: tkinter (built-in) or PyQt/Streamlit
- [ ] Add `jutsus.json` with jutsu definitions (name, sequence, effects).
- [ ] Add `naruto_jutsu/src/main.py` entry point.

---

## Phase 1: Hand Tracking (Week 1)

- [x] Integrate MediaPipe Hands in a minimal script.
- [x] Capture webcam feed; detect and draw 21 hand landmarks.
- [x] Support up to 2 hands; expose landmark coordinates (x, y, z).
- [x] Extract finger states (open/closed, angles) from landmarks.
- [x] Measure FPS; target ≥ 15 FPS on laptop webcam.
- [x] Add simple UI (e.g. OpenCV window or Tkinter) showing camera + overlay.

**Exit criteria:** Stable hand tracking with landmark overlay in real time.

---

## Phase 2: Single Gesture Detection (Week 2)

- [ ] Define 10 Naruto signs: Tiger, Ram, Snake, Dragon, Boar, Dog, Monkey, Rabbit, Ox, Bird.
- [ ] Design feature set from landmarks (angles, distances, finger states).
- [ ] Build data capture tool: record landmarks per frame, save to CSV with gesture label.
- [ ] Collect ≥ 200 samples per gesture; split train/validation.
- [ ] Train classifier (e.g. Random Forest / small MLP) on landmark features.
- [ ] Save model to `models/`; load in main pipeline.
- [ ] In main app: run hand tracking → feature extraction → predict gesture; display label.
- [ ] Tune for ≥ 90% accuracy in good lighting; log latency (target < 300 ms).

**Exit criteria:** Real-time single-gesture recognition with displayed label.

---

## Phase 3: Sequence Detection (Week 3)

- [ ] Implement sequence detector (FSM or sliding window) using ordered gestures.
- [ ] Load sequences from `jutsus.json` (e.g. Fireball: Snake → Ram → Tiger).
- [ ] Add time window (e.g. 3–5 s) for valid sequence; handle partial/cancel.
- [ ] Integrate with hand-tracking pipeline: continuous gesture stream → sequence check.
- [ ] Emit “jutsu detected” event when full sequence matches.
- [ ] Add at least: Fireball, Water Dragon, Earth Wall, Summoning (per PRD table).
- [ ] Optional: Shadow Clone (Ram → Snake → Tiger), Chidori (Ox → Rabbit → Monkey).

**Exit criteria:** Performing a full hand-sign sequence triggers a jutsu event.

---

## Phase 4: Effects & UI (Week 4)

- [ ] **Effects engine:** Map each jutsu (from `jutsus.json`) to sound + visual.
- [ ] **Sound:** Per-jutsu WAV/MP3 in `sounds/`; play via pygame/playsound on trigger.
- [ ] **Visual:** Jutsu name text on screen; optional overlay/particle from `effects/`.
- [ ] Implement 2–3 signature effects (e.g. Fireball: flash + sound; Chidori: lightning + crackle).
- [ ] Rasengan (optional): detect both hands + circular motion; blue glow + charging sound.
- [ ] Sharingan (optional): face mesh + eye tracking; red eye overlay + tomoe animation.
- [ ] Polish UI: clear feedback, FPS/latency display, reset/calibrate if needed.

**Exit criteria:** Each demo jutsu triggers unique sound + animation + name.

---

## Phase 5: Testing & Demo (Week 5)

- [ ] Unit tests: feature extraction, sequence FSM, effect triggers (mocked input).
- [ ] Integration test: sample video or scripted landmark stream → full pipeline.
- [ ] Performance: confirm ≥ 15 FPS, latency < 300 ms on target hardware.
- [ ] Accuracy check: test set for gestures; document results.
- [ ] Demo script: user performs sequence → detection → sound + animation.
- [ ] README: setup, run instructions, list of supported jutsus and sequences.
- [ ] Optional: short video/screen recording for portfolio.

**Exit criteria:** Reproducible demo and basic test coverage.

---

## Phase 6: Advanced Jutsus (Post-MVP)

- [ ] **Shadow Clone:** Ram → Snake → Tiger; clone faces, smoke, echo sound.
- [ ] **Rasengan:** Both hands + circular motion; trajectory/velocity; blue ball, glow, sound.
- [ ] **Chidori:** Ox → Rabbit → Monkey; lightning overlay, crackle, screen flash.
- [ ] **Sharingan:** Face mesh + eye tracking + gesture trigger; red eye, tomoe, blur.
- [ ] Motion-based detection: landmark velocity, optical flow or trajectory module.
- [ ] Extend `jutsus.json` and effects for all advanced jutsus.

---

## Quick Reference: Jutsu Sequences (from PRD)

| Jutsu        | Sequence                          |
|-------------|------------------------------------|
| Fireball    | Snake → Ram → Tiger                |
| Shadow Clone| Ram → Snake → Tiger                |
| Water Dragon| Tiger → Snake → Monkey → Ram       |
| Earth Wall  | Dog → Boar → Ram                   |
| Summoning   | Boar → Dog → Bird → Monkey → Ram   |
| Chidori     | Ox → Rabbit → Monkey               |

---

## Notes

- Keep `jutsus.json` as single source of truth for sequences and effect references.
- Prioritize stability and FPS over number of jutsus in MVP.
- Revisit non-functional requirements (CPU usage, lighting) after Phase 5.
