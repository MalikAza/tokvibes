import math
import random
import pygame
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .circle import Circle

from .consts import BOUNCE_DAMPENING, GRAVITY, RED, MIN_VELOCITY


class Ball:
    def __init__(
        self,
        x: int,
        y: int,
        radius=10
    ):
        self.x = x
        self.y = y
        self.radius = radius
        self.dx = random.choice([-4, 4])
        self.dy = 0  # Start with no vertical velocity
        self.gravity = GRAVITY
    
    def move(self):
        # Apply gravity
        self.dy += self.gravity
        
        # Update position
        self.x += self.dx
        self.y += self.dy
    
    def bounce(self, circle: 'Circle'):
        # Calculate distance from ball center to circle center
        dx = self.x - circle.x
        dy = self.y - circle.y
        distance = math.sqrt(dx*dx + dy*dy)
        
        # Improved collision detection with predictive position check
        next_x = self.x + self.dx
        next_y = self.y + self.dy
        next_dx = next_x - circle.x
        next_dy = next_y - circle.y
        next_distance = math.sqrt(next_dx*next_dx + next_dy*next_dy)
        
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
