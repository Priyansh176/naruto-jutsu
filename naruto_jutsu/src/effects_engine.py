"""
Effects Engine for Naruto Jutsu Recognition System
Handles sound playback and visual effects when jutsus are detected.
"""

import cv2
import numpy as np
from pathlib import Path
from typing import Optional, Dict
import time
import threading
import sys

# Try to import sound libraries (optional)
sound_backend = None
pygame_mixer = None
playsound_lib = None

try:
    import pygame
    pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
    pygame_mixer = pygame.mixer
    sound_backend = 'pygame'
except Exception:
    try:
        from playsound import playsound  # type: ignore
        playsound_lib = playsound
        sound_backend = 'playsound'
    except Exception:
        try:
            import winsound
            sound_backend = 'winsound'
        except Exception:
            pass


class EffectsEngine:
    """
    Manages sound and visual effects for detected jutsus.
    Supports multiple sound backends (pygame, playsound, winsound).
    """
    
    def __init__(self, sounds_dir: Optional[Path] = None, effects_dir: Optional[Path] = None):
        """
        Initialize the effects engine.
        
        Args:
            sounds_dir: Path to sounds folder
            effects_dir: Path to effects folder (images, animations)
        """
        if sounds_dir is None:
            sounds_dir = Path(__file__).parent.parent / "sounds"
        if effects_dir is None:
            effects_dir = Path(__file__).parent.parent / "effects"
        
        self.sounds_dir = Path(sounds_dir)
        self.effects_dir = Path(effects_dir)
        
        # Create directories if they don't exist
        self.sounds_dir.mkdir(exist_ok=True)
        self.effects_dir.mkdir(exist_ok=True)
        
        # Sound system info
        self.sound_enabled = sound_backend is not None
        self.sound_backend = sound_backend
        
        if self.sound_enabled:
            print(f"✓ Sound system initialized ({self.sound_backend})")
        else:
            print("ℹ Sound effects disabled (visual effects still available)")
        
        # Sound cache
        self.sound_cache = {}
        
        # Active effects
        self.active_effects = []  # List of (effect_dict, start_time, duration)
        
        # Screen flash state
        self.flash_active = False
        self.flash_start = None
        self.flash_color = (255, 255, 255)
        self.flash_duration = 0.0
        
    def load_sound(self, sound_file: str) -> Optional[object]:
        """
        Load a sound file from the sounds directory.
        
        Args:
            sound_file: Filename (e.g., "fireball.wav")
            
        Returns:
            Sound object or file path depending on backend
        """
        if not self.sound_enabled:
            return None
        
        # Check cache
        if sound_file in self.sound_cache:
            return self.sound_cache[sound_file]
        
        # Try to load
        sound_path = self.sounds_dir / sound_file
        
        if sound_path.exists():
            try:
                if self.sound_backend == 'pygame' and pygame_mixer:
                    sound = pygame_mixer.Sound(str(sound_path))
                    self.sound_cache[sound_file] = sound
                    print(f"✓ Loaded sound: {sound_file}")
                    return sound
                else:
                    # For playsound or winsound, cache the path
                    self.sound_cache[sound_file] = str(sound_path)
                    print(f"✓ Loaded sound: {sound_file}")
                    return str(sound_path)
            except Exception as e:
                print(f"⚠ Failed to load {sound_file}: {e}")
                return None
        else:
            # Sound file doesn't exist - create placeholder
            print(f"ℹ Sound file not found: {sound_file} (will use silence)")
            return None
    
    def play_sound(self, sound_file: str, volume: float = 1.0):
        """
        Play a sound effect.
        
        Args:
            sound_file: Filename in sounds directory
            volume: Volume level (0.0 to 1.0)
        """
        if not self.sound_enabled:
            return
        
        sound = self.load_sound(sound_file)
        if sound is None:
            return
        
        try:
            if self.sound_backend == 'pygame' and pygame_mixer:
                sound.set_volume(volume)
                sound.play()
            elif self.sound_backend == 'playsound' and playsound_lib:
                # playsound runs in blocking mode by default
                # Run in thread to avoid blocking
                thread = threading.Thread(target=playsound_lib, args=(sound,))
                thread.daemon = True
                thread.start()
            elif self.sound_backend == 'winsound':
                import winsound
                # Note: winsound only supports WAV files
                winsound.PlaySound(sound, winsound.SND_FILENAME | winsound.SND_ASYNC)
        except Exception as e:
            print(f"⚠ Error playing sound: {e}")
    
    def play_jutsu_sound(self, jutsu: Dict):
        """
        Play the sound effect for a detected jutsu.
        
        Args:
            jutsu: Jutsu dictionary with 'effects' containing 'sound'
        """
        if 'effects' in jutsu and 'sound' in jutsu['effects']:
            sound_file = jutsu['effects']['sound']
            print(f"🔊 Playing sound: {sound_file}")
            self.play_sound(sound_file, volume=0.8)
    
    def play_gesture_sound(self, sound_file: str = "jutsu.wav", volume: float = 0.5):
        """
        Play a sound effect for gesture recognition.
        
        Args:
            sound_file: Filename (default "jutsu.wav")
            volume: Volume level (0.0 to 1.0)
        """
        print(f"🔊 Gesture recognized: {sound_file}")
        self.play_sound(sound_file, volume=volume)
    
    def trigger_screen_flash(self, color: tuple = (255, 255, 255), duration: float = 0.2):
        """
        Trigger a screen flash effect.
        
        Args:
            color: RGB color tuple
            duration: Flash duration in seconds
        """
        self.flash_active = True
        self.flash_start = time.time()
        self.flash_color = color
        self.flash_duration = duration
    
    def draw_screen_flash(self, frame: np.ndarray) -> np.ndarray:
        """
        Apply screen flash effect to frame if active.
        
        Args:
            frame: Video frame
            
        Returns:
            Frame with flash effect applied
        """
        if not self.flash_active:
            return frame
        
        # Check if flash should end
        elapsed = time.time() - self.flash_start
        if elapsed > self.flash_duration:
            self.flash_active = False
            return frame
        
        # Calculate flash intensity (fade out)
        progress = elapsed / self.flash_duration
        alpha = 1.0 - progress  # Fade from 1.0 to 0.0
        
        # Create flash overlay
        flash_overlay = np.full_like(frame, self.flash_color, dtype=np.uint8)
        
        # Blend with original frame
        result = cv2.addWeighted(frame, 1.0 - alpha * 0.5, flash_overlay, alpha * 0.5, 0)
        
        return result
    
    def draw_particle_effect(self, frame: np.ndarray, jutsu: Dict, center: tuple) -> np.ndarray:
        """
        Draw particle effects for a jutsu.
        
        Args:
            frame: Video frame
            jutsu: Jutsu dictionary with effects
            center: Center position (x, y) for particles
            
        Returns:
            Frame with particles drawn
        """
        if 'effects' not in jutsu or 'particle_type' not in jutsu['effects']:
            return frame
        
        particle_type = jutsu['effects']['particle_type']
        color = tuple(reversed(jutsu['effects'].get('color', [255, 255, 255])))  # BGR
        
        h, w = frame.shape[:2]
        cx, cy = center
        
        # Generate particles based on type
        num_particles = 30
        
        if particle_type == 'fire':
            # Fire particles: upward motion, fade to red/orange
            for _ in range(num_particles):
                offset_x = np.random.randint(-80, 80)
                offset_y = np.random.randint(-100, -20)
                size = np.random.randint(3, 10)
                
                px = cx + offset_x
                py = cy + offset_y
                
                if 0 <= px < w and 0 <= py < h:
                    # Gradient from yellow to red
                    particle_color = (0, int(165 + np.random.randint(-40, 40)), 255)
                    cv2.circle(frame, (px, py), size, particle_color, -1)
                    cv2.circle(frame, (px, py), size + 2, (0, 100, 200), 1)
        
        elif particle_type == 'water':
            # Water particles: blue droplets
            for _ in range(num_particles):
                offset_x = np.random.randint(-100, 100)
                offset_y = np.random.randint(-80, 80)
                size = np.random.randint(2, 8)
                
                px = cx + offset_x
                py = cy + offset_y
                
                if 0 <= px < w and 0 <= py < h:
                    particle_color = (255, int(100 + np.random.randint(0, 100)), 0)
                    cv2.circle(frame, (px, py), size, particle_color, -1)
        
        elif particle_type == 'lightning':
            # Lightning particles: electric arcs
            for _ in range(15):
                offset_x = np.random.randint(-120, 120)
                offset_y = np.random.randint(-120, 120)
                length = np.random.randint(10, 40)
                
                px1 = cx + offset_x
                py1 = cy + offset_y
                px2 = px1 + np.random.randint(-length, length)
                py2 = py1 + np.random.randint(-length, length)
                
                if 0 <= px1 < w and 0 <= py1 < h:
                    particle_color = (255, 255, int(100 + np.random.randint(0, 155)))
                    thickness = np.random.randint(1, 3)
                    cv2.line(frame, (px1, py1), (px2, py2), particle_color, thickness)
        
        elif particle_type == 'smoke':
            # Smoke particles: gray/white puffs
            for _ in range(num_particles):
                offset_x = np.random.randint(-100, 100)
                offset_y = np.random.randint(-100, 100)
                size = np.random.randint(10, 25)
                
                px = cx + offset_x
                py = cy + offset_y
                
                if 0 <= px < w and 0 <= py < h:
                    gray_val = np.random.randint(150, 255)
                    particle_color = (gray_val, gray_val, gray_val)
                    cv2.circle(frame, (px, py), size, particle_color, -1)
                    cv2.circle(frame, (px, py), size, (100, 100, 100), 1)
        
        elif particle_type == 'earth':
            # Earth particles: brown/gray rocks
            for _ in range(num_particles):
                offset_x = np.random.randint(-90, 90)
                offset_y = np.random.randint(-50, 50)
                size = np.random.randint(3, 12)
                
                px = cx + offset_x
                py = cy + offset_y
                
                if 0 <= px < w and 0 <= py < h:
                    particle_color = (int(40 + np.random.randint(0, 40)), 
                                     int(80 + np.random.randint(0, 40)), 
                                     int(100 + np.random.randint(0, 60)))
                    cv2.rectangle(frame, (px - size//2, py - size//2), 
                                 (px + size//2, py + size//2), particle_color, -1)
        
        return frame
    
    def trigger_jutsu_effects(self, jutsu: Dict, extended_duration: float = 3.0):
        """
        Trigger all effects for a detected jutsu.
        
        Args:
            jutsu: Jutsu dictionary with effects
            extended_duration: Duration to show particles (default 3 seconds)
        """
        # Play sound (if effects exist)
        if 'effects' in jutsu:
            self.play_jutsu_sound(jutsu)
        
        # Get effect color
        color = tuple(reversed(jutsu.get('effects', {}).get('color', [255, 255, 255])))
        
        # Trigger screen flash
        self.trigger_screen_flash(color=color, duration=0.3)
        
        # Add to active effects (for particles) - with EXTENDED duration
        self.active_effects.append({
            'jutsu': jutsu,
            'start_time': time.time(),
            'duration': extended_duration  # Use extended duration (default 3s)
        })
        
        jutsu_name = jutsu.get('name', 'Unknown Jutsu')
        print(f"✨ Triggered effects for: {jutsu_name}")
    
    def draw_active_effects(self, frame: np.ndarray, center: Optional[tuple] = None) -> np.ndarray:
        """
        Draw all active visual effects on frame.
        
        Args:
            frame: Video frame
            center: Center position for particles (default: screen center)
            
        Returns:
            Frame with effects applied
        """
        h, w = frame.shape[:2]
        if center is None:
            center = (w // 2, h // 2)
        
        # Apply screen flash
        frame = self.draw_screen_flash(frame)
        
        # Draw particles for active effects
        current_time = time.time()
        active_to_keep = []
        
        for effect in self.active_effects:
            elapsed = current_time - effect['start_time']
            if elapsed < effect['duration']:
                # Still active
                frame = self.draw_particle_effect(frame, effect['jutsu'], center)
                active_to_keep.append(effect)
        
        self.active_effects = active_to_keep
        
        return frame
    
    def cleanup(self):
        """Clean up resources."""
        if self.sound_enabled and self.sound_backend == 'pygame':
            try:
                pygame_mixer.quit()
                print("✓ Sound system cleaned up")
            except Exception:
                pass


if __name__ == "__main__":
    # Test the effects engine
    print("=== Effects Engine Test ===\n")
    
    engine = EffectsEngine()
    
    # Test jutsu
    test_jutsu = {
        'name': 'Fire Style: Fireball Jutsu',
        'japanese': 'Katon: Gōkakyū no Jutsu',
        'effects': {
            'sound': 'fireball.wav',
            'color': [255, 100, 0],
            'particle_type': 'fire'
        }
    }
    
    print("\nTriggering test jutsu effects...")
    engine.trigger_jutsu_effects(test_jutsu)
    
    # Create test frame
    test_frame = np.zeros((480, 640, 3), dtype=np.uint8)
    
    print("\nDrawing effects on test frame...")
    for i in range(30):
        frame = test_frame.copy()
        frame = engine.draw_active_effects(frame, center=(320, 240))
        
        cv2.imshow("Effects Test", frame)
        if cv2.waitKey(100) & 0xFF == ord('q'):
            break
    
    cv2.destroyAllWindows()
    engine.cleanup()
    
    print("\n✓ Effects engine test complete")
