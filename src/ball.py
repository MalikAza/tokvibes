import math
import random
import pygame
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .circle import Circle

from .consts import (BALL_RADIUS, BOUNCE_DAMPENING, HEIGHT, MIN_VELOCITY, RED, GRAVITY, WIDTH)


class Ball:
    def __init__(
        self,
        center: pygame.Vector2,
        radius=BALL_RADIUS
    ):
        self.x = center.x
        self.y = center.y
        self.radius = radius
        self.dx = random.choice([-4, 4])
        self.dy = 0 
        self.gravity = GRAVITY
    
    def move(self):
        # Apply gravity
        self.dy += self.gravity
        
        # Update position
        self.x += self.dx
        self.y += self.dy

        # Check for ball out of bounds
        if (self.x < 0 or self.x > WIDTH or 
            self.y < 0 or self.y > HEIGHT):
            self.x = WIDTH // 2
            self.y = HEIGHT // 2
            self.dx = random.choice([-4, 4])
            self.dy = 0
        return
        
    
    def check_collision(self, circle: 'Circle'):
        # Calculate distance from ball center to circle center
        dx = self.x - circle.x
        dy = self.y - circle.y
        distance = math.sqrt(dx*dx + dy*dy)
        
        next_x = self.x + self.dx
        next_y = self.y + self.dy
        next_dx = next_x - circle.x
        next_dy = next_y - circle.y
        next_distance = math.sqrt(next_dx*next_dx + next_dy*next_dy)
        
        hole_start, hole_end = circle.get_hole_point()
        if circle.active and \
              (hole_start[0] < self.x < hole_end[0] or hole_start[0] > self.x > hole_end[0]) and \
                (hole_start[1] < self.y < hole_end[1] or hole_start[1] > self.y > hole_end[1]):
            print("Ball in hole")
            circle.active = False
            self.dx = 0
            self.dy = 0
            return

        # Check both current and next position for collision
        if (abs(distance - circle.radius) < self.radius) or \
           (abs(next_distance - circle.radius) < self.radius):
            # Calculate normal vector
            nx = dx / distance
            ny = dy / distance
            
            # Calculate dot product
            dot = self.dx*nx + self.dy*ny
            
            # Update velocity with dampening
            self.dx = (self.dx - 2*dot*nx) * BOUNCE_DAMPENING
            self.dy = (self.dy - 2*dot*ny) * BOUNCE_DAMPENING
            
            # Ensure minimum velocity after bounce
            total_velocity = math.sqrt(self.dx*self.dx + self.dy*self.dy)
            if total_velocity < MIN_VELOCITY:
                scale = MIN_VELOCITY / total_velocity
                self.dx *= scale
                self.dy *= scale
          


    
    def draw(self, screen: pygame.Surface):
        pygame.draw.circle(screen, RED, (int(self.x), int(self.y)), self.radius)
