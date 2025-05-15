import os
import sys
import subprocess

def install_packages():
    """Install required packages using pip"""
    print("Installing required packages...")
    
    # Define packages
    required_packages = ["pygame", "numpy", "setuptools"]
    optional_packages = ["pretty_midi"]
    
    # Install required packages
    for package in required_packages:
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            print(f"✓ Installed {package}")
        except Exception as e:
            print(f"✗ Failed to install {package}: {e}")
            print(f"  Please install manually: pip install {package}")
    
    # Try to install optional packages
    for package in optional_packages:
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            print(f"✓ Installed optional package {package}")
        except Exception:
            print(f"✗ Optional package {package} not installed")
            print(f"  Some features will be limited")

def create_directories():
    """Create necessary directories"""
    print("\nSetting up directories...")
    
    # Project paths
    base_dir = os.path.dirname(os.path.abspath(__file__))
    src_dir = os.path.join(base_dir, "src")
    music_dir = os.path.join(src_dir, "Musics")
    midi_dir = os.path.join(music_dir, "MIDI")
    
    # Create directories
    for directory in [music_dir, midi_dir]:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"Created: {directory}")

def main():
    """Main setup function"""
    print("=" * 60)
    print("TokVibes Game Setup")
    print("=" * 60)
    
    # Run setup steps
    install_packages()
    create_directories()
    
    # Verify pygame installation
    try:
        import pygame
        pygame.init()
        print("\n✓ Pygame initialized successfully!")
    except:
        print("\n✗ Failed to initialize Pygame")
        print("  Game may not work correctly")
    
    # Display final instructions
    print("\n✓ Setup complete!")
    print("  To start the game:  python -m src.main")
    print("  For MIDI support:   Place MIDI files in src/Musics/MIDI/")

if __name__ == "__main__":
    main()
