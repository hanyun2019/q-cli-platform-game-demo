import pygame
import sys
import random
import math
import os
from pygame.locals import *
from camera import Camera
from sound_manager import SoundManager
from visual_effects import VisualEffects

# Initialize pygame
pygame.init()

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
GRAVITY = 0.75
SCROLL_THRESHOLD = 200

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
NEON_BLUE = (0, 195, 255)
NEON_PINK = (255, 0, 153)
NEON_GREEN = (57, 255, 20)
NEON_PURPLE = (180, 0, 255)
NEON_YELLOW = (255, 255, 0)

# Create the screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Cyberpunk Platform Game - Enhanced')

# Clock for controlling the frame rate
clock = pygame.time.Clock()

# Initialize camera, sound manager, and visual effects
camera = Camera(SCREEN_WIDTH, SCREEN_HEIGHT)
sound_manager = SoundManager()
visual_effects = VisualEffects(SCREEN_WIDTH, SCREEN_HEIGHT)

# Player class
class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        # Try to load player image, fall back to drawing if not available
        try:
            self.image = pygame.image.load(os.path.join('assets', 'player.png')).convert_alpha()
        except:
            # Create a simple player character
            self.image = pygame.Surface((32, 48), pygame.SRCALPHA)
            pygame.draw.rect(self.image, NEON_BLUE, (8, 8, 16, 32))
            pygame.draw.circle(self.image, WHITE, (16, 8), 8)
            pygame.draw.line(self.image, NEON_PINK, (12, 6), (20, 6), 2)
        
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.vel_y = 0
        self.vel_x = 0
        self.jumped = False
        self.direction = 0
        self.in_air = True
        self.last_ground_y = y
        
        # Animation variables
        self.jumping_frame = 0
        self.running_frame = 0
        self.frame_timer = 0
        
        # Add light source to player
        visual_effects.add_light_source(x + self.width // 2, y + self.height // 2, 
                                       100, NEON_BLUE, 0.6)

    def update(self, platforms):
        dx = 0
        dy = 0
        
        # Get key presses
        key = pygame.key.get_pressed()
        if key[K_LEFT]:
            dx = -5
            self.direction = -1
            self.vel_x = max(self.vel_x - 0.2, -5)
        elif key[K_RIGHT]:
            dx = 5
            self.direction = 1
            self.vel_x = min(self.vel_x + 0.2, 5)
        else:
            # Apply friction
            if self.vel_x > 0:
                self.vel_x = max(self.vel_x - 0.3, 0)
            elif self.vel_x < 0:
                self.vel_x = min(self.vel_x + 0.3, 0)
                
        dx = self.vel_x
                
        if key[K_SPACE] and not self.jumped and not self.in_air:
            self.vel_y = -15
            self.jumped = True
            self.in_air = True
            self.last_ground_y = self.rect.y
            # Play jump sound
            sound_manager.play_sound('jump', 0.4)
            
            # Add jump particles
            for _ in range(10):
                visual_effects.add_particle(
                    self.rect.centerx, self.rect.bottom,
                    NEON_BLUE, random.randint(2, 4), 
                    random.uniform(1, 3), random.randint(20, 40),
                    (random.uniform(-1, 1), random.uniform(-2, 0))
                )
                
        if not key[K_SPACE]:
            self.jumped = False
            
        # Apply gravity
        self.vel_y += GRAVITY
        if self.vel_y > 10:
            self.vel_y = 10
        dy += self.vel_y
        
        # Check for collisions
        self.in_air = True
        for platform in platforms:
            # Check for collision in x direction
            if platform.rect.colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                dx = 0
                self.vel_x = 0
                
            # Check for collision in y direction
            if platform.rect.colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                # Check if below platform (jumping)
                if self.vel_y < 0:
                    dy = platform.rect.bottom - self.rect.top
                    self.vel_y = 0
                # Check if above platform (falling)
                elif self.vel_y >= 0:
                    dy = platform.rect.top - self.rect.bottom
                    self.vel_y = 0
                    self.in_air = False
                    
                    # If we just landed, play sound and add particles
                    if self.rect.y - self.last_ground_y > 10:  # Only if falling from height
                        sound_manager.play_sound('land', 0.3)
                        # Add landing particles
                        for _ in range(8):
                            visual_effects.add_particle(
                                self.rect.centerx, self.rect.bottom,
                                WHITE, random.randint(1, 3),
                                random.uniform(0.5, 2), random.randint(10, 30),
                                (random.uniform(-2, 2), random.uniform(-0.5, 0))
                            )
        
        # Update player position
        self.rect.x += dx
        self.rect.y += dy
        
        # Ensure player stays on screen
        if self.rect.left < 0:
            self.rect.left = 0
            self.vel_x = 0
        if self.rect.bottom > SCREEN_HEIGHT:
            self.rect.bottom = SCREEN_HEIGHT
            self.vel_y = 0
            self.in_air = False
            
        # Update player's light source position
        for light in visual_effects.light_sources:
            if light['color'] == NEON_BLUE:  # Identify player's light
                light['x'] = self.rect.centerx
                light['y'] = self.rect.centery
                
        # Add motion trail particles
        if random.random() < 0.2:
            visual_effects.add_particle(
                self.rect.centerx, self.rect.centery,
                NEON_BLUE + (100,), random.randint(1, 3),
                0.5, random.randint(10, 20)
            )
            
        # Update animation frames
        self.frame_timer += 1
        if self.frame_timer > 5:
            self.frame_timer = 0
            if self.in_air:
                self.jumping_frame = (self.jumping_frame + 1) % 4
            else:
                self.running_frame = (self.running_frame + 1) % 6
                
        return dx

# Platform class
class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, platform_type=1):
        super().__init__()
        self.platform_type = platform_type
        self.width = width
        self.height = height
        
        # Create 3D platform with visual effects
        if platform_type == 1:
            color = NEON_BLUE
            highlight = (100, 220, 255)
            shadow = (0, 100, 150)
        elif platform_type == 2:
            color = NEON_PINK
            highlight = (255, 100, 200)
            shadow = (150, 0, 100)
        else:
            color = NEON_GREEN
            highlight = (150, 255, 150)
            shadow = (0, 150, 50)
            
        # Create 3D platform surface
        self.image = visual_effects.create_3d_platform(
            width, height, color, highlight, shadow, 10
        )
            
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        
        # Add light source to some platforms
        if random.random() < 0.3:
            visual_effects.add_light_source(
                x + width // 2, y + height // 2,
                70, color, 0.4
            )

# Star class (replacing traditional coins)
class Star(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        # Try to load star image, fall back to drawing if not available
        try:
            self.image = pygame.image.load(os.path.join('assets', 'star.png')).convert_alpha()
        except:
            # Create a star collectible
            self.image = pygame.Surface((32, 32), pygame.SRCALPHA)
            # Star shape
            points = [
                (16, 0), (20, 12), (32, 12), (22, 20),
                (26, 32), (16, 24), (6, 32), (10, 20),
                (0, 12), (12, 12)
            ]
            pygame.draw.polygon(self.image, NEON_YELLOW, points, 0)
        
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        
        # Animation variables
        self.float_offset = random.uniform(0, math.pi * 2)
        self.float_speed = random.uniform(0.05, 0.1)
        self.original_y = y
        self.angle = 0
        
        # Add light source to star
        visual_effects.add_light_source(x, y, 50, NEON_YELLOW, 0.5)

    def update(self):
        # Make star float up and down
        self.float_offset += self.float_speed
        self.rect.y = self.original_y + math.sin(self.float_offset) * 5
        
        # Rotate star
        self.angle = (self.angle + 1) % 360
        
        # Update star's light position
        for light in visual_effects.light_sources:
            if light['color'] == NEON_YELLOW and abs(light['x'] - self.rect.centerx) < 10:
                light['x'] = self.rect.centerx
                light['y'] = self.rect.centery

# World class to manage level
class World():
    def __init__(self):
        self.platform_list = pygame.sprite.Group()
        self.star_list = pygame.sprite.Group()
        self.score = 0
        
        # Parallax background layers
        self.bg_layers = []
        self.create_background_layers()
        
    def create_background_layers(self):
        # Create multiple background layers for parallax effect
        # Layer 1: Distant city skyline
        layer1 = pygame.Surface((SCREEN_WIDTH * 2, SCREEN_HEIGHT), pygame.SRCALPHA)
        for i in range(30):
            height = random.randint(50, 200)
            width = random.randint(30, 80)
            x = random.randint(0, int(SCREEN_WIDTH * 2) - width)
            y = SCREEN_HEIGHT - height
            color = (20, 20, 40)
            pygame.draw.rect(layer1, color, (x, y, width, height))
            
            # Add windows
            for _ in range(width // 10):
                wx = x + random.randint(5, width - 5)
                wy = y + random.randint(5, height - 5)
                wcolor = random.choice([NEON_BLUE, NEON_PINK, NEON_YELLOW, NEON_PURPLE])
                pygame.draw.rect(layer1, wcolor, (wx, wy, 3, 3))
        
        # Layer 2: Mid-distance buildings
        layer2 = pygame.Surface((int(SCREEN_WIDTH * 1.5), SCREEN_HEIGHT), pygame.SRCALPHA)
        for i in range(15):
            height = random.randint(100, 300)
            width = random.randint(50, 120)
            x = random.randint(0, int(SCREEN_WIDTH * 1.5) - width)
            y = SCREEN_HEIGHT - height
            color = (30, 30, 50)
            pygame.draw.rect(layer2, color, (x, y, width, height))
            
            # Add windows and details
            for _ in range(width // 8):
                wx = x + random.randint(5, width - 5)
                wy = y + random.randint(5, height - 5)
                wcolor = random.choice([NEON_BLUE, NEON_PINK, NEON_GREEN])
                pygame.draw.rect(layer2, wcolor, (wx, wy, 4, 4))
        
        # Layer 3: Foreground elements
        layer3 = pygame.Surface((int(SCREEN_WIDTH * 1.2), SCREEN_HEIGHT), pygame.SRCALPHA)
        for i in range(10):
            height = random.randint(50, 150)
            width = random.randint(20, 60)
            x = random.randint(0, int(SCREEN_WIDTH * 1.2) - width)
            y = SCREEN_HEIGHT - height
            color = (40, 40, 60)
            pygame.draw.rect(layer3, color, (x, y, width, height))
        
        self.bg_layers = [
            {"surface": layer1, "speed": 0.2},
            {"surface": layer2, "speed": 0.5},
            {"surface": layer3, "speed": 0.8}
        ]
        
    def draw(self, surface, camera_offset):
        # Draw background layers with parallax effect
        for layer in self.bg_layers:
            # Calculate parallax offset
            offset_x = camera_offset[0] * layer["speed"]
            # Draw the layer with offset
            surface.blit(layer["surface"], (-offset_x % layer["surface"].get_width() - layer["surface"].get_width(), 0))
            surface.blit(layer["surface"], (-offset_x % layer["surface"].get_width(), 0))
        
        # Draw grid lines for cyberpunk effect
        grid_offset_x = camera_offset[0] * 0.9
        grid_offset_y = camera_offset[1] * 0.9
        
        for x in range(0, SCREEN_WIDTH * 2, 50):
            x_pos = x - (grid_offset_x % 50)
            pygame.draw.line(surface, (20, 20, 40), (x_pos, 0), (x_pos, SCREEN_HEIGHT), 1)
            
        for y in range(0, SCREEN_HEIGHT * 2, 50):
            y_pos = y - (grid_offset_y % 50)
            pygame.draw.line(surface, (20, 20, 40), (0, y_pos), (SCREEN_WIDTH, y_pos), 1)
        
        # Draw platforms and stars with camera offset
        for platform in self.platform_list:
            surface.blit(platform.image, (platform.rect.x - camera_offset[0], platform.rect.y - camera_offset[1]))
            
        for star in self.star_list:
            # Apply rotation to star
            rotated_image = pygame.transform.rotate(star.image, star.angle)
            # Get the rect of the rotated image and set its center to the star's center
            rotated_rect = rotated_image.get_rect(center=star.rect.center)
            surface.blit(rotated_image, (rotated_rect.x - camera_offset[0], rotated_rect.y - camera_offset[1]))
        
    def update(self, scroll, camera_offset):
        # Update platform positions
        for platform in self.platform_list:
            platform.rect.x -= scroll
            # Remove platforms that have gone off screen
            if platform.rect.right < -100:
                # Remove associated light sources
                for i in range(len(visual_effects.light_sources) - 1, -1, -1):
                    light = visual_effects.light_sources[i]
                    if abs(light['x'] - platform.rect.centerx) < platform.width and abs(light['y'] - platform.rect.centery) < platform.height:
                        visual_effects.light_sources.pop(i)
                platform.kill()
                
        # Update star positions and animations
        for star in self.star_list:
            star.rect.x -= scroll
            star.update()
            # Remove stars that have gone off screen
            if star.rect.right < -100:
                # Remove associated light sources
                for i in range(len(visual_effects.light_sources) - 1, -1, -1):
                    light = visual_effects.light_sources[i]
                    if light['color'] == NEON_YELLOW and abs(light['x'] - star.rect.centerx) < 30:
                        visual_effects.light_sources.pop(i)
                star.kill()

# Function to generate platforms
def generate_platforms(world, start_x, width=100):
    # Create a platform at the given x position
    y = random.randint(SCREEN_HEIGHT // 2, SCREEN_HEIGHT - 100)
    platform_type = random.randint(1, 3)
    platform = Platform(start_x, y, width, 20, platform_type)
    world.platform_list.add(platform)
    
    # Randomly add a star above the platform
    if random.random() < 0.7:  # 70% chance to spawn a star
        star = Star(start_x + width // 2, y - 50)
        world.star_list.add(star)
    
    return platform

# Main game function
def main():
    # Create placeholder sounds if needed
    sound_files = sound_manager.create_placeholder_sounds()
    
    # Load sounds
    sound_manager.load_sound('jump', os.path.join('assets', 'sounds', 'jump.wav'))
    sound_manager.load_sound('collect', os.path.join('assets', 'sounds', 'collect.wav'))
    sound_manager.load_sound('land', os.path.join('assets', 'sounds', 'land.wav'))
    
    # Create player
    player = Player(100, SCREEN_HEIGHT - 150)
    player_group = pygame.sprite.Group()
    player_group.add(player)
    
    # Create world
    world = World()
    
    # Create initial platforms
    for i in range(10):
        if i == 0:
            # First platform is longer for starting area
            platform = generate_platforms(world, i * 200, 200)
        else:
            platform = generate_platforms(world, i * 200)
    
    # Game variables
    scroll = 0
    camera_offset = [0, 0]
    game_over = False
    score = 0
    font = pygame.font.SysFont('Arial', 30)
    
    # Main game loop
    running = True
    while running:
        clock.tick(FPS)
        
        # Clear screen
        screen.fill(BLACK)
        
        # Update camera to follow player
        camera.update(player)
        camera_offset = [-camera.camera.x, -camera.camera.y]
        
        # Draw world with camera offset
        world.draw(screen, camera_offset)
        
        # Update visual effects
        visual_effects.update_particles()
        
        # Draw shadows
        visual_effects.draw_shadows(screen, camera_offset)
        
        # Draw player with camera offset
        screen.blit(player.image, (player.rect.x - camera_offset[0], player.rect.y - camera_offset[1]))
        
        # Draw particles
        visual_effects.draw_particles(screen, camera_offset)
        
        # Apply lighting effects
        visual_effects.apply_lighting(screen)
        
        # Update player
        dx = player.update(world.platform_list)
        
        # Check if player has collected any stars
        hits = pygame.sprite.spritecollide(player, world.star_list, True)
        for hit in hits:
            score += 1
            # Play collect sound
            sound_manager.play_sound('collect', 0.5)
            
            # Add collection particles
            for _ in range(15):
                visual_effects.add_particle(
                    hit.rect.centerx, hit.rect.centery,
                    NEON_YELLOW, random.randint(2, 5),
                    random.uniform(1, 3), random.randint(20, 40)
                )
                
            # Remove the star's light source
            for i in range(len(visual_effects.light_sources) - 1, -1, -1):
                light = visual_effects.light_sources[i]
                if light['color'] == NEON_YELLOW and abs(light['x'] - hit.rect.centerx) < 30:
                    visual_effects.light_sources.pop(i)
        
        # Display score with glow effect
        score_text = font.render(f'Stars: {score}', True, NEON_YELLOW)
        # Add glow
        glow_surface = pygame.Surface((score_text.get_width() + 10, score_text.get_height() + 10), pygame.SRCALPHA)
        glow_rect = glow_surface.get_rect()
        for i in range(5, 0, -1):
            alpha = 50 - i * 10
            pygame.draw.rect(glow_surface, (*NEON_YELLOW, alpha), 
                            glow_rect.inflate(-i*2, -i*2), border_radius=3)
        screen.blit(glow_surface, (15, 15))
        screen.blit(score_text, (20, 20))
        
        # Update world with scroll
        if player.rect.right > SCREEN_WIDTH - SCROLL_THRESHOLD:
            scroll = player.rect.right - (SCREEN_WIDTH - SCROLL_THRESHOLD)
        else:
            scroll = 0
            
        world.update(scroll, camera_offset)
        
        # Generate new platforms as player moves right
        if len(world.platform_list) < 10:
            if world.platform_list:
                last_platform = max([p.rect.right for p in world.platform_list])
                gap = random.randint(50, 200)
                width = random.randint(80, 150)
                generate_platforms(world, last_platform + gap, width)
            else:
                # If no platforms exist, create one at a default position
                generate_platforms(world, SCREEN_WIDTH // 2, 200)
        
        # Event handling
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    running = False
        
        pygame.display.update()
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
