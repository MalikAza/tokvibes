import sys
import pygame

from .circle import Circle
from .ball import Ball
from .consts import BLACK, FPS, HEIGHT, ROTATION_SPEED, WIDTH


class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("TikTok Circles")
        self.clock = pygame.time.Clock()
        
        # Create circles with holes at same angle but different rotation speeds
        base_rotation_speed = ROTATION_SPEED
        self.circles = [
            Circle(WIDTH//2, HEIGHT//2, 100, base_rotation_speed * 1.5),
            Circle(WIDTH//2, HEIGHT//2, 200, base_rotation_speed * 1.25),
            Circle(WIDTH//2, HEIGHT//2, 300, base_rotation_speed),
            Circle(WIDTH//2, HEIGHT//2, 400, base_rotation_speed * 0.75)
        ]
        
        # Create ball in the center
        self.ball = Ball(WIDTH//2, HEIGHT//2)
        
    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
            
            # Update
            self.ball.move()
            
            # Update circle rotations
            for circle in self.circles:
                circle.update()
            
            # Check for collisions and escapes
            for circle in self.circles:
                if circle.active:
                    self.ball.bounce(circle)
                    if circle.ball_escaped(self.ball):
                        # When a circle is escaped, rotate all remaining active circles
                        for other_circle in self.circles:
                            if other_circle.active and other_circle != circle:
                                other_circle.start_rotation()
            
            # Draw
            self.screen.fill(BLACK)
            for circle in self.circles:
                circle.draw(self.screen)
            self.ball.draw(self.screen)
            
            # Check win condition
            if all(not circle.active for circle in self.circles):
                running = False
            
            pygame.display.flip()
            self.clock.tick(FPS)
        
        pygame.quit()
        sys.exit()
