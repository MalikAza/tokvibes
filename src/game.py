import math
import random
import sys
import numpy as np
import pygame

from .circle import Circle
from .ball import Ball
from .consts import BLACK, CIRCLE_NUMBERS, CIRCLE_NUMBERS_DISPLAY, FPS, HEIGHT, RED, WIDTH, HOLE_SHIFT, WHITE



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
        
    # # # #
    # MAIN #
    # # # #   
    def run(self):
        running = True
        while running:
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        self.__init__()
                        self.game_over = False
                    elif event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key == pygame.K_d:
                        self.debug_bounce = not self.debug_bounce
            
            # hanle game
            if not self.game_over:
                # Update ball position
                self.ball.move()
                
                # Update circle rotations/zoom
                for i, circle in enumerate(self.circles):
                    circle.update(i)
                
                # Check for collisions and escapes, and update score
                for circle in self.circles:
                    if circle.active:
                        if self.ball.check_collision(circle):
                            self.score += 1
                
                
                # End game if no circles are active
                if all(not circle.active for circle in self.circles):
                    self.game_over = True
            
            # Draw everything
            self.screen.fill(BLACK)
            # delete inactive circles
            self.circles = [circle for circle in self.circles if circle.active]
           
            # display only the first CIRCLE_NUMBERS_DISPLAY circles
            for i in range(min(len(self.circles), CIRCLE_NUMBERS_DISPLAY)):
                circle = self.circles[i]
                circle.draw(self.screen)

            self.ball.draw(self.screen)
            

            # Display score (optional)
            self.display_text(f"Score: {self.score}", 20, 20)
            
            if self.game_over:
                self.display_text("Game Over! Press R to restart", WIDTH//2, HEIGHT//2, center=True)
            if self.debug_bounce:  # Only show when debug is enabled
                self.draw_debug_info()
            pygame.display.flip()
            self.clock.tick(FPS)
        
        pygame.quit()
        sys.exit()
    
    def draw_debug_info(self):
        # Draw hole visualization for debugging
        for circle in self.circles:
            if circle.active:
             # Get hole start and end angles
                hole_start_angle = circle.angle + circle.hole_position
                hole_end_angle = hole_start_angle + circle.hole_size
            
                # Draw the hole path
                points_hole = []
                for angle in np.linspace(hole_start_angle, hole_end_angle, 100):
                    points_hole.append((
                        circle.x + circle.radius * math.cos(-angle),
                        circle.y + circle.radius * math.sin(-angle)
                    ))
                if len(points_hole) > 1:
                    pygame.draw.lines(self.screen, RED, False, points_hole, 5)
    
    # Draw a diagonal line for reference
    def display_text(self, text, x, y, center=False):
        font = pygame.font.SysFont(None, 36)
        text_surface = font.render(text, True, WHITE)
        if center:
            text_rect = text_surface.get_rect(center=(x, y))
        else:
            text_rect = text_surface.get_rect(topleft=(x, y))
        self.screen.blit(text_surface, text_rect)
