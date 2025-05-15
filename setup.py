import os
import sys
import subprocess
import platform

def install_packages():
    """Install required packages using pip"""
    print("Installing required packages...")
    
    # Basic required packages
    required_packages = [
        "pygame",
        "numpy",
        "setuptools"  # Add setuptools to required packages
    ]
    
    # Optional packages (will be skipped if installation fails)
    optional_packages = [
        "pretty_midi"
    ]
    
    # Install required packages
    for package in required_packages:
        print(f"Installing {package}...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            print(f"Successfully installed {package}")
        except Exception as e:
            print(f"Failed to install {package}: {e}")
            print(f"Please install {package} manually with: pip install {package}")
    
    # Try to install optional packages
    for package in optional_packages:
        print(f"Installing optional package {package}...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            print(f"Successfully installed {package}")
        except Exception as e:
            print(f"Note: Optional package {package} could not be installed.")
            print(f"Game will still work, but with reduced functionality.")

def create_sound_files():
    """Create sound files needed for the game"""
    print("\nCreating sound files...")
    
    # Create Musics directory if it doesn't exist
    src_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "src")
    music_dir = os.path.join(src_dir, "Musics")
    
    if not os.path.exists(music_dir):
        os.makedirs(music_dir)
        print(f"Created directory: {music_dir}")
    
    # Create simple WAV files for bounce and hmm sounds
    bounce_path = os.path.join(music_dir, "bounce.wav")
    hmm_path = os.path.join(music_dir, "hmm.wav")
    
    # Only create files if they don't exist
    if not os.path.exists(bounce_path) and not os.path.exists(bounce_path.replace('.wav', '.mp3')):
        create_simple_wav_file(bounce_path, frequency=800, duration=0.3, is_hmm=False)
    
    if not os.path.exists(hmm_path) and not os.path.exists(hmm_path.replace('.wav', '.mp3')):
        create_simple_wav_file(hmm_path, frequency=150, duration=0.5, is_hmm=True)
    
    print("Sound files created successfully!")

def create_simple_wav_file(filepath, frequency=440, duration=0.5, is_hmm=False):
    """Create a simple WAV file without external dependencies"""
    try:
        import wave
        import struct
        import math
        
        # WAV parameters
        sample_rate = 44100
        num_samples = int(sample_rate * duration)
        
        # Create wave file
        with wave.open(filepath, 'w') as wav_file:
            wav_file.setparams((1, 2, sample_rate, 0, 'NONE', 'not compressed'))
            
            # Generate samples
            samples = []
            for i in range(num_samples):
                t = float(i) / sample_rate
                
                if is_hmm:
                    # Create a more complex hmm sound with harmonics
                    value = int(32767 * 0.5 * (
                        math.sin(2 * math.pi * frequency * t) + 
                        0.3 * math.sin(2 * math.pi * frequency * 2 * t)
                    ))
                    
                    # Apply envelope for hmm sound
                    if t < 0.1:
                        value = int(value * (t / 0.1))
                    elif t > duration - 0.2:
                        value = int(value * ((duration - t) / 0.2))
                else:
                    # Create bounce sound with quick decay
                    decay = math.exp(-10 * t)
                    value = int(32767 * 0.5 * math.sin(2 * math.pi * frequency * t) * decay)
                
                # Pack value as signed short
                packed_value = struct.pack('h', value)
                samples.append(packed_value)
            
            # Write samples to file
            wav_file.writeframes(b''.join(samples))
        
        print(f"Created {filepath}")
        
    except Exception as e:
        print(f"Failed to create {filepath}: {e}")
        print("You'll need to provide your own sound files.")

def main():
    """Main setup function"""
    print("=" * 60)
    print("TokVibes Game Setup")
    print("=" * 60)
    
    # Install required packages
    install_packages()
    
    # Try to import pygame after installation
    try:
        import pygame
        pygame.init()
        print("\nPygame initialized successfully!")
    except:
        print("\nWarning: Failed to initialize Pygame.")
        print("The game may not work correctly.")
    
    # Create sound files
    create_sound_files()
    
    print("\nSetup complete! You can now run the game.")
    print("To start the game, run: python -m src.main")

if __name__ == "__main__":
    main()
