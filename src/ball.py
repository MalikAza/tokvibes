import math
import os
import random
import numpy as np
import pygame
from typing import TYPE_CHECKING, List

if TYPE_CHECKING:
    from .circle import Circle

from .consts import (
    BALL_RADIUS, BALL_TRAIL_LENGTH, BOUNCE_DAMPENING, HEIGHT, MIN_VELOCITY, 
    RED, GRAVITY, WIDTH, FIRE_PARTICLES, FIRE_LIFETIME, FIRE_SPEED, 
    SCORE_EFFECT_DURATION, FPS, BALL_TEXT_SIZE
)


class FireParticle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        # Random initial velocity with upward bias
        self.dx = random.uniform(-1.0, 1.0) * FIRE_SPEED
        self.dy = random.uniform(-2.0, -0.5) * FIRE_SPEED
        self.lifetime = random.uniform(0.5, 1.0) * FIRE_LIFETIME
        self.original_lifetime = self.lifetime
        self.size = random.uniform(2, 4)
        
    def update(self):
        # Update position
        self.x += self.dx
        self.y += self.dy
        # Add some random movement for flame effect
        self.dx += random.uniform(-0.1, 0.1)
        self.dy -= random.uniform(0.05, 0.15)  # Flames rise
        # Decrease lifetime
        self.lifetime -= 1
        # Decrease size as it burns out
        self.size = max(0.5, self.size * 0.97)
        
    def draw(self, surface):
        # Calculate alpha based on remaining lifetime
        alpha = int(255 * (self.lifetime / self.original_lifetime))
        # Make color more yellow/white as it burns (fire effect)
        intensity = 1 - (self.lifetime / self.original_lifetime)
        r = min(255, self.color[0] + int(intensity * (255 - self.color[0])))
        g = min(255, self.color[1] + int(intensity * (255 - self.color[1])))
        b = min(255, self.color[2] + int(intensity * (255 - self.color[2])))
        
        # Fix: Create RGB color (without alpha) for drawing on the surface
        rgb_color = (r, g, b)
        
        # Create a small surface for this particle with alpha
        particle_size = int(self.size * 2) + 1  # Ensure odd size for centering
        particle_surface = pygame.Surface((particle_size, particle_size), pygame.SRCALPHA)
        
        # Draw the circle on the particle surface
        pygame.draw.circle(
            particle_surface, 
            rgb_color, 
            (particle_size // 2, particle_size // 2), 
            int(self.size)
        )
        
        # Set the alpha for the whole surface
        particle_surface.set_alpha(alpha)
        
        # Blit the particle onto the main surface
        surface.blit(
            particle_surface, 
            (int(self.x - self.size), int(self.y - self.size))
        )


class Ball:
    def __init__(
        self,
        center: pygame.Vector2,
        color=RED,
        radius=BALL_RADIUS,
        score_position=(0, 0),
        text="yes",
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
        self.fire_particles: List[FireParticle] = []
        self.pill_rect = None  # Will store the pill rect for particle emission
        self.score_effect_timer = 0    # Counter for how long to show effect
        self.score_effect_duration = SCORE_EFFECT_DURATION * FPS  # Convert seconds to frames
        
        # New properties for ball fire effect
        self.ball_fire_timer = 0
        self.ball_fire_duration = SCORE_EFFECT_DURATION * FPS
        self.ball_fire_particles = []
    
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
        
        # Update fire particles and effect timer
        if self.score_effect_timer > 0:
            self.score_effect_timer -= 1
            
        # Update ball fire timer
        if self.ball_fire_timer > 0:
            self.ball_fire_timer -= 1
        
        self._update_fire_particles()
        self._update_ball_fire_particles()
        return
        
    def _update_ball_fire_particles(self):
        """Update fire particles around the ball itself"""
        # Remove dead particles
        self.ball_fire_particles = [p for p in self.ball_fire_particles if p.lifetime > 0]
        
        # Update existing particles
        for particle in self.ball_fire_particles:
            particle.update()
        
        # Only add new particles if ball fire effect is active
        if self.ball_fire_timer > 0:
            # Create more particles when effect is fresh (higher emission rate)
            effect_freshness = self.ball_fire_timer / self.ball_fire_duration
            max_ball_particles = FIRE_PARTICLES * 1.5  # More particles for the ball (50% more)
            new_particles = max(1, int((max_ball_particles - len(self.ball_fire_particles)) * effect_freshness / 4))
            
            for _ in range(new_particles):
                # Generate particles in a circle around the ball
                angle = random.uniform(0, 2 * math.pi)
                offset = random.uniform(0.8, 1.2)  # Slight randomness in emission distance
                
                # Position slightly outside the ball's perimeter
                x = self.x + math.cos(angle) * (self.radius * offset)
                y = self.y + math.sin(angle) * (self.radius * offset)
                
                # Customize particle for more dramatic effect
                particle = FireParticle(x, y, self.color)
                
                # Add velocity in direction away from ball center (fire bursting outward)
                outward_speed = random.uniform(1.0, 3.0) * FIRE_SPEED
                particle.dx = math.cos(angle) * outward_speed
                particle.dy = math.sin(angle) * outward_speed
                
                # Larger particles for ball fire
                particle.size *= 1.3
                
                self.ball_fire_particles.append(particle)

    def _update_fire_particles(self):
        # Remove dead particles
        self.fire_particles = [p for p in self.fire_particles if p.lifetime > 0]
        
        # Update existing particles
        for particle in self.fire_particles:
            particle.update()
        
        # Only add new particles if score effect is active
        if self.pill_rect and self.score_position != (0, 0) and self.score_effect_timer > 0:
            # Create more particles when effect is fresh (higher emission rate)
            effect_freshness = self.score_effect_timer / self.score_effect_duration
            new_particles = max(1, int((FIRE_PARTICLES - len(self.fire_particles)) * effect_freshness / 5))
            
            for _ in range(new_particles):
                # Emit from random position around pill perimeter
                perimeter_choice = random.randint(0, 3)  # 0=top, 1=right, 2=bottom, 3=left
                
                if perimeter_choice == 0:  # Top
                    x = random.uniform(self.pill_rect.left, self.pill_rect.right)
                    y = self.pill_rect.top
                elif perimeter_choice == 1:  # Right
                    x = self.pill_rect.right
                    y = random.uniform(self.pill_rect.top, self.pill_rect.bottom)
                elif perimeter_choice == 2:  # Bottom
                    x = random.uniform(self.pill_rect.left, self.pill_rect.right)
                    y = self.pill_rect.bottom
                else:  # Left
                    x = self.pill_rect.left
                    y = random.uniform(self.pill_rect.top, self.pill_rect.bottom)
                    
                self.fire_particles.append(FireParticle(x, y, self.color))
        
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
                
                # Trigger fire effect on the score pill
                self.score_effect_timer = self.score_effect_duration
                
                # Trigger fire effect on the ball itself
                self.ball_fire_timer = self.ball_fire_duration
                
                # Add an initial burst of particles
                self._create_score_burst()
                
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
            
    def _create_score_burst(self):
        """Create an initial burst of particles when scoring"""
        burst_count = 20  # Number of particles in the initial burst
        
        for _ in range(burst_count):
            angle = random.uniform(0, 2 * math.pi)
            offset = random.uniform(0.9, 1.3)
            
            # Position at the ball's perimeter
            x = self.x + math.cos(angle) * (self.radius * offset)
            y = self.y + math.sin(angle) * (self.radius * offset)
            
            # Create particle with bright color (add some yellow to make it more fiery)
            r = 255
            g = random.randint(180, 255)  # More yellow for a more intense fire effect
            b = random.randint(0, 100)
            color = (r, g, b)
            
            particle = FireParticle(x, y, color)
            
            # Stronger outward velocity for burst effect
            burst_speed = random.uniform(2.0, 5.0) * FIRE_SPEED
            particle.dx = math.cos(angle) * burst_speed
            particle.dy = math.sin(angle) * burst_speed
            
            # Larger particles for the burst
            particle.size = random.uniform(3, 7)
            
            self.ball_fire_particles.append(particle)
            
    def draw(self, screen: pygame.Surface):
        # Draw ball fire particles
        if self.ball_fire_particles:
            fire_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            for particle in self.ball_fire_particles:
                particle.draw(fire_surface)
            screen.blit(fire_surface, (0, 0))

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

        # Draw the ball
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)
        pygame.draw.circle(screen, (0, 0, 0), (int(self.x), int(self.y)), self.radius - 2)
        
        # Create a pulsating effect when ball is on fire
        pulse_size = 0
        if self.ball_fire_timer > 0:
            # Calculate pulse size based on remaining fire time
            pulse_progress = self.ball_fire_timer / self.ball_fire_duration
            pulse_frequency = 0.3  # Controls how fast the pulse happens
            pulse_magnitude = 3  # Maximum size increase
            pulse_size = int(math.sin(pulse_progress * 30) * pulse_magnitude * pulse_progress)
        
        # Write text in ball, accounting for any pulse effect
        font = pygame.font.Font(None, BALL_TEXT_SIZE + pulse_size)
        text_color = (255, 255, 255)
        
        # Make text yellow/orange when ball is on fire
        if self.ball_fire_timer > 0:
            # Pulse the text color too
            pulse_color = int(math.sin(self.ball_fire_timer * 0.5) * 40 + 215)
            text_color = (255, pulse_color, 0)
            
        text = font.render(self.text, True, text_color)
        text_rect = text.get_rect(center=(self.x, self.y))
        screen.blit(text, text_rect)

        # Draw score with pill background and fire effect (if active)
        if self.score_position != (0, 0):
            # Only draw fire particles if effect is active or there are remaining particles
            if self.score_effect_timer > 0 or self.fire_particles:
                # Create fire particle effect surface
                fire_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
                
                # Draw all fire particles
                for particle in self.fire_particles:
                    particle.draw(fire_surface)
                
                # Draw the fire effect
                screen.blit(fire_surface, (0, 0))
            
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
            self.pill_rect = pill_rect  # Store for particle emission
            
            # Draw the outer pill (colored border)
            pygame.draw.rect(screen, self.color, pill_rect, border_radius=pill_height//2)
            
            # Draw the inner pill (black interior)
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

