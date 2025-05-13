import math
import numpy as np
import pygame
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .ball import Ball
from .consts import WHITE


class Circle:
    def __init__(
        self,
        x: int,
        y: int,
        radius: int,
        rotation_speed: float
    ):
        self.x = x
        self.y = y
        self.radius = radius
        self.angle = 0  # All circles start with hole at same position
        self.hole_size = math.pi/6  # 30 degrees hole
        self.active = True
        self.rotation_speed = rotation_speed
        self.rotating = True  # Start rotating by default
        self.target_angle = 2 * math.pi  # Full rotation
    
    def update(self):
        # Always rotate when active
        if self.active:
            self.angle = (self.angle + self.rotation_speed) % (2 * math.pi)

    def draw(self, screen: pygame.Surface):
        if not self.active:
            return
            
        # Draw circle with a hole
        start_angle = self.angle - self.hole_size/2
        end_angle = self.angle + self.hole_size/2
        
        # Convert angles to start and end points
        points = []
        # Draw the main part of the circle (everything except the hole)
        for angle in np.linspace(end_angle, start_angle + 2*math.pi, 100):
            points.append((
                self.x + self.radius * math.cos(-angle),
                self.y + self.radius * math.sin(-angle)
            ))
        
        if len(points) > 1:
            pygame.draw.lines(screen, WHITE, False, points, 2)

    def ball_escaped(self, ball: 'Ball'):
        if not self.active:
            return False
            
        # Calculate distance from ball to circle center
        dx = ball.x - self.x
        dy = ball.y - self.y
        distance = math.sqrt(dx*dx + dy*dy)
        
        # Calculate angle of ball relative to circle center
        angle = math.atan2(dy, dx)
        if angle < 0:
            angle += 2*math.pi
            
        # Check if ball is near the circle's radius and within the hole
        hole_start = self.angle - self.hole_size/2
        hole_end = self.angle + self.hole_size/2
        
        # Only trigger when the ball is moving outward through the hole
        if self.radius - ball.radius <= distance <= self.radius + ball.radius:
            if (hole_start <= angle <= hole_end) or \
               (hole_start <= angle + 2*math.pi <= hole_end + 2*math.pi):
                # Calculate if ball is moving outward
                velocity_angle = math.atan2(ball.dy, ball.dx)
                if velocity_angle < 0:
                    velocity_angle += 2*math.pi
                    
                # Check if ball's movement direction roughly matches the hole direction
                angle_diff = abs(angle - velocity_angle)
                if angle_diff <= math.pi/2:  # Ball is moving outward
                    self.active = False
                    # Trigger rotation of remaining active circles
                    self.start_rotation()
                    return True
        return False
    
    def start_rotation(self):
        self.rotating = True
        # When triggered by ball escape, rotate 180 degrees from current position
        self.target_angle = (self.angle + math.pi) % (2 * math.pi)
