import pygame
import sys
import random
from pygame.locals import *

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

# Create the screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Cyberpunk Platform Game')

# Clock for controlling the frame rate
clock = pygame.time.Clock()

# Player class
class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
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
        self.jumped = False
        self.direction = 0
        self.in_air = True

    def update(self, platforms):
        dx = 0
        dy = 0
        
        # Get key presses
        key = pygame.key.get_pressed()
        if key[K_LEFT]:
            dx = -5
            self.direction = -1
        if key[K_RIGHT]:
            dx = 5
            self.direction = 1
        if key[K_SPACE] and not self.jumped and not self.in_air:
            self.vel_y = -15
            self.jumped = True
            self.in_air = True
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
        
        # Update player position
        self.rect.x += dx
        self.rect.y += dy
        
        # Ensure player stays on screen
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH
        if self.rect.bottom > SCREEN_HEIGHT:
            self.rect.bottom = SCREEN_HEIGHT
            self.vel_y = 0
            self.in_air = False
            
        return dx

# Platform class
class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, platform_type=1):
        super().__init__()
        self.image = pygame.Surface((width, height))
        self.platform_type = platform_type
        
        # Different platform types for cyberpunk aesthetic
        if platform_type == 1:
            self.image.fill(NEON_BLUE)
        elif platform_type == 2:
            self.image.fill(NEON_PINK)
        else:
            self.image.fill(NEON_GREEN)
            
        # Add some cyberpunk details
        pygame.draw.line(self.image, WHITE, (0, 0), (width, 0), 2)
        pygame.draw.line(self.image, WHITE, (0, height-1), (width, height-1), 1)
        
        # Add circuit-like patterns
        for _ in range(3):
            x1 = random.randint(5, width-5)
            pygame.draw.line(self.image, WHITE, (x1, 0), (x1, height), 1)
            
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

# Star class (replacing traditional coins)
class Star(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        # Create a star collectible
        self.image = pygame.Surface((32, 32), pygame.SRCALPHA)
        # Star shape
        points = [
            (16, 0), (20, 12), (32, 12), (22, 20),
            (26, 32), (16, 24), (6, 32), (10, 20),
            (0, 12), (12, 12)
        ]
        pygame.draw.polygon(self.image, (255, 255, 0), points, 0)
        
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

# World class to manage level
class World():
    def __init__(self):
        self.platform_list = pygame.sprite.Group()
        self.star_list = pygame.sprite.Group()
        self.score = 0
        
    def draw(self, surface):
        self.platform_list.draw(surface)
        self.star_list.draw(surface)
        
    def update(self, scroll):
        # Update platform positions
        for platform in self.platform_list:
            platform.rect.x -= scroll
            # Remove platforms that have gone off screen
            if platform.rect.right < 0:
                platform.kill()
                
        # Update star positions
        for star in self.star_list:
            star.rect.x -= scroll
            # Remove stars that have gone off screen
            if star.rect.right < 0:
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
    bg_scroll = 0
    game_over = False
    score = 0
    font = pygame.font.SysFont('Arial', 30)
    
    # Main game loop
    running = True
    while running:
        clock.tick(FPS)
        
        # Draw cyberpunk background
        screen.fill(BLACK)
        
        # Draw grid lines for cyberpunk effect
        for x in range(0, SCREEN_WIDTH, 50):
            pygame.draw.line(screen, (20, 20, 40), (x - bg_scroll % 50, 0), (x - bg_scroll % 50, SCREEN_HEIGHT), 1)
        for y in range(0, SCREEN_HEIGHT, 50):
            pygame.draw.line(screen, (20, 20, 40), (0, y), (SCREEN_WIDTH, y), 1)
        
        # Draw world
        world.draw(screen)
        
        # Draw player
        player_group.draw(screen)
        
        # Update player
        scroll = player.update(world.platform_list)
        
        # Check if player has collected any stars
        hits = pygame.sprite.spritecollide(player, world.star_list, True)
        for hit in hits:
            score += 1
        
        # Display score
        score_text = font.render(f'Stars: {score}', True, WHITE)
        screen.blit(score_text, (20, 20))
        
        # Update world with scroll
        world.update(scroll)
        
        # Generate new platforms as player moves right
        if len(world.platform_list) < 10:
            last_platform = max([p.rect.right for p in world.platform_list])
            gap = random.randint(50, 200)
            width = random.randint(80, 150)
            generate_platforms(world, last_platform + gap, width)
        
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
