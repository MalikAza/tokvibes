import math
import numpy as np
import pygame
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .ball import Ball
from .consts import CIRCLE_ROTATION_SPEED, CIRCLE_SPACING, FIRST_INNER_CIRCLE_RADIUS, HOLE_SHIFT, WHITE, HOLE_SIZE_DEGREES, CIRCLE_WIDTH, GRAVITY, ZOOM_SPEED


class Circle:
    def __init__(
        self,
        center: pygame.Vector2,
        circle_number: int,
        hole_position: float = 0,
    ):
        self.x = center.x
        self.y = center.y
        self.width = CIRCLE_WIDTH
        self.hole_position = math.radians(hole_position)
        self.hole_size = math.radians(HOLE_SIZE_DEGREES) 
        self.radius = FIRST_INNER_CIRCLE_RADIUS + circle_number * (CIRCLE_SPACING+CIRCLE_WIDTH)
        self.rotation_speed = CIRCLE_ROTATION_SPEED
        self.active = True
        self.angle = 0
        self.points_hole = []
        
    def update(self, number: int):
        if self.active:
            # update the radius depending of the ZOOM_SPEED only if the first circle is > FIRST_INNER_CIRCLE_RADIUS
            if self.radius > FIRST_INNER_CIRCLE_RADIUS + (CIRCLE_WIDTH + CIRCLE_SPACING) * number:
                self.radius -= ZOOM_SPEED
            
            # Rotate the circle
            self.angle = (self.angle + self.rotation_speed) % (2 * math.pi)
            # Update hole position
            self.hole_position = (self.hole_position + self.rotation_speed) % (2 * math.pi)
                        

    def desactivate(self):
        self.active = False
        print("Ball in hole")
        # TODO: faded explosion animation of the circle
        

    def draw(self, screen: pygame.Surface):
        # TODO: maybe if first time drawn, fade in the circle?
        if not self.active:
            return
        
        # Draw circle with a hole
        start_angle = self.angle + self.hole_position
        end_angle = start_angle + self.hole_size
        
        # Convert angles to start and end points
        points = []
        # Draw the main part of the circle (everything except the hole)
        for angle in np.linspace(end_angle, start_angle + 2*math.pi, 100):
            points.append((
                self.x + self.radius * math.cos(-angle),
                self.y + self.radius * math.sin(-angle)
            ))
        
        if len(points) > 1:
            pygame.draw.lines(screen, WHITE, False, points, self.width)
        