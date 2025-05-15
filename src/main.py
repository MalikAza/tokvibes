import pygame
import sys
import os

from .game import Game
from .consts import WIDTH, HEIGHT, DEFAULT_CIRCLE_NUMBERS, DEFAULT_CIRCLE_NUMBERS_DISPLAY

def main():
    """Main function to start the game"""
    try:
        # Initialize pygame
        pygame.init()
        
        # Set up the display
        screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("TokVibes")
        
        # Create and run the game
        game = Game(
            screen=screen,
            circles_number=DEFAULT_CIRCLE_NUMBERS,
            circles_display=DEFAULT_CIRCLE_NUMBERS_DISPLAY
        )
        game.run()
        
    except Exception as e:
        # Show error
        print(f"Error: {e}")
        pygame.quit()
        sys.exit(1)

if __name__ == "__main__":
    # Run the game
    main()
