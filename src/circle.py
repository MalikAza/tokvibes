import math
import numpy as np
import pygame
from typing import TYPE_CHECKING

from .consts import CIRCLE_FADE_IN_FRAME, CIRCLE_ROTATION_SPEED, CIRCLE_SPACING, FIRST_INNER_CIRCLE_RADIUS, HOLE_SHIFT, WHITE, HOLE_SIZE_DEGREES, CIRCLE_WIDTH, CIRCLE_FADE_OUT_FRAME, ZOOM_SPEED


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
        
        # Calculate the arc angles
        start_angle = self.angle + self.hole_position
        end_angle = start_angle + self.hole_size
        
        # Handle fade-out (deactivated circles)
        if not self.active and self.desactivate_frame > 0:
            fade_surface = pygame.Surface((screen.get_width(), screen.get_height()), pygame.SRCALPHA)
            alpha = int(255 * (self.desactivate_frame / CIRCLE_FADE_OUT_FRAME))
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
            return
        
        # Handle fade-in (newly displayed circles)
        if self.activation_frame < CIRCLE_FADE_IN_FRAME:
            fade_surface = pygame.Surface((screen.get_width(), screen.get_height()), pygame.SRCALPHA)
            # Correct alpha calculation: start at 0, go to 255
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

