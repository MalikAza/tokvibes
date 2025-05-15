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
    print("Song database not available. Using default MIDI.")
    SONG_DB_AVAILABLE = False
    ALL_SONG = []

# Try to import pretty_midi, but handle case where it's not available
try:
    import pretty_midi
    PRETTY_MIDI_AVAILABLE = True
except ImportError:
    print("pretty_midi not available. Some sound features will be limited.")
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
        # Ensure this is only instantiated once
        if MusicManager._instance is not None:
            raise Exception("This class is a singleton! Use get_instance() instead.")
        
        # Initialize pygame mixer if needed
        if not pygame.mixer.get_init():
            pygame.mixer.init(frequency=44100)
        
        # Sound files paths
        self.current_dir = os.path.dirname(os.path.abspath(__file__))
        self.sound_dir = os.path.join(self.current_dir, 'Musics')
        
        # Create basic sounds if directory doesn't exist
        if not os.path.exists(self.sound_dir):
            os.makedirs(self.sound_dir)
            print(f"Created Musics directory: {self.sound_dir}")
        
        # Load the basic bounce and score sounds
        self.bounce_sound = self._load_sound('bounce')
        self.score_sound = self._load_sound('hmm')
        
        # MIDI handling
        self.midi_notes = []
        self.current_note_index = 0
        self.midi_loaded = False
        
        # Only attempt to load MIDI if pretty_midi is available
        if PRETTY_MIDI_AVAILABLE:
            self.midi_loaded = self._load_midi()
    
    def _load_sound(self, name):
        """Load a sound file (MP3 or WAV)"""
        mp3_path = os.path.join(self.sound_dir, f'{name}.mp3')
        wav_path = os.path.join(self.sound_dir, f'{name}.wav')
        
        if os.path.exists(mp3_path):
            try:
                sound = pygame.mixer.Sound(mp3_path)
                print(f"Loaded {name}.mp3")
                return sound
            except:
                pass
                
        if os.path.exists(wav_path):
            try:
                sound = pygame.mixer.Sound(wav_path)
                print(f"Loaded {name}.wav")
                return sound
            except:
                pass
        
        print(f"Warning: Could not load sound {name}")
        return None
        
    def _load_midi(self):
        """Load and parse MIDI file for bounce notes"""
        # Try to load from song database first
        if SONG_DB_AVAILABLE and ALL_SONG:
            # Pick a random song from the database
            song_data = random.choice(ALL_SONG)
            print(f"Selected song: {song_data['name']}")
            
            # Get the song path relative to the Musics directory
            midi_path = os.path.join(self.sound_dir, song_data['path'].replace('Musics/', ''))
            
            # Get skip_first_beats and volume
            skip_first_beats = song_data.get('skip_first_beats', 0)
            custom_volume = song_data.get('volume', MIDI_VOLUME)
            
            if os.path.exists(midi_path):
                print(f"Loading song from database: {midi_path}")
                try:
                    # Load the MIDI file using pretty_midi
                    midi_data = pretty_midi.PrettyMIDI(midi_path)
                    print(f"Loaded MIDI file: {midi_path}")
                    
                    # Extract notes from all instruments
                    all_notes = []
                    for instrument in midi_data.instruments:
                        for note in instrument.notes:
                            pitch = note.pitch
                            velocity = note.velocity
                            start_time = note.start
                            all_notes.append((pitch, velocity, start_time))
                    
                    # Sort notes by start time
                    all_notes.sort(key=lambda x: x[2])
                    
                    # Skip the first N beats if specified
                    if skip_first_beats > 0:
                        print(f"Skipping first {skip_first_beats} beats")
                        if len(all_notes) > skip_first_beats:
                            all_notes = all_notes[skip_first_beats:]
                        else:
                            print("Warning: skip_first_beats larger than available notes, using all notes")
                    
                    # Remove the start_time after sorting and skipping
                    self.midi_notes = [(pitch, int(velocity * (custom_volume / MIDI_VOLUME))) 
                                      for pitch, velocity, _ in all_notes]
                    
                    if not self.midi_notes:
                        print("Warning: No notes found in MIDI file")
                        return False
                    
                    # Print a sample of notes for debugging
                    sample_size = min(10, len(self.midi_notes))
                    print(f"Extracted {len(self.midi_notes)} notes from MIDI file")
                    print(f"Using custom volume: {custom_volume}")
                    return True
                    
                except Exception as e:
                    print(f"Error loading MIDI file from database: {e}")
                    # Continue to try default MIDI file
        
        # Fall back to default MIDI file
        midi_path = os.path.join(self.sound_dir, 'music.mid')
        
        if not os.path.exists(midi_path):
            print(f"Warning: MIDI file not found at {midi_path}")
            return False
            
        try:
            # Load the MIDI file using pretty_midi
            midi_data = pretty_midi.PrettyMIDI(midi_path)
            print(f"Loaded MIDI file: {midi_path}")
            
            # Extract notes from all instruments
            all_notes = []
            for instrument in midi_data.instruments:
                for note in instrument.notes:
                    pitch = note.pitch
                    velocity = note.velocity
                    start_time = note.start
                    all_notes.append((pitch, velocity, start_time))
            
            # Sort notes by start time to play in sequence (not by pitch)
            all_notes.sort(key=lambda x: x[2])
            
            # Remove the start_time after sorting
            self.midi_notes = [(pitch, velocity) for pitch, velocity, _ in all_notes]
            
            if not self.midi_notes:
                print("Warning: No notes found in MIDI file")
                return False
            
            # Print a sample of notes for debugging
            sample_size = min(10, len(self.midi_notes))
            print(f"Sample of notes: {self.midi_notes[:sample_size]}")
            print(f"Extracted {len(self.midi_notes)} notes from MIDI file")
            return True
            
        except Exception as e:
            print(f"Error loading MIDI file: {e}")
            return False
    
    def play_score_sound(self):
        """Play the scoring sound"""
        if self.score_sound:
            try:
                self.score_sound.play()
            except Exception as e:
                print(f"Error playing score sound: {e}")
    
    def play_bounce_sound(self):
        """Play the next note in the MIDI sequence or bounce sound"""
        # If we have MIDI notes, use those for variety
        if self.midi_notes:
            # Get the next note
            pitch, velocity = self.midi_notes[self.current_note_index]
            
            # Advance index (loop around if we reach the end)
            next_index = (self.current_note_index + 1) % len(self.midi_notes)
            self.current_note_index = next_index
            
            try:
                # Convert MIDI pitch to frequency (Hz)
                frequency = 440.0 * (2.0 ** ((pitch - 69) / 12.0))
                
                # Normalize velocity to volume (0.0 to 1.0)
                volume = min(1.0, velocity / 127.0 * MIDI_VOLUME)
                
                # Generate a simple sine wave at the note's frequency
                duration = 0.2  # Short duration for bounce
                sample_rate = 44100
                num_samples = int(duration * sample_rate)
                
                # Create a short sine wave with a quick decay
                buf = bytearray(num_samples * 2)  # 16-bit samples
                for i in range(num_samples):
                    t = float(i) / sample_rate
                    decay = max(0, 1.0 - t / duration)
                    value = int(32767.0 * volume * decay * math.sin(2 * 3.14159 * frequency * t))
                    # Little-endian 16-bit samples
                    buf[i*2] = value & 0xFF
                    buf[i*2+1] = (value >> 8) & 0xFF
                
                # Create a sound from the buffer
                bounce_sound = pygame.mixer.Sound(buffer=buf)
                bounce_sound.play()
                return
                
            except Exception as e:
                print(f"Error playing MIDI note: {e}")
                # Fall back to regular bounce sound
        
        # Only play bounce sound if no MIDI notes available or MIDI playback failed
        if self.bounce_sound:
            self.bounce_sound.play()
