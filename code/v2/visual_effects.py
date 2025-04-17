import pygame
import random
import math

class VisualEffects:
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.particles = []
        self.shadows = []
        self.light_sources = []
        
    def add_particle(self, x, y, color, size=3, speed=2, lifetime=30, direction=None):
        """Add a particle effect at the given position"""
        if direction is None:
            angle = random.uniform(0, math.pi * 2)
            dx = math.cos(angle) * speed
            dy = math.sin(angle) * speed
        else:
            dx, dy = direction
            
        self.particles.append({
            'x': x,
            'y': y,
            'dx': dx,
            'dy': dy,
            'size': size,
            'color': color,
            'lifetime': lifetime,
            'max_lifetime': lifetime
        })
        
    def add_light_source(self, x, y, radius, color, intensity=0.7):
        """Add a light source at the given position"""
        self.light_sources.append({
            'x': x,
            'y': y,
            'radius': radius,
            'color': color,
            'intensity': intensity
        })
        
    def add_shadow(self, entity, length=20, direction=(1, 1)):
        """Add a shadow for an entity"""
        self.shadows.append({
            'entity': entity,
            'length': length,
            'direction': direction
        })
        
    def update_particles(self):
        """Update all particles"""
        for i in range(len(self.particles) - 1, -1, -1):
            p = self.particles[i]
            p['x'] += p['dx']
            p['y'] += p['dy']
            p['lifetime'] -= 1
            
            # Remove dead particles
            if p['lifetime'] <= 0:
                self.particles.pop(i)
                
    def draw_particles(self, surface, camera_offset=(0, 0)):
        """Draw all particles"""
        for p in self.particles:
            # Calculate fade based on lifetime
            alpha = int(255 * (p['lifetime'] / p['max_lifetime']))
            color = list(p['color'])
            if len(color) < 4:
                color.append(alpha)
            else:
                color[3] = alpha
                
            # Draw particle with camera offset
            x = int(p['x'] - camera_offset[0])
            y = int(p['y'] - camera_offset[1])
            
            # Create a surface for the particle with transparency
            particle_surface = pygame.Surface((p['size'] * 2, p['size'] * 2), pygame.SRCALPHA)
            pygame.draw.circle(particle_surface, color, (p['size'], p['size']), p['size'])
            surface.blit(particle_surface, (x - p['size'], y - p['size']))
            
    def draw_shadows(self, surface, camera_offset=(0, 0)):
        """Draw shadows for entities"""
        for shadow in self.shadows:
            entity = shadow['entity']
            length = shadow['length']
            direction = shadow['direction']
            
            # Create shadow polygon
            shadow_points = []
            rect = entity.rect
            
            # Base points (entity corners)
            shadow_points.append((rect.left, rect.top))
            shadow_points.append((rect.right, rect.top))
            shadow_points.append((rect.right, rect.bottom))
            shadow_points.append((rect.left, rect.bottom))
            
            # Offset points (shadow corners)
            shadow_points.append((rect.left + direction[0] * length, rect.bottom + direction[1] * length))
            shadow_points.append((rect.right + direction[0] * length, rect.bottom + direction[1] * length))
            
            # Adjust for camera
            adjusted_points = [(x - camera_offset[0], y - camera_offset[1]) for x, y in shadow_points]
            
            # Draw shadow
            shadow_surface = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
            pygame.draw.polygon(shadow_surface, (0, 0, 0, 100), adjusted_points)
            surface.blit(shadow_surface, (0, 0))
            
    def apply_lighting(self, surface):
        """Apply lighting effects to the surface"""
        # Create a dark overlay
        dark_surface = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        dark_surface.fill((0, 0, 0, 100))  # Semi-transparent black
        
        # Cut out light areas
        for light in self.light_sources:
            # Create a circular light mask
            light_mask = pygame.Surface((light['radius'] * 2, light['radius'] * 2), pygame.SRCALPHA)
            
            # Create gradient light
            for r in range(light['radius'], 0, -1):
                alpha = int(255 * (1 - (r / light['radius'])) * light['intensity'])
                color = (*light['color'], alpha)
                pygame.draw.circle(light_mask, color, (light['radius'], light['radius']), r)
                
            # Apply light to dark surface
            dark_surface.blit(light_mask, (light['x'] - light['radius'], light['y'] - light['radius']), special_flags=pygame.BLEND_RGBA_SUB)
            
        # Apply the final lighting to the main surface
        surface.blit(dark_surface, (0, 0))
        
    def create_3d_platform(self, width, height, color, highlight_color, shadow_color, depth=10):
        """Create a 3D platform surface"""
        # Create main surface with extra space for 3D effect
        surface = pygame.Surface((width, height + depth), pygame.SRCALPHA)
        
        # Top face (main platform)
        pygame.draw.rect(surface, color, (0, 0, width, height))
        
        # Right face (side)
        side_points = [
            (width, 0),
            (width, height),
            (width, height + depth),
            (width - depth, height + depth)
        ]
        pygame.draw.polygon(surface, shadow_color, side_points)
        
        # Bottom face
        bottom_points = [
            (0, height),
            (width, height),
            (width - depth, height + depth),
            (depth, height + depth)
        ]
        pygame.draw.polygon(surface, shadow_color, bottom_points)
        
        # Left face (highlight)
        left_points = [
            (0, 0),
            (0, height),
            (depth, height + depth),
            (depth, depth)
        ]
        pygame.draw.polygon(surface, highlight_color, left_points)
        
        # Top edge highlight
        pygame.draw.line(surface, highlight_color, (0, 0), (width, 0), 2)
        
        # Add circuit-like patterns
        for _ in range(3):
            x1 = random.randint(5, width-5)
            pygame.draw.line(surface, highlight_color, (x1, 0), (x1, height), 1)
            
        return surface
