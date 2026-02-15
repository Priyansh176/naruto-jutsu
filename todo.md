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

## Phase 2: Single Gesture Detection (Week 2) ✅ UPDATED FOR TWO HANDS

- [x] Define 12 Naruto signs: Tiger, Ram, Snake, Dragon, Boar, Dog, Monkey, Rabbit, Ox, Bird, Horse, Rat.
- [x] Design feature set from landmarks (angles, distances, finger states) - **72 features for 2 hands**
- [x] Build data capture tool: record landmarks per frame, save to CSV with gesture label - **with reference images**
- [x] Collect ≥ 200 samples per gesture; split train/validation - **12 gestures × 200 = 2400+ samples**
- [x] Train classifier (e.g. Random Forest / small MLP) on landmark features.
- [x] Save model to `models/`; load in main pipeline.
- [x] In main app: run hand tracking → feature extraction → predict gesture; display label.
- [x] Tune for ≥ 90% accuracy in good lighting; log latency (target < 300 ms).
- [x] **NEW: Two-hand support with 72-feature extraction**
- [x] **NEW: Reference image overlays in capture tool**
- [x] **NEW: Larger window size (1280x720)**

**Exit criteria:** Real-time two-hand gesture recognition with displayed label for 12 signs.

**See:** [PHASE2_UPDATES.md](PHASE2_UPDATES.md) for complete details on two-hand system.

---

## Phase 3: Sequence Detection (Week 3) ✅ COMPLETED

- [x] Implement sequence detector (FSM or sliding window) using ordered gestures.
- [x] Load sequences from `jutsus.json` (e.g. Fireball: Snake → Ram → Tiger).
- [x] Add time window (e.g. 3–5 s) for valid sequence; handle partial/cancel.
- [x] Integrate with hand-tracking pipeline: continuous gesture stream → sequence check.
- [x] Emit "jutsu detected" event when full sequence matches.
- [x] Add at least: Fireball, Water Dragon, Earth Wall, Summoning (per PRD table).
- [x] Optional: Shadow Clone (Ram → Snake → Tiger), Chidori (Ox → Rabbit → Monkey).

**Exit criteria:** ✅ Performing a full hand-sign sequence triggers a jutsu event.

**See:** [PHASE3_GUIDE.md](PHASE3_GUIDE.md) for complete Phase 3 documentation.

---

## Phase 4: Effects & UI (Week 4) ✅ COMPLETED

- [x] **Effects engine:** Map each jutsu (from `jutsus.json`) to sound + visual.
- [x] **Sound:** Per-jutsu WAV/MP3 in `sounds/`; play via multi-backend sound system.
- [x] **Visual:** Jutsu name text on screen; overlay/particle effects from `effects/`.
- [x] Implement 2–3 signature effects (fire, water, lightning, earth, smoke).
- [x] Screen flash effect on jutsu detection
- [x] Particle system for visual effects
- [x] Multi-backend sound support (pygame, playsound, winsound)

**Exit criteria:** ✅ Each jutsu triggers unique effects (visual + optional sound).

**See:** [PHASE4_GUIDE.md](PHASE4_GUIDE.md) for complete Phase 4 documentation.

---

## Phase 5: Testing & Demo (Week 5) ✅ COMPLETED

- [x] Unit tests: feature extraction, sequence FSM, effect triggers (mocked input).
- [x] Integration test: sample video or scripted landmark stream → full pipeline.
- [x] Performance: confirm ≥ 15 FPS, latency < 300 ms on target hardware.
- [x] Accuracy check: test set for gestures; document results.
- [x] Demo script: user performs sequence → detection → sound + animation.
- [x] README: setup, run instructions, list of supported jutsus and sequences.
- [x] Optional: short video/screen recording for portfolio.

**Exit criteria:** ✅ Reproducible demo and comprehensive test coverage.

**See:** [PHASE5_GUIDE.md](PHASE5_GUIDE.md) for complete Phase 5 documentation.

**Test Suite:**
- Unit tests: `python naruto_jutsu/tests/run_tests.py`
- Performance tests: `python naruto_jutsu/tests/performance_test.py`
- All tests passing with >90% accuracy and 25+ FPS

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
