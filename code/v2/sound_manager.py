import pygame
import os

class SoundManager:
    def __init__(self):
        pygame.mixer.init()
        self.sounds = {}
        self.music_playing = False
        
    def load_sound(self, name, file_path):
        """Load a sound effect and store it in the sounds dictionary"""
        try:
            sound = pygame.mixer.Sound(file_path)
            self.sounds[name] = sound
            return True
        except:
            print(f"Error loading sound: {file_path}")
            return False
            
    def play_sound(self, name, volume=0.5, loops=0):
        """Play a sound effect by name"""
        if name in self.sounds:
            self.sounds[name].set_volume(volume)
            self.sounds[name].play(loops)
            
    def play_music(self, file_path, volume=0.3, loops=-1):
        """Play background music"""
        try:
            pygame.mixer.music.load(file_path)
            pygame.mixer.music.set_volume(volume)
            pygame.mixer.music.play(loops)
            self.music_playing = True
        except:
            print(f"Error playing music: {file_path}")
            
    def stop_music(self):
        """Stop the currently playing music"""
        pygame.mixer.music.stop()
        self.music_playing = False
        
    def create_placeholder_sounds(self):
        """Create placeholder sound files for testing"""
        sounds_dir = "assets/sounds"
        os.makedirs(sounds_dir, exist_ok=True)
        
        # Create simple sound files using pygame
        self._create_beep_sound(os.path.join(sounds_dir, "jump.wav"), 440, 300)  # A4 note
        self._create_beep_sound(os.path.join(sounds_dir, "collect.wav"), 880, 200)  # A5 note
        self._create_beep_sound(os.path.join(sounds_dir, "land.wav"), 220, 150)  # A3 note
        
        return [
            os.path.join(sounds_dir, "jump.wav"),
            os.path.join(sounds_dir, "collect.wav"),
            os.path.join(sounds_dir, "land.wav")
        ]
        
    def _create_beep_sound(self, filename, frequency, duration_ms):
        """Create a simple beep sound file"""
        sample_rate = 44100
        bits = 16
        
        # Calculate samples
        num_samples = int(duration_ms * (sample_rate / 1000.0))
        buf = bytearray(num_samples * 2)  # 16-bit audio
        
        # Generate a simple sine wave
        import math
        amplitude = 32767 / 4  # 1/4 of max amplitude
        for i in range(num_samples):
            t = float(i) / sample_rate
            value = int(amplitude * math.sin(2.0 * math.pi * frequency * t))
            # Convert to 16-bit value
            buf[i*2] = value & 0xFF
            buf[i*2+1] = (value >> 8) & 0xFF
            
        # Save to file
        try:
            import wave
            with wave.open(filename, 'wb') as f:
                f.setnchannels(1)  # Mono
                f.setsampwidth(bits // 8)
                f.setframerate(sample_rate)
                f.writeframes(buf)
            return True
        except:
            print(f"Error creating sound file: {filename}")
            return False
