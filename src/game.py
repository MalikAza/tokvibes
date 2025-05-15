import math
import sys
import time
import random
from typing import List
import numpy as np
import pygame

from .circle import Circle
from .ball import Ball, FireParticle
from .consts import (
    BLACK,
    CIRCLE_NUMBERS_DISPLAY,
    FPS,
    GREEN,
    RED,
    SCORE_POSITION_1,
    SCORE_POSITION_2,
    HOLE_SHIFT,
    WHITE,
    GAME_TIMER_SECONDS,
    TIMER_RADIUS,
    TIMER_POSITION,
    TIMER_EXPLOSION_THRESHOLD,
    TIMER_PULSE_SPEED,
    TIMER_CRITICAL_COLOR,
    TIMER_WARNING_COLOR,
    TIMER_NORMAL_COLOR
)


class TimerExplosion:
    """Creates explosion effects for the timer"""
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.particles = []
        self.create_particles()
        
    def create_particles(self):
        # Create 20-30 particles in all directions
        num_particles = random.randint(20, 30)
        for _ in range(num_particles):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(2, 8)
            size = random.uniform(3, 8)
            lifetime = random.randint(10, 30)
            
            self.particles.append({
                'dx': math.cos(angle) * speed,
                'dy': math.sin(angle) * speed,
                'size': size,
                'lifetime': lifetime,
                'original_lifetime': lifetime
            })
    
    def update(self):
        # Update all particles
        for particle in self.particles:
            particle['dx'] *= 0.95  # Slow down
            particle['dy'] *= 0.95
            particle['x'] = particle.get('x', self.x) + particle['dx']
            particle['y'] = particle.get('y', self.y) + particle['dy']
            particle['lifetime'] -= 1
            particle['size'] *= 0.97  # Shrink
    
    def draw(self, screen):
        # Draw all particles
        for particle in self.particles:
            if particle['lifetime'] <= 0:
                continue
                
            alpha = int(255 * particle['lifetime'] / particle['original_lifetime'])
            size = int(particle['size'])
            
            # Increase brightness as particles fade
            fade_factor = 1 - (particle['lifetime'] / particle['original_lifetime'])
            r = min(255, self.color[0] + int((255 - self.color[0]) * fade_factor))
            g = min(255, self.color[1] + int((255 - self.color[1]) * fade_factor))
            b = min(255, self.color[2] + int((255 - self.color[2]) * fade_factor))
            
            # Create a surface for this particle
            particle_surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            pygame.draw.circle(
                particle_surf, 
                (r, g, b), 
                (size, size), 
                size
            )
            particle_surf.set_alpha(alpha)
            
            # Draw the particle
            screen.blit(
                particle_surf, 
                (int(particle.get('x', self.x) - size), int(particle.get('y', self.y) - size))
            )
    
    def is_alive(self):
        return any(p['lifetime'] > 0 for p in self.particles)


class Game:
    def __init__(
        self,
        screen: pygame.Surface,
        circles_number: int
    ) -> None:
        self.screen = screen
        self.clock = pygame.time.Clock()
        self.circles_number = circles_number
        self.center = pygame.Vector2(
            x=self.screen.get_width()//2,
            y=self.screen.get_height()//2
        )

        # Elements
        self.circles = [
            Circle(
                center=self.center,
                circle_number=i,
                hole_position=(i*HOLE_SHIFT)%360,
                displayed= i < CIRCLE_NUMBERS_DISPLAY
            )
            for i in range(self.circles_number)
        ]
        self.balls = [
            Ball(center=self.center, color=GREEN, score_position=SCORE_POSITION_1, text="Yes"),
            Ball(center=self.center, score_position=SCORE_POSITION_2, text="No")
        ]
        
        # Game state
        self.score = 0
        self.game_over = False
        self.debug_bounce = False
        
        # Timer variables
        self.start_time = time.time()
        self.time_remaining = GAME_TIMER_SECONDS
        self.timer_pulse = 0
        self.timer_explosions = []
        self.last_explosion_time = 0
        self.shake_screen = False
        self.shake_intensity = 0
        self.shake_duration = 0
        self.shake_offset = (0, 0)

    def _handle_events(self) -> bool:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            if event.type == pygame.KEYDOWN:
                match event.key:
                    case pygame.K_r:
                        self.__init__(self.screen, self.circles_number)
                        self.game_over = False

                    case pygame.K_d:
                        self.debug_bounce = not self.debug_bounce

                    case pygame.K_ESCAPE:
                        return False
                    
        return True
    
    def _handle_game(self) -> None:
        if self.game_over: 
            return

        # Update timer
        self._update_timer()
        
        # Update explosions
        self._update_explosions()
        
        # Update screen shake
        self._update_screen_shake()
        
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

        # Check for game over conditions
        if all(
            not circle.active and circle.desactivate_frame <= 0
            for circle in self.circles
        ) or self.time_remaining <= 0:
            self.game_over = True

    def _update_timer(self):
        # Calculate time remaining
        elapsed = time.time() - self.start_time
        self.time_remaining = max(0, GAME_TIMER_SECONDS - elapsed)
        
        # Update pulse effect (oscillating size)
        self.timer_pulse = (self.timer_pulse + TIMER_PULSE_SPEED) % (2 * math.pi)
        
        # Create explosion effects when time is low
        if self.time_remaining <= TIMER_EXPLOSION_THRESHOLD:
            # More frequent explosions as time decreases
            explosion_interval = max(0.5, self.time_remaining / 5)
            
            # Create new explosion if it's time
            if time.time() - self.last_explosion_time > explosion_interval:
                self.last_explosion_time = time.time()
                
                # Add random offset to timer position for explosion
                offset_x = random.randint(-20, 20)
                offset_y = random.randint(-20, 20)
                
                # Create explosion with appropriate color
                if self.time_remaining < 3:
                    color = TIMER_CRITICAL_COLOR
                    self._trigger_screen_shake(10, 5)  # Intense shake
                else:
                    color = TIMER_WARNING_COLOR
                    self._trigger_screen_shake(5, 3)  # Mild shake
                
                self.timer_explosions.append(
                    TimerExplosion(
                        TIMER_POSITION[0] + offset_x,
                        TIMER_POSITION[1] + offset_y,
                        color
                    )
                )
    
    def _update_explosions(self):
        # Update all explosion effects
        for explosion in self.timer_explosions:
            explosion.update()
        
        # Remove dead explosions
        self.timer_explosions = [e for e in self.timer_explosions if e.is_alive()]
    
    def _trigger_screen_shake(self, intensity, duration):
        self.shake_screen = True
        self.shake_intensity = intensity
        self.shake_duration = duration * FPS  # Convert to frames
    
    def _update_screen_shake(self):
        if self.shake_screen:
            if self.shake_duration > 0:
                self.shake_offset = (
                    random.randint(-self.shake_intensity, self.shake_intensity),
                    random.randint(-self.shake_intensity, self.shake_intensity)
                )
                self.shake_duration -= 1
            else:
                self.shake_screen = False
                self.shake_offset = (0, 0)

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
        center: bool = False,
        font_size: int = 36,
        color = WHITE
    ) -> None:
        font = pygame.font.SysFont(None, font_size)
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect(center=(x, y)) if center \
                    else text_surface.get_rect(topleft=(x, y))
        
        self.screen.blit(text_surface, text_rect)

    def _draw_timer(self):
        # Determine color based on time remaining
        if self.time_remaining <= 5:
            color = TIMER_CRITICAL_COLOR
        elif self.time_remaining <= TIMER_EXPLOSION_THRESHOLD:
            color = TIMER_WARNING_COLOR
        else:
            color = TIMER_NORMAL_COLOR
        
        # Calculate pulse effect
        pulse_amount = math.sin(self.timer_pulse) * 0.2
        
        # Make pulse more dramatic as time decreases
        if self.time_remaining <= TIMER_EXPLOSION_THRESHOLD:
            pulse_amount *= 2
        
        # Apply pulse to timer radius
        timer_radius = TIMER_RADIUS * (1 + pulse_amount)
        
        # Draw outer circle
        pygame.draw.circle(
            self.screen, 
            color, 
            (TIMER_POSITION[0] + self.shake_offset[0], TIMER_POSITION[1] + self.shake_offset[1]), 
            int(timer_radius)
        )
        
        # Draw inner black circle
        pygame.draw.circle(
            self.screen, 
            BLACK, 
            (TIMER_POSITION[0] + self.shake_offset[0], TIMER_POSITION[1] + self.shake_offset[1]), 
            int(timer_radius) - 3
        )
        
        # Draw time text
        minutes = int(self.time_remaining // 60)
        seconds = int(self.time_remaining % 60)
        time_text = f"{minutes:01d}:{seconds:02d}"
        
        # Make text larger and bounce more as time decreases
        font_size = 28
        if self.time_remaining <= TIMER_EXPLOSION_THRESHOLD:
            font_size = int(32 + math.sin(self.timer_pulse * 3) * 4)
        
        self._display_text(
            time_text,
            TIMER_POSITION[0] + self.shake_offset[0],
            TIMER_POSITION[1] + self.shake_offset[1],
            center=True,
            font_size=font_size,
            color=WHITE
        )
        
        # Draw explosions
        for explosion in self.timer_explosions:
            explosion.draw(self.screen)

    def _update_display(self) -> None:
        # Create base screen
        base_screen = pygame.Surface((self.screen.get_width(), self.screen.get_height()))
        base_screen.fill(BLACK)

        # Draw circles and balls on base screen
        displayed_circles = [c for c in self.circles if c.displayed]
        if len(displayed_circles) < CIRCLE_NUMBERS_DISPLAY:
            for circle in self.circles:
                if not circle.displayed:
                    circle.display()  
                    break

        displayed_circles = [c for c in self.circles if c.displayed]
        for circle in displayed_circles:
            circle.draw(base_screen)

        for ball in self.balls:
            ball.draw(base_screen)
            
        # Apply screen shake if active
        if self.shake_screen:
            self.screen.blit(base_screen, self.shake_offset)
        else:
            self.screen.blit(base_screen, (0, 0))
            
        # Draw timer AFTER blitting the base screen so it doesn't get overwritten
        self._draw_timer()

        if self.game_over:
            self._display_text(
                "Game Over! Press R to restart",
                self.center.x,
                self.center.y,
                center=True
            )

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
