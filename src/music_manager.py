import os
import random
import pygame
import math  # Add math module import

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
    print("pretty_midi not available. Using simple sounds instead.")
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
        else:
            self._create_default_notes()  # Still create notes for simple sound generation
    
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
        
        # If we couldn't load any sound files, create a basic sound
        print(f"Warning: Could not load sound {name}, generating a simple sound")
        return self._create_simple_sound(name == 'hmm')
        
    def _create_simple_sound(self, is_hmm=False):
        """Create a simple sound effect with pygame directly"""
        try:
            frequency = 150 if is_hmm else 800
            duration = 0.5 if is_hmm else 0.3
            sample_rate = 44100
            num_samples = int(duration * sample_rate)
            
            # Create a buffer for the sound
            buf = bytearray(num_samples * 2)  # 16-bit samples
            
            # Generate a simple sine wave
            for i in range(num_samples):
                t = float(i) / sample_rate
                if is_hmm:
                    # More complex hmm sound
                    value = int(32767.0 * 0.5 * (
                        math.sin(2 * 3.14159 * frequency * t) + 
                        0.3 * math.sin(2 * 3.14159 * frequency * 2 * t)
                    ))
                    
                    # Apply envelope
                    if t < 0.1:
                        value = int(value * (t / 0.1))
                    elif t > duration - 0.2:
                        value = int(value * ((duration - t) / 0.2))
                else:
                    # Bounce sound with decay
                    decay = max(0, 1.0 - t / duration)
                    value = int(32767.0 * 0.5 * decay * math.sin(2 * 3.14159 * frequency * t))
                    
                # Pack into buffer (little-endian 16-bit samples)
                buf[i*2] = value & 0xFF
                buf[i*2+1] = (value >> 8) & 0xFF
            
            # Create sound from buffer
            return pygame.mixer.Sound(buffer=buf)
            
        except Exception as e:
            print(f"Failed to create simple sound: {e}")
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
                        self._create_default_notes()
                        return False
                    
                    # Print a sample of notes for debugging
                    sample_size = min(10, len(self.midi_notes))
                    print(f"Sample of notes: {self.midi_notes[:sample_size]}")
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
            self._create_default_notes()
            return False
            
        try:
            # Load the MIDI file using pretty_midi
            midi_data = pretty_midi.PrettyMIDI(midi_path)
            print(f"Loaded MIDI file: {midi_path}")
            
            # Extract notes from all instruments
            for instrument in midi_data.instruments:
                for note in instrument.notes:
                    pitch = note.pitch
                    velocity = note.velocity
                    start_time = note.start
                    self.midi_notes.append((pitch, velocity, start_time))
            
            # Sort notes by start time to play in sequence (not by pitch)
            self.midi_notes.sort(key=lambda x: x[2])
            
            # Remove the start_time after sorting
            self.midi_notes = [(pitch, velocity) for pitch, velocity, _ in self.midi_notes]
            
            if not self.midi_notes:
                print("Warning: No notes found in MIDI file")
                self._create_default_notes()
                return False
            
            # Print a sample of notes for debugging
            sample_size = min(10, len(self.midi_notes))
            print(f"Sample of notes: {self.midi_notes[:sample_size]}")
            print(f"Extracted {len(self.midi_notes)} notes from MIDI file")
            return True
            
        except Exception as e:
            print(f"Error loading MIDI file: {e}")
            self._create_default_notes()
            return False
    
    def _create_default_notes(self):
        """Create default notes if MIDI file can't be loaded"""
        # Generate a simple C major scale
        base_pitches = [60, 62, 64, 65, 67, 69, 71, 72]  # C4 to C5
        
        # Create a variety of notes across octaves
        for octave in range(3, 6):  # 3 octaves
            for pitch in base_pitches:
                adjusted_pitch = pitch + (octave - 4) * 12
                velocity = random.randint(70, 100)
                self.midi_notes.append((adjusted_pitch, velocity))
        
        # Shuffle for variety
        random.shuffle(self.midi_notes)
        print(f"Created {len(self.midi_notes)} default notes")
    
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
            
            next_pitch = self.midi_notes[next_index][0] if next_index < len(self.midi_notes) else "N/A"
            
            try:
                # Convert MIDI pitch to frequency (Hz)
                frequency = 440.0 * (2.0 ** ((pitch - 69) / 12.0))
                
                # Normalize velocity to volume (0.0 to 1.0)
                volume = min(1.0, velocity / 127.0 * MIDI_VOLUME)  # Use constant from consts.py
                
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
            print("Playing default bounce sound")
            self.bounce_sound.play()


# Create sample MIDI file if needed and pretty_midi is available
def create_sample_midi():
    """Create a simple MIDI file for testing"""
    if not PRETTY_MIDI_AVAILABLE:
        print("pretty_midi not available, skipping MIDI file creation")
        return
        
    try:
        midi_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 
                                      'Musics', 'music.mid')
        
        if os.path.exists(midi_file_path):
            return  # Don't overwrite existing file
            
        # Create a PrettyMIDI object
        midi = pretty_midi.PrettyMIDI()
        
        # Create an instrument
        instrument = pretty_midi.Instrument(program=0)  # Piano
        
        # Create notes for a richer melody with variety
        notes = [60, 64, 67, 72, 67, 64, 60,  # C major arpeggio (C E G C G E C)
                 62, 65, 69, 74, 69, 65, 62,  # D minor arpeggio (D F A D A F D)
                 64, 67, 71, 76, 71, 67, 64]  # E minor arpeggio (E G B E B G E)
        note_duration = 0.25  # Quarter-second notes for more variety
        
        # Add notes to the instrument with varying velocities
        start_time = 0.0
        for pitch in notes:
            # Add some velocity variation for dynamic range
            velocity = random.randint(70, 110)
            
            note = pretty_midi.Note(
                velocity=velocity,
                pitch=pitch,
                start=start_time,
                end=start_time + note_duration
            )
            instrument.notes.append(note)
            start_time += note_duration
        
        # Add the instrument to the MIDI data
        midi.instruments.append(instrument)
        
        # Write out the MIDI file
        midi.write(midi_file_path)
        print(f"Created sample MIDI file with {len(notes)} varied notes at: {midi_file_path}")
        
    except Exception as e:
        print(f"Error creating sample MIDI file: {e}")

if __name__ == "__main__":
    # Initialize pygame
    pygame.init()
    pygame.mixer.init()
    
    # Create sample MIDI file and ensure sound directory exists
    sound_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Musics')
    if not os.path.exists(sound_dir):
        os.makedirs(sound_dir)
        print(f"Created Musics directory: {sound_dir}")
    
    create_sample_midi()
    
    # Test music manager
    manager = MusicManager.get_instance()
    print("Music manager initialized and ready")
