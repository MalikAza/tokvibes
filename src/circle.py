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
        displayed: bool = False,
        hole_position: float = 0,
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
        self.activation_frame = 0
        
    def update(self, number: int):
        if self.active or self.desactivate_frame > 0:
            # update the radius depending of the ZOOM_SPEED only if the first circle is > FIRST_INNER_CIRCLE_RADIUS
            if self.radius > FIRST_INNER_CIRCLE_RADIUS + (CIRCLE_WIDTH + CIRCLE_SPACING) * number:
                self.radius -= ZOOM_SPEED
            
            # Rotate the circle
            self.angle = (self.angle + self.rotation_speed) % (2 * math.pi)
            # Update hole position
            self.hole_position = (self.hole_position + self.rotation_speed) % (2 * math.pi)
        
        if not self.active and self.desactivate_frame > 0:
            self.desactivate_frame -= 1
        
        if self.activation_frame < CIRCLE_FADE_IN_FRAME and self.active and self.displayed:
            print(f"Circle {number} activated")
            self.activation_frame += 1


    def desactivate(self):
        self.active = False
        
        

    def draw(self, screen: pygame.Surface):
        if not self.active and self.desactivate_frame <= 0:
            return
        
        if not self.active and self.desactivate_frame > 0:
            # Draw the circle with a fade-out effect using a transparent surface
            fade_surface = pygame.Surface((screen.get_width(), screen.get_height()), pygame.SRCALPHA)
            alpha = int(255 * (self.desactivate_frame / CIRCLE_FADE_OUT_FRAME))
            color = (*self.color[:3], alpha) 
            
            start_angle = self.angle + self.hole_position
            end_angle = start_angle + self.hole_size
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
        
        # Draw the circle with a fade-in effect using a transparent surface
        if self.active and self.activation_frame < CIRCLE_FADE_IN_FRAME:
            fade_surface = pygame.Surface((screen.get_width(), screen.get_height()), pygame.SRCALPHA)
            alpha = int(255 * (self.activation_frame / CIRCLE_FADE_IN_FRAME))
            color = (*self.color[:3], alpha) 
            
            start_angle = self.angle + self.hole_position
            end_angle = start_angle + self.hole_size
            pygame.draw.arc(
                fade_surface, 
                color, 
                (self.x - self.radius, self.y - self.radius, 2 * self.radius, 2 * self.radius), 
                end_angle, 
                start_angle + 2 * math.pi, 
                self.width
            )
            screen.blit(fade_surface, (0, 0))


        # Draw the circle full activateddd
        if self.active and self.activation_frame <= CIRCLE_FADE_IN_FRAME and self.displayed:
            start_angle = self.angle + self.hole_position
            end_angle = start_angle + self.hole_size
            
            # Draw the rest of the circle in white
            pygame.draw.arc(
                screen, 
                self.color, 
                (self.x - self.radius, self.y - self.radius, 2 * self.radius, 2 * self.radius), 
                end_angle, 
                start_angle + 2 * math.pi, 
                self.width
            )

