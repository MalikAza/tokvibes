import math
import sys
import random
from typing import List
import numpy as np
import pygame

from .type import Args
from .circle import Circle
from .ball import Ball
from .timer import Timer
from .consts import (
    BLACK,
    FPS,
    GREEN,
    RED,
    SCORE_POSITION_1,
    SCORE_POSITION_2,
    HOLE_SHIFT,
    WHITE,
    SCREEN_SHAKE_INTENSITY,
    SCREEN_SHAKE_DURATION
)


class Game:
    def __init__(
        self,
        screen: pygame.Surface,
        args: Args
    ) -> None:
        self.screen = screen
        self.clock = pygame.time.Clock()
        self.circles_number = args.circles
        self.circles_display = args.circles_display
        self.center = pygame.Vector2(
            x=self.screen.get_width()//2,
            y=self.screen.get_height()//2
        )

        self._init_elements()
        self._init_states()
        self.timer = Timer()
        
        # Screen shake effect
        self.shake_frames = 0
        self.shake_duration = 0
        self.shake_intensity = 0
        self.original_screen_rect = self.screen.get_rect()

    def _init_elements(self) -> None:
        self.circles = [
            Circle(
                center=self.center,
                circle_number=i,
                hole_position=(i*HOLE_SHIFT)%360,
                displayed= i < self.circles_display
            )
            for i in range(self.circles_number)
        ]
        self.balls = [
            Ball(center=self.center, score_position=SCORE_POSITION_2, text="No"),
            Ball(center=self.center, color=GREEN, score_position=SCORE_POSITION_1, text="Yes")
        ]

    def _init_states(self) -> None:
        self.score = 0
        self.game_over = False
        self.debug_bounce = False

    def _handle_events(self) -> bool:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            if event.type == pygame.KEYDOWN:
                match event.key:
                    case pygame.K_r:
                        self.__init__(self.screen, self.circles_number, self.circles_display)
                        self.game_over = False

                    case pygame.K_d:
                        self.debug_bounce = not self.debug_bounce

                    case pygame.K_ESCAPE:
                        return False
                    
        return True

    def _start_screen_shake(self, intensity=SCREEN_SHAKE_INTENSITY, duration=SCREEN_SHAKE_DURATION):
        """Start a screen shake effect"""
        self.shake_frames = int(duration * FPS)
        self.shake_duration = self.shake_frames
        self.shake_intensity = intensity
    
    def _handle_game(self) -> None:
        if self.game_over: return

        # Update timer
        self.timer.update()
        if self.timer.is_expired():
            self.game_over = True
            return

        # Update screen shake
        if self.shake_frames > 0:
            self.shake_frames -= 1

        for ball in self.balls:
            ball.move()

        active_circles: List[Circle] = []
        for i, circle in enumerate(self.circles):
            circle.update(i) # Update circle rotations/zoom

            # Keeping only active circles
            if circle.active or circle.desactivate_frame > 0:
                active_circles.append(circle)
                
            # Check for collisions, escapes, and update score
            if circle.active:
                for ball in self.balls:
                    # Check if the ball scored a point
                    if ball.check_collision(circle):
                        # Trigger screen shake on score
                        self._start_screen_shake()

        self.circles = active_circles

        if all(
            not circle.active and circle.desactivate_frame <= 0
            for circle in self.circles
        ):
            self.game_over = True

    def _draw_debug_info(self):
        # Draw hole visualization for debugging
        for circle in self.circles:
            if circle.active:
             # Get hole start and end angles
                hole_start_angle = circle.angle + circle.hole_position
                hole_end_angle = hole_start_angle + circle.hole_size
            
                # Draw the hole path
                points_hole = []
                for angle in np.linspace(hole_start_angle, hole_end_angle, 100):
                    points_hole.append((
                        circle.x + circle.radius * math.cos(-angle),
                        circle.y + circle.radius * math.sin(-angle)
                    ))
                if len(points_hole) > 1:
                    pygame.draw.lines(self.screen, RED, False, points_hole, 5)
    
    def _display_text(
        self,
        text: str,
        x: float,
        y: float,
        center: bool = False
    ) -> None:
        font = pygame.font.SysFont(None, 36)
        text_surface = font.render(text, True, WHITE)
        text_rect = text_surface.get_rect(center=(x, y)) if center \
                    else text_surface.get_rect(topleft=(x, y))
        
        self.screen.blit(text_surface, text_rect)

    def _update_display(self) -> None:
        # Clear the screen
        self.screen.fill(BLACK)
        
        # Create a display surface for shake effect
        if self.shake_frames > 0:
            # Calculate shake intensity based on remaining frames
            shake_progress = self.shake_frames / self.shake_duration
            current_intensity = self.shake_intensity * shake_progress
            
            # Apply random offset for shaking
            dx = random.randint(-int(current_intensity), int(current_intensity))
            dy = random.randint(-int(current_intensity), int(current_intensity))
            
            # Create a display surface that will be offset
            display_surface = pygame.Surface((self.screen.get_width(), self.screen.get_height()))
            display_surface.fill(BLACK)
        else:
            # No shake, use the main screen directly
            display_surface = self.screen
            dx, dy = 0, 0

        # Draw all game elements on the appropriate surface
        displayed_circles = [c for c in self.circles if c.displayed]
        if len(displayed_circles) < self.circles_display:
            for circle in self.circles:
                if not circle.displayed:
                    circle.display()  
                    break

        displayed_circles = [c for c in self.circles if c.displayed]
        for circle in displayed_circles:
            circle.draw(display_surface)

        for ball in self.balls:
            ball.draw(display_surface)
            
        # Draw the timer
        self.timer.draw(display_surface)

        if self.game_over:
            game_over_text = "Time's up!" if self.timer.is_expired() else "Game Over!"
            self._display_text(
                f"{game_over_text} Press R to restart",
                self.center.x,
                self.center.y,
                center=True
            )

        if self.debug_bounce:
            self._draw_debug_info()

        # If shaking, blit the display surface onto the screen with offset
        if self.shake_frames > 0:
            self.screen.blit(display_surface, (dx, dy))
        
        # Update the display and maintain frame rate
        pygame.display.flip()
        self.clock.tick(FPS)
        
    def run(self):
        running = True
        while running:
            running = self._handle_events()
            self._handle_game()
            self._update_display()
        
        pygame.quit()
        sys.exit()
