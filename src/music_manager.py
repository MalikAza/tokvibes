import os
import random
import pygame
import math

# Import from constants
from .consts import MIDI_VOLUME

# Try to import the song database
try:
    from .Musics.db_midi import ALL_SONG
    SONG_DB_AVAILABLE = True
except ImportError:
    SONG_DB_AVAILABLE = False
    ALL_SONG = []

# Try to import pretty_midi
try:
    import pretty_midi
    PRETTY_MIDI_AVAILABLE = True
except ImportError:
    PRETTY_MIDI_AVAILABLE = False

class MusicManager:
    _instance = None
    
    @staticmethod
    def get_instance():
        if MusicManager._instance is None:
            MusicManager._instance = MusicManager()
        return MusicManager._instance
    
    def __init__(self):
        """Initialize the music manager (singleton)"""
        if MusicManager._instance is not None:
            raise Exception("This class is a singleton! Use get_instance() instead.")
        
        # Initialize pygame mixer if needed
        if not pygame.mixer.get_init():
            pygame.mixer.init(frequency=44100)
        
        # Setup paths
        self.current_dir = os.path.dirname(os.path.abspath(__file__))
        self.sound_dir = os.path.join(self.current_dir, 'Musics')
        if not os.path.exists(self.sound_dir):
            os.makedirs(self.sound_dir)
        
        # Load basic sounds
        self.bounce_sound = self._load_sound('bounce')
        self.score_sound = self._load_sound('hmm')
        
        # MIDI handling
        self.midi_notes = []
        self.current_note_index = 0
        
        # Load MIDI if available
        if PRETTY_MIDI_AVAILABLE:
            self._load_midi()
    
    def _load_sound(self, name):
        """Load a sound file (MP3 or WAV)"""
        for ext in ['mp3', 'wav']:
            sound_path = os.path.join(self.sound_dir, f'{name}.{ext}')
            if os.path.exists(sound_path):
                try:
                    return pygame.mixer.Sound(sound_path)
                except:
                    pass
        return None
        
    def _load_midi(self):
        """Load and parse MIDI file for bounce notes"""
        # Try to load from song database first
        if SONG_DB_AVAILABLE and ALL_SONG:
            # Pick a random song from the database
            song_data = random.choice(ALL_SONG)
            midi_path = os.path.join(self.sound_dir, song_data['path'].replace('Musics/', ''))
            
            if os.path.exists(midi_path) and self._parse_midi_file(
                midi_path, 
                song_data.get('skip_first_beats', 0),
                song_data.get('volume', MIDI_VOLUME)
            ):
                return True
        
        # Fall back to default MIDI file
        midi_path = os.path.join(self.sound_dir, 'music.mid')
        if os.path.exists(midi_path):
            return self._parse_midi_file(midi_path, 0, MIDI_VOLUME)
        
        return False
    
    def _parse_midi_file(self, midi_path, skip_beats=0, volume=MIDI_VOLUME):
        """Parse a MIDI file and extract notes"""
        try:
            midi_data = pretty_midi.PrettyMIDI(midi_path)
            
            # Extract and sort notes by start time
            all_notes = []
            for instrument in midi_data.instruments:
                for note in instrument.notes:
                    all_notes.append((note.pitch, note.velocity, note.start))
            
            if not all_notes:
                return False
                
            # Sort by start time and skip beats if needed
            all_notes.sort(key=lambda x: x[2])
            if skip_beats > 0 and len(all_notes) > skip_beats:
                all_notes = all_notes[skip_beats:]
            
            # Adjust velocity based on volume setting
            self.midi_notes = [
                (pitch, int(velocity * (volume / MIDI_VOLUME))) 
                for pitch, velocity, _ in all_notes
            ]
            
            return bool(self.midi_notes)
            
        except Exception as e:
            return False
    
    def play_score_sound(self):
        """Play the scoring sound"""
        if self.score_sound:
            self.score_sound.play()
    
    def play_bounce_sound(self):
        """Play the next note in the MIDI sequence or bounce sound"""
        # If we have MIDI notes, use those for variety
        if self.midi_notes:
            # Get the next note and advance index
            pitch, velocity = self.midi_notes[self.current_note_index]
            self.current_note_index = (self.current_note_index + 1) % len(self.midi_notes)
            
            try:
                # Convert MIDI pitch to frequency
                frequency = 440.0 * (2.0 ** ((pitch - 69) / 12.0))
                volume = min(1.0, velocity / 127.0 * MIDI_VOLUME)
                
                # Generate a simple sine wave
                duration = 0.2
                sample_rate = 44100
                num_samples = int(duration * sample_rate)
                
                # Create buffer and generate sound
                buf = bytearray(num_samples * 2)
                for i in range(num_samples):
                    t = float(i) / sample_rate
                    decay = max(0, 1.0 - t / duration)
                    value = int(32767.0 * volume * decay * math.sin(2 * math.pi * frequency * t))
                    buf[i*2] = value & 0xFF
                    buf[i*2+1] = (value >> 8) & 0xFF
                
                pygame.mixer.Sound(buffer=buf).play()
                return
                
            except Exception:
                pass
        
        # Fall back to regular bounce sound
        if self.bounce_sound:
            self.bounce_sound.play()
