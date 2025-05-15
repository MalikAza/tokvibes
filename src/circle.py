import math
import numpy as np
import pygame
import random
from typing import TYPE_CHECKING

from .consts import CIRCLE_FADE_IN_FRAME, CIRCLE_ROTATION_SPEED, CIRCLE_SPACING, FIRST_INNER_CIRCLE_RADIUS, HOLE_SHIFT, WHITE, HOLE_SIZE_DEGREES, CIRCLE_WIDTH, CIRCLE_FADE_OUT_FRAME, ZOOM_SPEED, DISSOLVE_SEGMENTS, MIN_CIRCLE_WIDTH


class Circle:
    def __init__(
        self,
        center: pygame.Vector2,
        circle_number: int,
        hole_position: float = 0,
        displayed: bool = False
    ):
        self.x = center.x
        self.y = center.y
        self.width = CIRCLE_WIDTH
        self.original_width = CIRCLE_WIDTH  # Store original width for fading
        self.color = WHITE
        self.hole_position = math.radians(hole_position)
        self.hole_size = math.radians(HOLE_SIZE_DEGREES) 
        self.radius = FIRST_INNER_CIRCLE_RADIUS + circle_number * (CIRCLE_SPACING+CIRCLE_WIDTH)
        self.rotation_speed = CIRCLE_ROTATION_SPEED
        self.angle = 0
        self.points_hole = []
        self.active = True
        self.displayed = displayed
        self.desactivate_frame = CIRCLE_FADE_OUT_FRAME
        self.activation_frame = CIRCLE_FADE_IN_FRAME if displayed else 0
        self.dissolve_segments = []
        self.generate_dissolve_segments()
        
    def generate_dissolve_segments(self):
        """Generate segments for dissolve effect"""
        # Create segments around the circle (excluding the hole)
        self.dissolve_segments = []
        total_angle = 2 * math.pi - self.hole_size
        segment_size = total_angle / DISSOLVE_SEGMENTS
        
        for i in range(DISSOLVE_SEGMENTS):
            # Calculate segment start and end angles
            start = i * segment_size + self.hole_position + self.hole_size
            end = start + segment_size
            
            segment = {
                'start': start,
                'end': end,
                'active': True,
                'dissolve_time': random.randint(0, CIRCLE_FADE_OUT_FRAME),
                'alpha_factor': random.uniform(0.5, 1.0)
            }
            self.dissolve_segments.append(segment)
        
    def update(self, number: int):
        # Always update rotation for active circles regardless of display status
        if self.active or self.desactivate_frame > 0:
            # update the radius depending of the ZOOM_SPEED only if the first circle is > FIRST_INNER_CIRCLE_RADIUS
            if self.radius > FIRST_INNER_CIRCLE_RADIUS + (CIRCLE_WIDTH + CIRCLE_SPACING) * number:
                self.radius -= ZOOM_SPEED
            
            # Rotate the circle
            self.angle = (self.angle + self.rotation_speed) % (2 * math.pi)
            # Update hole position
            self.hole_position = (self.hole_position + self.rotation_speed) % (2 * math.pi)
        
        # Update fade-out frame counter
        if not self.active and self.desactivate_frame > 0 and self.displayed:
            self.desactivate_frame -= 1
            for segment in self.dissolve_segments:
                if self.desactivate_frame <= segment['dissolve_time']:
                    segment['active'] = False
        
        # Only increment activation_frame for displayed circles
        if self.displayed and self.activation_frame < CIRCLE_FADE_IN_FRAME and self.active:
            self.activation_frame += 1

    def desactivate(self):
        self.active = False

    def display(self):
        self.displayed = True
        self.activation_frame = 0
        

    def draw(self, screen: pygame.Surface):
        # Don't draw if not displayed or fully faded out
        if not self.displayed or (not self.active and self.desactivate_frame <= 0):
            return
        
        start_angle = self.angle + self.hole_position
        end_angle = start_angle + self.hole_size
        
        # Handle fade-out with dissolve effect (deactivated circles)
        if not self.active and self.desactivate_frame > 0:
            fade_surface = pygame.Surface((screen.get_width(), screen.get_height()), pygame.SRCALPHA)
            
            fade_progress = max(0, min(1, (self.desactivate_frame / CIRCLE_FADE_OUT_FRAME)))
            current_width = max(1, int(self.original_width * fade_progress))
            
            # Draw each active segment separately
            for segment in self.dissolve_segments:
                if segment['active']:
                    seg_start = self.angle + segment['start']
                    seg_end = self.angle + segment['end']
                    
                    segment_progress = max(0, min(1, (self.desactivate_frame - segment['dissolve_time']) / 
                                          (CIRCLE_FADE_OUT_FRAME - segment['dissolve_time'] + 1)))
                    
                    segment_progress = segment_progress * segment_progress  # Quadratic fade
                    
                    alpha = int(255 * segment_progress * segment['alpha_factor'])
                    color = (*self.color[:3], alpha)
                    
                    pygame.draw.arc(
                        fade_surface, 
                        color, 
                        (self.x - self.radius, self.y - self.radius, 2 * self.radius, 2 * self.radius), 
                        seg_start, 
                        seg_end, 
                        current_width
                    )
            
            screen.blit(fade_surface, (0, 0))
            return
        
        # Handle fade-in (newly displayed circles)
        if self.activation_frame < CIRCLE_FADE_IN_FRAME:
            fade_surface = pygame.Surface((screen.get_width(), screen.get_height()), pygame.SRCALPHA)

            alpha = int(255 * (self.activation_frame / CIRCLE_FADE_IN_FRAME))
            color = (*self.color[:3], alpha) 
            
            pygame.draw.arc(
                fade_surface, 
                color, 
                (self.x - self.radius, self.y - self.radius, 2 * self.radius, 2 * self.radius), 
                end_angle, 
                start_angle + 2 * math.pi, 
                self.width
            )
            screen.blit(fade_surface, (0, 0))
        else:

            # Draw fully visible circle
            pygame.draw.arc(
                screen, 
                self.color, 
                (self.x - self.radius, self.y - self.radius, 2 * self.radius, 2 * self.radius), 
                end_angle, 
                start_angle + 2 * math.pi, 
                self.width
            )

