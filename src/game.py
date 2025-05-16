import math
import sys
from typing import List, Union
import numpy as np
import pygame

from .type import Args, ColorType, GameType
from .circle import Circle
from .ball import Ball
from .timer import Timer
from .consts import (
    Colors,
    FPS,
    SCORE_POSITION_1,
    SCORE_POSITION_2,
    HOLE_SHIFT,
)


class Game(GameType):
    def __init__(
        self,
        screen: pygame.Surface,
        args: Args
    ) -> None:
        self.screen = screen
        self.__args = args
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

    def _init_elements(self) -> None:
        self.circles = [
            Circle(
                id=i,
                position=self.center,
                hole_position=(i*HOLE_SHIFT)%360,
                displayed=i<self.circles_display
            )
            for i in range(self.circles_number)
        ]
        self.balls = [
            Ball(
                position=self.center,
                score_position=SCORE_POSITION_1,
                color=Colors.GREEN.value,
                text="Yes"
            ),
            Ball(
                position=self.center,
                score_position=SCORE_POSITION_2,
                color=Colors.RED.value,
                text="No"
            ),
        ]

    def _init_states(self) -> None:
        self.game_over = False
        self.debug_bounce = False

    def _handle_events(self) -> bool:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            if event.type == pygame.KEYDOWN:
                match event.key:
                    case pygame.K_r:
                        self.__init__(self.screen, self.__args)
                        self.game_over = False

                    case pygame.K_d:
                        self.debug_bounce = not self.debug_bounce

                    case pygame.K_ESCAPE:
                        return False
                    
        return True
    
    def _handle_game(self) -> None:
        if self.game_over: return

        # Update timer
        self.timer.update()
        if self.timer.is_expired():
            self.game_over = True
            return

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
                    ball.check_collision(circle)

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
                    pygame.draw.lines(self.screen, Colors.RED.value, False, points_hole, 5)
    
    def _get_winner(self) -> Union[False, Ball]:
        """If Tie, returns False.
        Otherwise returns the ball instance with the highest score.
        """
        if len(set([ball.score for ball in self.balls])) == 1:
            return False
        
        return max(self.balls, key=lambda x: x.score)

    def _colored_text_surface(
        self,
        text: str,
        color: ColorType
    ) -> pygame.Surface:
        font = pygame.font.SysFont(None, 36)
        
        return font.render(text, True, color)

    def _display_text(
        self,
        text_surfs: Union[pygame.Surface, List[pygame.Surface]],
        x: float,
        y: float,
        center: bool = False
    ) -> None:
        if not isinstance(text_surfs, list):
            text_surfs = [text_surfs]

        total_width = sum(surf.get_width() for surf in text_surfs)
        max_height = max(surf.get_height() for surf in text_surfs)

        if center:
            start_x = x - total_width // 2
            start_y = y - max_height // 2
        else:
            start_x = x
            start_y = y

        current_x = start_x
        for surf in text_surfs:
            self.screen.blit(surf, (current_x, start_y))
            current_x += surf.get_width()

    def _update_display(self) -> None:
        self.screen.fill(Colors.BLACK.value)

        if self.game_over:
            winner = self._get_winner()
            title_text = "Tie!" if not winner else f'"{winner.text}" wins!'
            title_color = Colors.WHITE.value if not winner else winner.color

            restart_text = " Press R to restart"

            text_surfs = [
                self._colored_text_surface(title_text, title_color),
                self._colored_text_surface(restart_text, Colors.WHITE.value)
            ]
            self._display_text(
                text_surfs,
                self.center.x,
                self.center.y,
                center=True
            )
            pygame.display.flip()
            self.clock.tick(FPS)
            return

        # Add one more circle at this frame if needed
        if sum(1 for c in self.circles if c.displayed) < self.circles_display:
            next_circle = next((c for c in self.circles if not c.displayed), None)
            if next_circle:
                next_circle.display()

        for circle in self.circles:
            if circle.displayed:
                circle.draw(self.screen)

        for ball in self.balls:
            ball.draw(self.screen)
            
        self.timer.draw(self.screen)

        if self.debug_bounce:
            self._draw_debug_info()
        
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
