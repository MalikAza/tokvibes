import os
import numpy as np
import pygame
from scipy.io import wavfile
import wave
import struct

def generate_sound(filename, frequency, duration, volume=0.5, is_hmm=False):
    """Generate a simple sound file"""
    # Set parameters
    sample_rate = 44100  # CD quality
    num_samples = int(duration * sample_rate)
    
    # Generate time array
    t = np.linspace(0, duration, num_samples, False)
    
    if is_hmm:
        # Generate a more voice-like "hmm" sound with harmonics
        # Base tone plus harmonics
        note = np.sin(2 * np.pi * frequency * t) * volume
        # Add some harmonics for richness
        note += np.sin(2 * np.pi * frequency * 2 * t) * volume * 0.3
        note += np.sin(2 * np.pi * frequency * 3 * t) * volume * 0.2
        # Add an envelope to shape the sound (rise and fall)
        envelope = np.ones(num_samples)
        attack = int(0.05 * sample_rate)  # 50ms attack
        decay = int(0.1 * sample_rate)    # 100ms decay
        release = int(0.3 * sample_rate)  # 300ms release
        # Apply envelope
        envelope[:attack] = np.linspace(0, 1, attack)
        envelope[-release:] = np.linspace(1, 0, release)
        note = note * envelope
    else:
        # Generate a simple bounce sound (short ping)
        note = np.sin(2 * np.pi * frequency * t) * volume
        # Add fast decay for bounce effect
        decay = np.exp(-5 * t)
        note = note * decay
    
    # Normalize to 16-bit range
    audio = note * 32767 / np.max(np.abs(note))
    audio = audio.astype(np.int16)
    
    # Write to file
    wavfile.write(filename, sample_rate, audio)
    print(f"Created sound file: {filename}")
    
    # Convert WAV to MP3 if possible (requires ffmpeg)
    mp3_filename = filename.replace('.wav', '.mp3')
    try:
        import subprocess
        subprocess.call(['ffmpeg', '-i', filename, '-y', mp3_filename])
        print(f"Converted to MP3: {mp3_filename}")
        os.remove(filename)  # Remove the WAV file
        return mp3_filename
    except:
        print(f"Couldn't convert to MP3. WAV file saved as: {filename}")
        return filename

def create_simple_wav(filename, is_hmm=False):
    """Create a simple WAV file using wave module (no external dependencies)"""
    sample_rate = 44100
    duration = 0.3 if not is_hmm else 0.5
    frequency = 800 if not is_hmm else 120
    
    # Create a new wave file
    wav_file = wave.open(filename, 'w')
    wav_file.setparams((1, 2, sample_rate, 0, 'NONE', 'not compressed'))
    
    # Calculate samples
    num_samples = int(sample_rate * duration)
    
    # Generate wave data
    values = []
    for i in range(num_samples):
        t = float(i) / sample_rate  # Time in seconds
        
        if is_hmm:
            # More complex "hmm" sound
            angle = 2 * np.pi * t
            value = int(32767 * 0.5 * (
                np.sin(frequency * angle) + 
                0.3 * np.sin(2 * frequency * angle) + 
                0.1 * np.sin(3 * frequency * angle)
            ))
            
            # Apply envelope
            if t < 0.1:  # Attack
                value = int(value * (t / 0.1))
            elif t > duration - 0.2:  # Release
                value = int(value * ((duration - t) / 0.2))
        else:
            # Simple bounce sound with decay
            angle = 2 * np.pi * frequency * t
            decay = np.exp(-10 * t)
            value = int(32767 * 0.5 * np.sin(angle) * decay)
        
        # Pack value as short int
        packed_value = struct.pack('h', value)
        values.append(packed_value)
    
    # Join values and write to file
    value_str = b''.join(values)
    wav_file.writeframes(value_str)
    wav_file.close()
    
    print(f"Created sound file: {filename}")
    return filename

def ensure_sounds_exist():
    """Ensure the sound files exist, creating them if needed"""
    # Get the directory of this script
    current_dir = os.path.dirname(os.path.abspath(__file__))
    sound_dir = os.path.join(current_dir, 'Musics')
    
    # Create the directory if it doesn't exist
    if not os.path.exists(sound_dir):
        os.makedirs(sound_dir)
        print(f"Created Musics directory at: {sound_dir}")
    
    # Define paths for sound files
    bounce_path = os.path.join(sound_dir, 'bounce.wav')
    hmm_path = os.path.join(sound_dir, 'hmm.wav')
    
    # Check if files exist, create them if not
    if not os.path.exists(bounce_path.replace('.wav', '.mp3')):
        try:
            if 'scipy' in globals():
                generate_sound(bounce_path, 800, 0.3, 0.7, False)
            else:
                create_simple_wav(bounce_path, False)
        except Exception as e:
            print(f"Error creating bounce sound: {e}")
    
    if not os.path.exists(hmm_path.replace('.wav', '.mp3')):
        try:
            if 'scipy' in globals():
                generate_sound(hmm_path, 150, 0.6, 0.8, True)
            else:
                create_simple_wav(hmm_path, True)
        except Exception as e:
            print(f"Error creating hmm sound: {e}")
    
    print("\nSound files are ready to use!")
    print("You can replace these with better quality sounds if desired.")
    print("Just place your sound files in the Musics directory with the same names.")

if __name__ == "__main__":
    try:
        # Initialize pygame for sound capability testing
        pygame.init()
        pygame.mixer.init()
        print("Sound system initialized for testing.")
    except:
        print("Warning: Could not initialize sound system.")
    
    # Ensure sound files exist
    ensure_sounds_exist()
