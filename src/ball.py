import math
import random
import pygame
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .circle import Circle

from .consts import BOUNCE_DAMPENING, GRAVITY, RED


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
    
    def bounce(self, circle: 'Circle'):  # Using string literal type hint
        # Calculate distance from ball center to circle center
        dx = self.x - circle.x
        dy = self.y - circle.y
        distance = math.sqrt(dx*dx + dy*dy)
        
        # Check for collision with circle border
        if abs(distance - circle.radius) < self.radius:
            # Calculate normal vector
            nx = dx / distance
            ny = dy / distance
            
            # Calculate dot product
            dot = self.dx*nx + self.dy*ny
            
            # Update velocity with dampening
            self.dx = (self.dx - 2*dot*nx) * BOUNCE_DAMPENING
            self.dy = (self.dy - 2*dot*ny) * BOUNCE_DAMPENING
    
    def draw(self, screen: pygame.Surface):
        pygame.draw.circle(screen, RED, (int(self.x), int(self.y)), self.radius)
