"""
Unit tests for EffectsEngine
Tests sound playback and visual effects system.
"""

import unittest
import sys
import numpy as np
from pathlib import Path
from unittest.mock import Mock, patch

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from effects_engine import EffectsEngine


class TestEffectsEngine(unittest.TestCase):
    """Test suite for EffectsEngine class"""
    
    def setUp(self):
        """Set up test fixtures"""
        # Create temporary sounds directory
        self.test_sounds_dir = Path(__file__).parent / "test_sounds"
        self.test_sounds_dir.mkdir(exist_ok=True)
        
        # Initialize effects engine with test directory
        self.engine = EffectsEngine(sounds_dir=self.test_sounds_dir)
        
        # Mock jutsu for testing
        self.test_jutsu = {
            "id": "test_jutsu",
            "name": "Test Jutsu",
            "japanese": "Tesuto no Jutsu",
            "effects": {
                "sound": "test.wav",
                "color": [255, 100, 0],
                "particle_type": "fire"
            }
        }
    
    def tearDown(self):
        """Clean up test fixtures"""
        # Clean up test sounds directory
        if self.test_sounds_dir.exists():
            for file in self.test_sounds_dir.iterdir():
                file.unlink()
            self.test_sounds_dir.rmdir()
    
    def test_initialization(self):
        """Test that effects engine initializes correctly"""
        self.assertIsNotNone(self.engine.sounds_dir, "Sounds directory should be set")
        self.assertIsNotNone(self.engine.effects_dir, "Effects directory should be set")
        self.assertEqual(len(self.engine.active_effects), 0, "No active effects initially")
        self.assertFalse(self.engine.flash_active, "No flash active initially")
    
    def test_sound_backend_detection(self):
        """Test that sound backend is detected"""
        # Backend should be one of: pygame, playsound, winsound, or None
        self.assertIn(self.engine.sound_backend, 
                     ['pygame', 'playsound', 'winsound', None],
                     "Sound backend should be recognized type")
    
    def test_load_missing_sound(self):
        """Test loading a sound file that doesn't exist"""
        sound = self.engine.load_sound("nonexistent.wav")
        
        # Should return None for missing file
        self.assertIsNone(sound, "Should return None for missing sound file")
    
    def test_play_sound_when_disabled(self):
        """Test playing sound when sound is disabled"""
        # Temporarily disable sound
        original_enabled = self.engine.sound_enabled
        self.engine.sound_enabled = False
        
        # Should not raise an exception
        try:
            self.engine.play_sound("test.wav")
        except Exception as e:
            self.fail(f"play_sound should not raise exception when disabled: {e}")
        finally:
            self.engine.sound_enabled = original_enabled
    
    def test_trigger_screen_flash(self):
        """Test triggering screen flash effect"""
        # Trigger flash
        self.engine.trigger_screen_flash(color=(255, 0, 0), duration=0.2)
        
        # Flash should be active
        self.assertTrue(self.engine.flash_active, "Flash should be active")
        self.assertEqual(self.engine.flash_color, (255, 0, 0), "Flash color should be set")
        self.assertEqual(self.engine.flash_duration, 0.2, "Flash duration should be set")
    
    def test_draw_screen_flash(self):
        """Test drawing screen flash on frame"""
        # Create test frame
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        
        # Trigger flash
        self.engine.trigger_screen_flash(color=(255, 255, 255), duration=0.5)
        
        # Draw flash
        result = self.engine.draw_screen_flash(frame)
        
        # Result should be modified (brighter due to flash)
        self.assertFalse(np.array_equal(frame, result), "Frame should be modified by flash")
        self.assertEqual(result.shape, frame.shape, "Frame shape should be preserved")
    
    def test_draw_particle_effect_fire(self):
        """Test drawing fire particle effect"""
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        center = (320, 240)
        
        # Draw fire particles
        result = self.engine.draw_particle_effect(frame.copy(), self.test_jutsu, center)
        
        # Result should have same shape
        # Note: Particles might not always be visible if they fall outside frame
        self.assertEqual(result.shape, frame.shape, "Frame shape should be preserved")
    
    def test_draw_particle_effect_types(self):
        """Test all particle effect types"""
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        center = (320, 240)
        
        particle_types = ['fire', 'water', 'lightning', 'smoke', 'earth']
        
        for particle_type in particle_types:
            test_jutsu = {
                "effects": {
                    "particle_type": particle_type,
                    "color": [255, 255, 255]
                }
            }
            
            # Should not raise exception
            try:
                result = self.engine.draw_particle_effect(frame.copy(), test_jutsu, center)
                self.assertEqual(result.shape, frame.shape, 
                               f"Frame shape should be preserved for {particle_type}")
            except Exception as e:
                self.fail(f"draw_particle_effect failed for {particle_type}: {e}")
    
    def test_trigger_jutsu_effects(self):
        """Test triggering complete jutsu effects"""
        # Trigger effects
        self.engine.trigger_jutsu_effects(self.test_jutsu)
        
        # Should have active effect
        self.assertEqual(len(self.engine.active_effects), 1, "Should have one active effect")
        
        # Flash should be active
        self.assertTrue(self.engine.flash_active, "Flash should be triggered")
    
    def test_draw_active_effects(self):
        """Test drawing all active effects"""
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        center = (320, 240)
        
        # Trigger effects
        self.engine.trigger_jutsu_effects(self.test_jutsu)
        
        # Draw active effects
        result = self.engine.draw_active_effects(frame, center)
        
        # Should have drawn particles and flash
        self.assertFalse(np.array_equal(frame, result), "Frame should be modified")
        self.assertEqual(result.shape, frame.shape, "Frame shape should be preserved")
    
    def test_effect_duration(self):
        """Test that effects expire after duration"""
        import time
        
        # Trigger effect with short duration
        self.engine.trigger_jutsu_effects(self.test_jutsu, extended_duration=0.1)
        
        # Should have active effect
        self.assertEqual(len(self.engine.active_effects), 1, "Should have active effect")
        
        # Wait for duration to expire
        time.sleep(0.15)
        
        # Draw effects (should clean up expired)
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        self.engine.draw_active_effects(frame)
        
        # Effect should be removed
        self.assertEqual(len(self.engine.active_effects), 0, 
                        "Expired effect should be removed")
    
    def test_play_gesture_sound(self):
        """Test playing gesture recognition sound"""
        # Should not raise exception even if sound missing
        try:
            self.engine.play_gesture_sound("jutsu.wav", volume=0.5)
        except Exception as e:
            self.fail(f"play_gesture_sound should not raise exception: {e}")
    
    def test_multiple_active_effects(self):
        """Test handling multiple active effects simultaneously"""
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        
        # Trigger multiple effects
        self.engine.trigger_jutsu_effects(self.test_jutsu, extended_duration=1.0)
        
        # Create another jutsu
        jutsu2 = {
            "effects": {
                "sound": "test2.wav",
                "color": [0, 255, 0],
                "particle_type": "water"
            }
        }
        self.engine.trigger_jutsu_effects(jutsu2, extended_duration=1.0)
        
        # Should have two active effects
        self.assertEqual(len(self.engine.active_effects), 2, 
                        "Should have multiple active effects")
        
        # Should draw both without error
        try:
            result = self.engine.draw_active_effects(frame)
            self.assertEqual(result.shape, frame.shape, "Frame shape should be preserved")
        except Exception as e:
            self.fail(f"Multiple effects should not raise exception: {e}")


class TestEffectsEdgeCases(unittest.TestCase):
    """Test edge cases and error handling"""
    
    def setUp(self):
        self.engine = EffectsEngine()
    
    def test_missing_effects_in_jutsu(self):
        """Test handling jutsu with missing effects"""
        incomplete_jutsu = {
            "name": "Incomplete Jutsu"
            # No 'effects' key
        }
        
        # Should not raise exception
        try:
            self.engine.trigger_jutsu_effects(incomplete_jutsu)
        except Exception as e:
            self.fail(f"Should handle missing effects gracefully: {e}")
    
    def test_invalid_particle_type(self):
        """Test handling invalid particle type"""
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        jutsu = {
            "effects": {
                "particle_type": "invalid_type",
                "color": [255, 255, 255]
            }
        }
        
        # Should not raise exception (just won't draw particles)
        try:
            result = self.engine.draw_particle_effect(frame, jutsu, (320, 240))
            # Should return original frame unchanged for invalid type
            self.assertEqual(result.shape, frame.shape, "Frame shape should be preserved")
        except Exception as e:
            self.fail(f"Should handle invalid particle type gracefully: {e}")
    
    def test_out_of_bounds_center(self):
        """Test particle effect with center outside frame"""
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        jutsu = {
            "effects": {
                "particle_type": "fire",
                "color": [255, 100, 0]
            }
        }
        
        # Center way outside frame
        center = (1000, 1000)
        
        # Should not raise exception
        try:
            result = self.engine.draw_particle_effect(frame, jutsu, center)
            self.assertEqual(result.shape, frame.shape, "Frame shape should be preserved")
        except Exception as e:
            self.fail(f"Should handle out-of-bounds center gracefully: {e}")


if __name__ == '__main__':
    unittest.main()
