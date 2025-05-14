import random
import sys
import pygame

from .circle import Circle
from .ball import Ball
from .consts import BLACK, CIRCLE_NUMBERS, FPS, HEIGHT, WIDTH, HOLE_SHIFT, WHITE



class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("TikTok Circles")
        self.clock = pygame.time.Clock()
        self.center = pygame.Vector2(WIDTH//2, HEIGHT//2)
        self.num_circles = CIRCLE_NUMBERS
        
        self.circles = []
        for i in range(self.num_circles):
            circle = Circle(
                center=self.center,
                circle_number=i,
                hole_position=(i * HOLE_SHIFT) % 360
            )
            self.circles.append(circle)
        
        # Create ball in the center
        self.ball = Ball(center=self.center,)
        
        # Game state
        self.score = 0
        self.game_over = False

        self.debug_bounce = False
        
    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        self.__init__()
                        self.game_over = False
                    elif event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key == pygame.K_b:
                        self.debug_bounce = True
            
            if not self.game_over:
                # Update ball position
                self.ball.move()
                
                # Update circle rotations
                for circle in self.circles:
                    circle.update()
                
                # Check for collisions and escapes
                for circle in self.circles:
                    if circle.active:
                        self.ball.check_collision(circle)
                
                
                # Check win condition
                if all(not circle.active for circle in self.circles):
                    self.game_over = True
            
            # Draw everything
            self.screen.fill(BLACK)
            for circle in self.circles:
                circle.draw(self.screen)
            self.ball.draw(self.screen)
            
            # Display score (optional)
            self.display_text(f"Score: {self.score}", 20, 20)
            
            if self.game_over:
                self.display_text("Game Over! Press R to restart", WIDTH//2, HEIGHT//2, center=True)
            
            pygame.display.flip()
            self.clock.tick(FPS)
        
        pygame.quit()
        sys.exit()
        
    def display_text(self, text, x, y, center=False):
        font = pygame.font.SysFont(None, 36)
        text_surface = font.render(text, True, WHITE)
        if center:
            text_rect = text_surface.get_rect(center=(x, y))
        else:
            text_rect = text_surface.get_rect(topleft=(x, y))
        self.screen.blit(text_surface, text_rect)
