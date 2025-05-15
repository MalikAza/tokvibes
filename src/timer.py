import math
import random
import pygame
from .consts import (
    FPS, TIMER_DURATION, TIMER_POSITION, TIMER_RADIUS, TIMER_COLOR,
    TIMER_FIRE_THRESHOLD, FIRE_LIFETIME, FIRE_SPEED, 
    TIMER_BLINK_THRESHOLD, TIMER_MAX_PARTICLES
)

class TimerFireParticle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(0.7, 2.0) * FIRE_SPEED  # Increased speed range
        self.dx = math.cos(angle) * speed
        self.dy = math.sin(angle) * speed
        self.lifetime = random.uniform(0.6, 1.2) * FIRE_LIFETIME  # Increased lifetime
        self.original_lifetime = self.lifetime
        self.size = random.uniform(2.5, 5.0)  # Increased size
        
    def update(self):
        self.x += self.dx
        self.y += self.dy
        self.dx *= 0.98  # Slow down over time
        self.dy *= 0.98
        self.lifetime -= 1
        self.size = max(0.5, self.size * 0.97)
        
    def draw(self, surface):
        alpha = int(255 * (self.lifetime / self.original_lifetime))
        intensity = 1 - (self.lifetime / self.original_lifetime)
        r = min(255, self.color[0] + int(intensity * (255 - self.color[0])))
        g = min(255, self.color[1] + int(intensity * (255 - self.color[1])))
        b = min(255, self.color[2] + int(intensity * (255 - self.color[2])))
        
        rgb_color = (r, g, b)
        particle_size = int(self.size * 2) + 1
        particle_surface = pygame.Surface((particle_size, particle_size), pygame.SRCALPHA)
        
        pygame.draw.circle(
            particle_surface, 
            rgb_color, 
            (particle_size // 2, particle_size // 2), 
            int(self.size)
        )
        
        particle_surface.set_alpha(alpha)
        surface.blit(
            particle_surface, 
            (int(self.x - self.size), int(self.y - self.size))
        )

class Timer:
    def __init__(self):
        self.duration = TIMER_DURATION * FPS  # Convert to frames
        self.remaining = self.duration
        self.position = TIMER_POSITION
        self.radius = TIMER_RADIUS
        self.base_color = TIMER_COLOR
        self.fire_particles = []
        self.active = True
        self.font = pygame.font.SysFont(None, 36)
        self.blink_state = True
        self.blink_counter = 0
        self.last_seconds = -1  # Track seconds to detect changes
        
        # New fields for second change blink
        self.second_change_blink = False
        self.second_change_frames = 0
        self.second_change_duration = 5  # Number of frames to blink on second change
        
    def update(self):
        if not self.active:
            return
            
        if self.remaining > 0:
            self.remaining -= 1
        else:
            self.active = False
            
        # Update existing fire particles
        self.fire_particles = [p for p in self.fire_particles if p.lifetime > 0]
        for particle in self.fire_particles:
            particle.update()
            
        # Update blink state for visual blinking effect
        seconds_remaining = self.remaining // FPS
        
        # Handle second change blinking
        if seconds_remaining != self.last_seconds:
            self.second_change_blink = True
            self.second_change_frames = self.second_change_duration
            self.last_seconds = seconds_remaining
            
        # Update second change blink counter
        if self.second_change_frames > 0:
            self.second_change_frames -= 1
            if self.second_change_frames <= 0:
                self.second_change_blink = False
        
        # Handle critical time blinking effect (faster as time decreases)
        if seconds_remaining <= TIMER_BLINK_THRESHOLD:
            # Calculate blink rate - higher as time decreases (1 to 15)
            blink_rate = int(15 * (1 - seconds_remaining / TIMER_BLINK_THRESHOLD)) + 1
            self.blink_counter += 1
            
            if self.blink_counter >= (FPS // blink_rate):
                self.blink_state = not self.blink_state
                self.blink_counter = 0
        else:
            self.blink_state = True  # No critical blinking above threshold
            
        # Generate fire particles throughout the timer duration
        # Calculate base number of particles based on time remaining
        if seconds_remaining <= TIMER_FIRE_THRESHOLD:
            # More particles as time gets lower for critical phase
            intensity = 1 - (seconds_remaining / TIMER_FIRE_THRESHOLD)
            particle_count = int(TIMER_MAX_PARTICLES * intensity)
            particle_generation_rate = max(1, int(5 * (1 - intensity)))  # 1-5 particles per frame
        else:
            # Fewer particles during normal operation
            base_intensity = 0.2  # Base intensity for white particles (20% of max)
            particle_count = int(TIMER_MAX_PARTICLES * base_intensity)
            particle_generation_rate = 10  # Slower generation rate during normal operation
            
        # Generate particles based on calculated rate
        if len(self.fire_particles) < particle_count and self.remaining % particle_generation_rate == 0:
            # Number of particles to generate per burst
            if seconds_remaining <= TIMER_FIRE_THRESHOLD:
                intensity = 1 - (seconds_remaining / TIMER_FIRE_THRESHOLD)
                particles_per_burst = min(4, int(3 * intensity) + 1)
            else:
                particles_per_burst = 1  # Just one particle per burst during normal operation
                
            # Generate particles around the perimeter
            for _ in range(particles_per_burst):
                angle = random.uniform(0, 2 * math.pi)
                variance = random.uniform(0.9, 1.1)  # Slight radius variance
                x = self.position[0] + math.cos(angle) * (self.radius * variance)
                y = self.position[1] + math.sin(angle) * (self.radius * variance)
                
                # Color transitions: white -> orange -> red as time decreases
                if seconds_remaining <= TIMER_FIRE_THRESHOLD:
                    # Critical phase colors (orange to red)
                    intensity = 1 - (seconds_remaining / TIMER_FIRE_THRESHOLD)
                    r = 255  # Always max red
                    g = max(0, int(165 * (1 - intensity)))  # Orange -> Red
                    b = max(0, int(30 * (1 - intensity)))   # Just a touch of blue
                else:
                    # Normal phase colors (white with a slight tint)
                    r = 255
                    g = 255
                    b = 255
                
                color = (r, g, b)
                self.fire_particles.append(TimerFireParticle(x, y, color))
                
    def get_time_color(self):
        """Return color based on remaining time"""
        # Transition from white -> orange -> red as time decreases
        seconds_remaining = self.remaining / FPS
        
        if seconds_remaining > TIMER_FIRE_THRESHOLD:
            return self.base_color  # White
        else:
            # Calculate transition (0.0 to 1.0)
            intensity = 1 - (seconds_remaining / TIMER_FIRE_THRESHOLD)
            r = 255  # Always max red
            g = max(0, int(165 * (1 - intensity)))  # Orange to Red
            b = max(0, int(30 * (1 - intensity)))   # Just a little blue for orange
            return (r, g, b)
            
    def draw(self, screen):
        # Draw fire effect
        if self.fire_particles:
            fire_surface = pygame.Surface((screen.get_width(), screen.get_height()), pygame.SRCALPHA)
            for particle in self.fire_particles:
                particle.draw(fire_surface)
            screen.blit(fire_surface, (0, 0))
            
        seconds_remaining = self.remaining // FPS
            
        # Skip drawing circle when critically blinking off
        if seconds_remaining <= TIMER_BLINK_THRESHOLD and not self.blink_state:
            # Only draw text during blink off
            text = self.font.render(f"{seconds_remaining}s", True, (255, 0, 0))
            text_rect = text.get_rect(center=self.position)
            screen.blit(text, text_rect)
            return
            
        # Draw background circle
        pygame.draw.circle(screen, (0, 0, 0), self.position, self.radius)
        
        # Draw remaining time arc
        if self.remaining > 0:
            time_color = self.get_time_color()
            progress = self.remaining / self.duration
            
            # Draw arc (counterclockwise)
            start_angle = -math.pi/2  # Start at top
            end_angle = start_angle + 2 * math.pi * progress
            
            # Make arc wider when time is low
            arc_width = 3
            if seconds_remaining <= TIMER_BLINK_THRESHOLD:
                arc_width = 4 + int(2 * (1 - seconds_remaining / TIMER_BLINK_THRESHOLD))
                
            pygame.draw.arc(
                screen,
                time_color,
                (self.position[0] - self.radius, self.position[1] - self.radius,
                 2 * self.radius, 2 * self.radius),
                start_angle,
                end_angle,
                arc_width
            )
            
        # Display seconds text with appropriate color
        seconds = max(0, self.remaining // FPS)
        
        # Set text color based on time and blinking states
        text_color = (255, 255, 255)  # Default white
        
        if seconds <= TIMER_BLINK_THRESHOLD:
            text_color = (255, 0, 0)  # Red when critically low
        elif self.second_change_blink:
            # Blink with brighter color on second change
            text_color = (255, 255, 0)  # Yellow for second change blink
            
        # Add a subtle scale effect to the text when second changes
        text = self.font.render(f"{seconds}s", True, text_color)
        text_rect = text.get_rect(center=self.position)
        
        # Scale the text slightly larger when second changes
        if self.second_change_blink:
            scale_factor = 1.2  # 20% larger during blink
            scaled_width = int(text.get_width() * scale_factor)
            scaled_height = int(text.get_height() * scale_factor)
            scaled_text = pygame.transform.scale(text, (scaled_width, scaled_height))
            
            # Recenter the scaled text
            scaled_rect = scaled_text.get_rect(center=self.position)
            screen.blit(scaled_text, scaled_rect)
        else:
            screen.blit(text, text_rect)
            
    def reset(self):
        self.remaining = self.duration
        self.active = True
        self.fire_particles = []
        self.blink_state = True
        self.blink_counter = 0
        self.second_change_blink = False
        self.second_change_frames = 0
        
    def is_expired(self):
        return self.remaining <= 0
