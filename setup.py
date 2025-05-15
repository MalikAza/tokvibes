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
        "setuptools"
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

def create_directories():
    """Create necessary directories"""
    print("\nSetting up directories...")
    
    # Create Musics directory
    src_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "src")
    music_dir = os.path.join(src_dir, "Musics")
    midi_dir = os.path.join(music_dir, "MIDI")
    
    for directory in [music_dir, midi_dir]:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"Created directory: {directory}")

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
    
    # Create necessary directories
    create_directories()
    
    print("\nSetup complete! You can now run the game.")
    print("To start the game, run: python -m src.main")
    print("\nNote: You need to place MIDI files in the src/Musics/MIDI directory")
    print("      to enable MIDI-based sound effects.")

if __name__ == "__main__":
    main()
