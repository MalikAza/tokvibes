import math
import os
import random
import numpy as np
import pygame
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .circle import Circle

from .consts import (BALL_RADIUS, BALL_TRAIL_LENGTH, BOUNCE_DAMPENING, HEIGHT, MIN_VELOCITY, RED, GRAVITY, WIDTH)


class Ball:
    def __init__(
        self,
        center: pygame.Vector2,
        color=RED,
        radius=BALL_RADIUS,
        score_position=(0, 0),
        text = "yes",
    ):
        self.x = center.x
        self.y = center.y
        self.radius = radius
        self.dx = random.uniform(-5, 5) 
        while abs(self.dx) < 2:
            self.dx = random.uniform(-5, 5)
        self.dy = 0 
        self.gravity = GRAVITY
        self.color = color
        self.score = 0
        self.score_position = score_position
        self.text = text
        self.old_pos = []
    
    def move(self):
        # Apply gravity
        self.dy += self.gravity
        
        # Update position
        self.x += self.dx
        self.y += self.dy
        # Update old position
        self.old_pos.append((self.x, self.y))
        if len(self.old_pos) > BALL_TRAIL_LENGTH:
            self.old_pos.pop(0)

        # Check for ball out of bounds
        if (self.x < 0 or self.x > WIDTH or 
            self.y < 0 or self.y > HEIGHT):
            self.x = WIDTH // 2
            self.y = HEIGHT // 2
            self.dx = random.choice([-4, 4])
            self.dy = 0
            self.old_pos = []
        return
        
    def play_bounce_sound(self):
        #TODO: Implement sound playing
        # Placeholder for sound playing
        current_dir = os.path.dirname(os.path.abspath(__file__)) 
        music_dir = os.path.join(current_dir, 'Musics/bounce.mp3')
        pygame.mixer.Sound(music_dir).play(0)

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
    
        # Check if ball is in the hole
        hole_start_angle = circle.angle + circle.hole_position
        hole_end_angle = hole_start_angle + circle.hole_size
    
        # Check both current and next position for collision
        if (abs(distance - circle.radius) < self.radius) or \
            (abs(next_distance - circle.radius) < self.radius):
        
            # Check if ball is in the hole
            ball_angle = math.atan2(-(self.y - circle.y), (self.x - circle.x))
            
            # Normalize angles to the range [0, 2*pi]
            ball_angle %= 2 * math.pi
            hole_start_angle %= 2 * math.pi
            hole_end_angle %= 2 * math.pi
        
            if hole_start_angle <= hole_end_angle:
                in_hole = hole_start_angle <= ball_angle <= hole_end_angle
            else:  # Handle case where hole crosses the 0 angle
                in_hole = ball_angle >= hole_start_angle or ball_angle <= hole_end_angle
            
            if in_hole:
                circle.desactivate()
                self.score += 1
                return
            
            ### Bounce ###
            self.play_bounce_sound()
            # Normal collision handling
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

        # Add a trail behind the ball
        if len(self.old_pos) > 1:
            trail_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)  # Create a transparent surface
            for i in range(len(self.old_pos) - 1):
                size = int(self.radius - (self.radius / len(self.old_pos)) * (len(self.old_pos) - i - 1))
                # fade in
                alpha = int(255 * (i / len(self.old_pos)))
                color = (*self.color[:3], alpha)  # Add alpha to the color
                # position must be calculated at the surface of the ball (depending of the radius and the direction)
                pygame.draw.circle(trail_surface, color, self.old_pos[i], size)
            screen.blit(trail_surface, (0, 0))

            
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)
        # Draw inner circle in black
        pygame.draw.circle(screen, (0, 0, 0), (int(self.x), int(self.y)), self.radius - 2)
        # Write self.text in it
        font = pygame.font.Font(None, 15)
        text = font.render(self.text, True, (255, 255, 255))
        text_rect = text.get_rect(center=(self.x, self.y))
        screen.blit(text, text_rect)

        

        # Draw score with pill background at score_position
        if self.score_position != (0, 0):
            # Create smaller font for the text
            font = pygame.font.Font(None, 28)
            text_content = f"{self.text}: {self.score}"
            text = font.render(text_content, True, (255, 255, 255))  # White text
            
            # Calculate pill dimensions
            padding_x, padding_y = 15, 8
            pill_width = text.get_width() + padding_x * 2
            pill_height = text.get_height() + padding_y * 2
            
            # Create the pill rect
            pill_rect = pygame.Rect(
                self.score_position[0] - padding_x, 
                self.score_position[1] - padding_y,
                pill_width, 
                pill_height
            )
            
            # Draw the outer pill (colored border) with the ball's color
            pygame.draw.rect(screen, self.color, pill_rect, border_radius=pill_height//2)
            
            # Draw the inner pill (black interior) - 2 pixels smaller on each side
            inner_pill_rect = pygame.Rect(
                pill_rect.x + 2,
                pill_rect.y + 2,
                pill_rect.width - 4,
                pill_rect.height - 4
            )
            pygame.draw.rect(screen, (0, 0, 0), inner_pill_rect, border_radius=pill_height//2 - 1)
            
            # Center text in the pill
            text_pos = (
                self.score_position[0] - padding_x + pill_width//2 - text.get_width()//2,
                self.score_position[1] - padding_y + pill_height//2 - text.get_height()//2
            )
            
            # Draw text
            screen.blit(text, text_pos)

