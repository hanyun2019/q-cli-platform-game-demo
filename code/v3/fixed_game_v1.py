"""
Fixed Platform Game with Replay Feature
This is a simplified version that works without requiring external assets
"""
import pygame
import sys
import os
import time
import copy
import random  # Added for enemy movement randomization
import math    # Added for sound generation

# Initialize pygame
pygame.init()
pygame.mixer.init()  # Initialize sound mixer

# Screen settings
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
TILE_SIZE = 32

# Colors
SKY_COLOR = (93, 148, 251)
GROUND_COLOR = (88, 36, 9)
MARIO_COLOR = (255, 0, 0)
ENEMY_COLOR = (0, 0, 255)
STAR_COLOR = (255, 215, 0)
TEXT_COLOR = (255, 255, 255)
BUTTON_COLOR = (45, 91, 123)
BUTTON_HOVER_COLOR = (62, 123, 167)

# Sound effects
jump_sound = None
star_sound = None
enemy_defeat_sound = None
game_over_sound = None
level_complete_sound = None

def load_sounds():
    global jump_sound, star_sound, enemy_defeat_sound, game_over_sound, level_complete_sound
    
    # Create simple sound effects using sine waves
    sample_rate = 44100
    
    # Jump sound - rising tone
    jump_buffer = bytearray()
    for i in range(int(0.2 * sample_rate)):  # 0.2 seconds
        t = i / sample_rate
        freq = 440 + (i / (0.2 * sample_rate)) * 220  # Rising from 440Hz to 660Hz
        sample = int(32767 * 0.5 * math.sin(2 * math.pi * freq * t))
        # Convert to 16-bit little-endian bytes
        jump_buffer.extend(sample.to_bytes(2, byteorder='little', signed=True))
    jump_sound = pygame.mixer.Sound(buffer=bytes(jump_buffer))
    
    # Star sound - high ping with shimmer
    star_buffer = bytearray()
    for i in range(int(0.2 * sample_rate)):  # 0.2 seconds
        t = i / sample_rate
        # Base frequency with shimmer effect
        freq = 988 + 100 * math.sin(2 * math.pi * 10 * t)
        sample = int(32767 * 0.5 * math.sin(2 * math.pi * freq * t))
        star_buffer.extend(sample.to_bytes(2, byteorder='little', signed=True))
    star_sound = pygame.mixer.Sound(buffer=bytes(star_buffer))
    
    # Enemy defeat sound - descending tone
    enemy_buffer = bytearray()
    for i in range(int(0.3 * sample_rate)):  # 0.3 seconds
        t = i / sample_rate
        freq = 660 - (i / (0.3 * sample_rate)) * 440  # Descending from 660Hz to 220Hz
        sample = int(32767 * 0.5 * math.sin(2 * math.pi * freq * t))
        enemy_buffer.extend(sample.to_bytes(2, byteorder='little', signed=True))
    enemy_defeat_sound = pygame.mixer.Sound(buffer=bytes(enemy_buffer))
    
    # Game over sound - descending tones
    game_over_buffer = bytearray()
    freqs = [440, 349, 329, 220]
    for freq in freqs:
        for i in range(int(0.15 * sample_rate)):  # 0.15 seconds per note
            t = i / sample_rate
            sample = int(32767 * 0.5 * math.sin(2 * math.pi * freq * t))
            game_over_buffer.extend(sample.to_bytes(2, byteorder='little', signed=True))
    game_over_sound = pygame.mixer.Sound(buffer=bytes(game_over_buffer))
    
    # Level complete sound - ascending tones
    level_buffer = bytearray()
    freqs = [523, 659, 784, 1047]
    for freq in freqs:
        for i in range(int(0.15 * sample_rate)):  # 0.15 seconds per note
            t = i / sample_rate
            sample = int(32767 * 0.5 * math.sin(2 * math.pi * freq * t))
            level_buffer.extend(sample.to_bytes(2, byteorder='little', signed=True))
    level_complete_sound = pygame.mixer.Sound(buffer=bytes(level_buffer))

# Load sounds
load_sounds()

def load_mario_sprite():
    """Create a simple Mario-like sprite"""
    surface = pygame.Surface((32, 32), pygame.SRCALPHA)
    
    # Red hat and shirt
    pygame.draw.rect(surface, (255, 0, 0), (0, 0, 32, 10))
    pygame.draw.rect(surface, (255, 0, 0), (8, 18, 16, 14))
    
    # Blue overalls
    pygame.draw.rect(surface, (0, 0, 255), (8, 10, 16, 8))
    pygame.draw.rect(surface, (0, 0, 255), (4, 18, 4, 14))
    pygame.draw.rect(surface, (0, 0, 255), (24, 18, 4, 14))
    
    # Face
    pygame.draw.rect(surface, (255, 200, 150), (8, 10, 16, 8))
    
    # Eyes
    pygame.draw.rect(surface, (255, 255, 255), (10, 12, 4, 4))
    pygame.draw.rect(surface, (255, 255, 255), (18, 12, 4, 4))
    pygame.draw.rect(surface, (0, 0, 0), (12, 14, 2, 2))
    pygame.draw.rect(surface, (0, 0, 0), (20, 14, 2, 2))
    
    return surface

def load_enemy_sprite():
    """Create a simple Goomba-like sprite"""
    surface = pygame.Surface((32, 32), pygame.SRCALPHA)
    
    # Brown body
    pygame.draw.rect(surface, (165, 42, 42), (4, 16, 24, 16))
    
    # White eyes
    pygame.draw.rect(surface, (255, 255, 255), (8, 20, 6, 6))
    pygame.draw.rect(surface, (255, 255, 255), (18, 20, 6, 6))
    
    # Black pupils
    pygame.draw.rect(surface, (0, 0, 0), (10, 22, 2, 2))
    pygame.draw.rect(surface, (0, 0, 0), (20, 22, 2, 2))
    
    # Feet
    pygame.draw.rect(surface, (0, 0, 0), (4, 28, 8, 4))
    pygame.draw.rect(surface, (0, 0, 0), (20, 28, 8, 4))
    
    return surface

def load_coin_sprite():
    """Create a simple star sprite instead of a coin"""
    surface = pygame.Surface((16, 16), pygame.SRCALPHA)
    
    # Star shape
    points = []
    for i in range(5):
        # Outer point
        angle_outer = math.pi/2 + i * 2*math.pi/5
        x_outer = 8 + 7 * math.cos(angle_outer)
        y_outer = 8 + 7 * math.sin(angle_outer)
        points.append((x_outer, y_outer))
        
        # Inner point
        angle_inner = angle_outer + math.pi/5
        x_inner = 8 + 3 * math.cos(angle_inner)
        y_inner = 8 + 3 * math.sin(angle_inner)
        points.append((x_inner, y_inner))
    
    # Draw the star
    pygame.draw.polygon(surface, (255, 215, 0), points)  # Gold star
    
    return surface

# Game settings
GRAVITY = 0.5
JUMP_STRENGTH = -12  # Adjusted from -15 to -12 for more controlled jumps
PLAYER_SPEED = 5

# Create screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Platform Game - Fixed Version')
clock = pygame.time.Clock()

# Font
font = pygame.font.SysFont('Arial', 24)
title_font = pygame.font.SysFont('Arial', 48)

# Player
class Player:
    def __init__(self):
        self.rect = pygame.Rect(100, SCREEN_HEIGHT - 100, 32, 32)
        self.velocity = pygame.Vector2(0, 0)
        self.on_ground = False
        self.score = 0
        self.coins = 0
        self.sprite = load_mario_sprite()
        self.facing_right = True
        
    def update(self, platforms):
        # Apply gravity
        self.velocity.y += GRAVITY
        
        # Limit falling speed to prevent passing through platforms
        if self.velocity.y > 15:
            self.velocity.y = 15
        
        # Move horizontally
        self.rect.x += self.velocity.x
        
        # Update facing direction
        if self.velocity.x > 0:
            self.facing_right = True
        elif self.velocity.x < 0:
            self.facing_right = False
        
        # Check horizontal collisions
        for platform in platforms:
            if self.rect.colliderect(platform):
                if self.velocity.x > 0:  # Moving right
                    self.rect.right = platform.left
                elif self.velocity.x < 0:  # Moving left
                    self.rect.left = platform.right
        
        # Move vertically
        self.rect.y += self.velocity.y
        self.on_ground = False
        
        # Check vertical collisions
        for platform in platforms:
            if self.rect.colliderect(platform):
                if self.velocity.y > 0:  # Moving down
                    self.rect.bottom = platform.top
                    self.on_ground = True
                    self.velocity.y = 0
                elif self.velocity.y < 0:  # Moving up
                    self.rect.top = platform.bottom
                    self.velocity.y = 0
        
        # Keep player on screen
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH
        if self.rect.top < 0:
            self.rect.top = 0
        
        # Check if player fell off the screen
        if self.rect.top > SCREEN_HEIGHT:
            self.rect.x = 100
            self.rect.y = SCREEN_HEIGHT - 100
            self.velocity = pygame.Vector2(0, 0)
            
    def jump(self):
        if self.on_ground:
            self.velocity.y = JUMP_STRENGTH
            # Play jump sound
            if jump_sound:
                jump_sound.play()
            
    def draw(self):
        # Draw the sprite instead of a rectangle
        if self.facing_right:
            screen.blit(self.sprite, self.rect)
        else:
            # Flip the sprite if facing left
            flipped_sprite = pygame.transform.flip(self.sprite, True, False)
            screen.blit(flipped_sprite, self.rect)

# Enemy
class Enemy:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 32, 32)
        self.velocity = pygame.Vector2(-2, 0)
        self.initial_x = x
        self.initial_y = y
        self.direction_change_timer = 0
        self.sprite = load_enemy_sprite()
        self.direction_change_timer = 0
        
    def update(self, platforms):
        # Move horizontally
        self.rect.x += self.velocity.x
        
        # Check for collisions or edges
        collision = False
        for platform in platforms:
            if self.rect.colliderect(platform):
                self.velocity.x *= -1
                collision = True
                break
                
        if self.rect.left < 0 or self.rect.right > SCREEN_WIDTH:
            self.velocity.x *= -1
            
        # Occasionally change direction to make movement less predictable
        self.direction_change_timer += 1
        if self.direction_change_timer > 180:  # Change direction every ~3 seconds
            if random.random() < 0.3:  # 30% chance to change direction
                self.velocity.x *= -1
            self.direction_change_timer = 0
            
    def draw(self):
        # Draw the sprite instead of a rectangle
        if self.velocity.x > 0:
            # Flip sprite if moving right
            flipped_sprite = pygame.transform.flip(self.sprite, True, False)
            screen.blit(flipped_sprite, self.rect)
        else:
            screen.blit(self.sprite, self.rect)
        
    def reset(self):
        self.rect.x = self.initial_x
        self.rect.y = self.initial_y
        self.velocity = pygame.Vector2(-2, 0)

# Coin (now a star)
class Coin:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 16, 16)
        self.collected = False
        self.x = x
        self.y = y
        self.sprite = load_coin_sprite()
        self.bob_offset = 0
        self.bob_direction = 1
        self.bob_speed = 0.2
        self.rotation = 0  # Add rotation for the star
        self.rotation_speed = 2  # Degrees per frame
    def update(self):
        if not self.collected:
            # Make the star bob up and down
            self.bob_offset += self.bob_speed * self.bob_direction
            if abs(self.bob_offset) > 3:
                self.bob_direction *= -1
            
            # Update the rect position with the bob offset
            self.rect.y = self.y + self.bob_offset
            
            # Rotate the star
            self.rotation = (self.rotation + self.rotation_speed) % 360
        
    def draw(self):
        if not self.collected:
            # Rotate the sprite
            rotated_sprite = pygame.transform.rotate(self.sprite, self.rotation)
            # Get the rect of the rotated sprite to center it
            rect = rotated_sprite.get_rect(center=self.rect.center)
            screen.blit(rotated_sprite, rect)
            
    def reset(self):
        self.collected = False
        self.bob_offset = 0
        self.bob_direction = 1

# Game state for replay
class GameState:
    def __init__(self, player_pos, player_vel, enemy_positions, enemy_velocities, coin_states):
        self.player_pos = player_pos
        self.player_vel = player_vel
        self.enemy_positions = enemy_positions
        self.enemy_velocities = enemy_velocities
        self.coin_states = coin_states

# Game
class Game:
    def __init__(self):
        self.state = 'menu'  # menu, playing, game_over, win, replay
        self.player = Player()
        self.platforms = []
        self.enemies = []
        self.coins = []
        self.current_level = 1
        self.max_levels = 3
        self.setup_level(self.current_level)
        
        # Replay system
        self.recording = False
        self.replay_states = []
        self.replay_index = 0
        self.replay_speed = 1.0
        
    def setup_level(self, level_number=1):
        # Clear existing objects
        self.platforms = []
        self.enemies = []
        self.coins = []
        
        # Ground
        self.platforms.append(pygame.Rect(0, SCREEN_HEIGHT - 40, SCREEN_WIDTH, 40))
        
        if level_number == 1:
            # Level 1 - Basic level
            # Platforms - adjusted heights to be more accessible
            self.platforms.append(pygame.Rect(200, SCREEN_HEIGHT - 120, 200, 20))
            self.platforms.append(pygame.Rect(500, SCREEN_HEIGHT - 180, 200, 20))  # Lowered from -200
            self.platforms.append(pygame.Rect(100, SCREEN_HEIGHT - 240, 200, 20))  # Lowered from -280
            self.platforms.append(pygame.Rect(400, SCREEN_HEIGHT - 300, 200, 20))  # Lowered from -350
            
            # Enemies
            self.enemies.append(Enemy(300, SCREEN_HEIGHT - 80))
            self.enemies.append(Enemy(600, SCREEN_HEIGHT - 220))  # Adjusted for new platform height
            
            # Stars
            for i in range(5):
                self.coins.append(Coin(250 + i*30, SCREEN_HEIGHT - 150))
            for i in range(5):
                self.coins.append(Coin(550 + i*30, SCREEN_HEIGHT - 210))  # Adjusted for new platform height
            for i in range(5):
                self.coins.append(Coin(150 + i*30, SCREEN_HEIGHT - 270))  # Adjusted for new platform height
                
        elif level_number == 2:
            # Level 2 - More platforms and enemies
            # Platforms - adjusted heights to be more accessible
            self.platforms.append(pygame.Rect(100, SCREEN_HEIGHT - 150, 150, 20))
            self.platforms.append(pygame.Rect(350, SCREEN_HEIGHT - 180, 150, 20))  # Lowered from -200
            self.platforms.append(pygame.Rect(600, SCREEN_HEIGHT - 150, 150, 20))
            self.platforms.append(pygame.Rect(200, SCREEN_HEIGHT - 250, 150, 20))  # Lowered from -300
            self.platforms.append(pygame.Rect(450, SCREEN_HEIGHT - 300, 150, 20))  # Lowered from -350
            
            # Enemies
            self.enemies.append(Enemy(150, SCREEN_HEIGHT - 190))
            self.enemies.append(Enemy(400, SCREEN_HEIGHT - 220))  # Adjusted for new platform height
            self.enemies.append(Enemy(650, SCREEN_HEIGHT - 190))
            self.enemies.append(Enemy(250, SCREEN_HEIGHT - 290))  # Adjusted for new platform height
            
            # Stars
            for i in range(3):
                self.coins.append(Coin(120 + i*30, SCREEN_HEIGHT - 180))
            for i in range(3):
                self.coins.append(Coin(370 + i*30, SCREEN_HEIGHT - 210))  # Adjusted for new platform height
            for i in range(3):
                self.coins.append(Coin(620 + i*30, SCREEN_HEIGHT - 180))
            for i in range(3):
                self.coins.append(Coin(220 + i*30, SCREEN_HEIGHT - 280))  # Adjusted for new platform height
            for i in range(3):
                self.coins.append(Coin(470 + i*30, SCREEN_HEIGHT - 330))  # Adjusted for new platform height
                
        elif level_number == 3:
            # Level 3 - Complex layout with more challenges
            # Platforms - stair-like structure with reduced height differences
            for i in range(6):
                self.platforms.append(pygame.Rect(100 + i*100, SCREEN_HEIGHT - 100 - i*30, 80, 20))  # Reduced from i*40
                
            # Platforms - descending structure with reduced height differences
            for i in range(6):
                self.platforms.append(pygame.Rect(700 - i*100, SCREEN_HEIGHT - 280 - i*15, 80, 20))  # Adjusted heights
                
            # Center platform
            self.platforms.append(pygame.Rect(300, SCREEN_HEIGHT - 220, 200, 20))  # Lowered from -250
            
            # Enemies
            self.enemies.append(Enemy(150, SCREEN_HEIGHT - 140))
            self.enemies.append(Enemy(350, SCREEN_HEIGHT - 140))
            self.enemies.append(Enemy(550, SCREEN_HEIGHT - 140))
            self.enemies.append(Enemy(250, SCREEN_HEIGHT - 260))  # Adjusted for new platform height
            self.enemies.append(Enemy(450, SCREEN_HEIGHT - 260))  # Adjusted for new platform height
            self.enemies.append(Enemy(400, SCREEN_HEIGHT - 350))  # Adjusted height
            
            # Stars
            for i in range(20):
                x = 100 + (i % 5) * 150
                y = SCREEN_HEIGHT - 180 - (i // 5) * 60  # Adjusted from -200 and *80 to make more accessible
                self.coins.append(Coin(x, y))
    
    def start_recording(self):
        """Start recording gameplay for replay"""
        self.recording = True
        self.replay_states = []
        print("Recording started")
        
    def stop_recording(self):
        """Stop recording gameplay"""
        self.recording = False
        print(f"Recording stopped. Captured {len(self.replay_states)} frames")
        
    def record_state(self):
        """Record current game state for replay"""
        if not self.recording:
            return
            
        # Record player state
        player_pos = (self.player.rect.x, self.player.rect.y)
        player_vel = (self.player.velocity.x, self.player.velocity.y)
        
        # Record enemy states
        enemy_positions = []
        enemy_velocities = []
        for enemy in self.enemies:
            enemy_positions.append((enemy.rect.x, enemy.rect.y))
            enemy_velocities.append(enemy.velocity.x)
            
        # Record coin states
        coin_states = []
        for coin in self.coins:
            coin_states.append(coin.collected)
            
        # Create game state and add to replay
        game_state = GameState(player_pos, player_vel, enemy_positions, enemy_velocities, coin_states)
        self.replay_states.append(game_state)
        
    def start_replay(self):
        """Start replaying recorded gameplay"""
        if len(self.replay_states) == 0:
            print("No replay data available")
            return False
            
        self.state = 'replay'
        self.replay_index = 0
        self.replay_speed = 1.0
        print("Starting replay")
        return True
        
    def update_replay(self):
        """Update game state based on replay data"""
        if self.replay_index >= len(self.replay_states):
            print("Replay finished")
            self.state = 'menu'
            return
            
        # Get current replay frame
        frame = self.replay_states[self.replay_index]
        
        # Update player
        self.player.rect.x, self.player.rect.y = frame.player_pos
        self.player.velocity.x, self.player.velocity.y = frame.player_vel
        
        # Update enemies
        for i, enemy in enumerate(self.enemies):
            if i < len(frame.enemy_positions):
                enemy.rect.x, enemy.rect.y = frame.enemy_positions[i]
                enemy.velocity.x = frame.enemy_velocities[i]
                
        # Update coins
        for i, coin in enumerate(self.coins):
            if i < len(frame.coin_states):
                coin.collected = frame.coin_states[i]
                
        # Advance replay index based on speed
        self.replay_index += int(self.replay_speed)
        if self.replay_index >= len(self.replay_states):
            self.replay_index = len(self.replay_states) - 1
        
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
                
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.state == 'playing':
                        if self.recording:
                            self.stop_recording()
                        self.state = 'menu'
                    elif self.state == 'replay':
                        self.state = 'menu'
                    else:
                        pygame.quit()
                        sys.exit()
                        
                if event.key == pygame.K_SPACE:
                    if self.state == 'menu':
                        self.state = 'playing'
                        self.player = Player()
                        self.current_level = 1
                        self.setup_level(self.current_level)
                        self.start_recording()
                    elif self.state == 'game_over':
                        self.state = 'menu'
                    elif self.state == 'win':
                        # Check if there are more levels
                        if self.current_level < self.max_levels:
                            self.current_level += 1
                            self.state = 'playing'
                            self.player = Player()
                            self.setup_level(self.current_level)
                            self.start_recording()
                        else:
                            # Game completed
                            self.state = 'menu'
                    elif self.state == 'playing':
                        self.player.jump()
                
                # Replay controls
                if self.state == 'replay':
                    if event.key == pygame.K_r:  # Reset replay
                        self.replay_index = 0
                    if event.key == pygame.K_UP:  # Speed up
                        self.replay_speed = min(4.0, self.replay_speed * 2)
                        print(f"Replay speed: {self.replay_speed}x")
                    if event.key == pygame.K_DOWN:  # Slow down
                        self.replay_speed = max(0.25, self.replay_speed / 2)
                        print(f"Replay speed: {self.replay_speed}x")
                
                # Watch replay from game over or win screen
                if event.key == pygame.K_r:
                    if self.state == 'game_over' or self.state == 'win':
                        if len(self.replay_states) > 0:
                            self.start_replay()
                        
            # Handle mouse clicks
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left mouse button
                    mouse_pos = pygame.mouse.get_pos()
                    
                    # Check if in menu state
                    if self.state == 'menu':
                        # Check if play button was clicked
                        play_button_rect = pygame.Rect(SCREEN_WIDTH/2 - 100, 300, 200, 50)
                        if play_button_rect.collidepoint(mouse_pos):
                            self.state = 'playing'
                            self.player = Player()
                            self.current_level = 1
                            self.setup_level(self.current_level)
                            self.start_recording()
                            
                        # Check if replay button was clicked (if available)
                        if len(self.replay_states) > 0:
                            replay_button_rect = pygame.Rect(SCREEN_WIDTH/2 - 100, 370, 200, 50)
                            if replay_button_rect.collidepoint(mouse_pos):
                                self.start_replay()
        
        # Handle continuous key presses for movement - only in playing state
        keys = pygame.key.get_pressed()
        if self.state == 'playing':
            self.player.velocity.x = 0
            if keys[pygame.K_LEFT]:
                self.player.velocity.x = -PLAYER_SPEED
            if keys[pygame.K_RIGHT]:
                self.player.velocity.x = PLAYER_SPEED
                
    def update(self):
        if self.state == 'playing':
            self.player.update(self.platforms)
            
            # Create a copy of enemies list to safely remove during iteration
            enemies_to_remove = []
            
            # Update enemies
            for enemy in self.enemies:
                enemy.update(self.platforms)
                
                # Check if player jumps on enemy
                if self.player.rect.colliderect(enemy.rect):
                    # Improved collision detection for jumping on enemies
                    # Check if player is falling down and is mostly above the enemy
                    if (self.player.velocity.y > 0 and 
                        self.player.rect.bottom < enemy.rect.top + 15 and
                        self.player.rect.bottom > enemy.rect.top - 10):
                        # Mark enemy for removal instead of removing immediately
                        enemies_to_remove.append(enemy)
                        self.player.velocity.y = JUMP_STRENGTH / 2
                        self.player.score += 100
                        # Play enemy defeat sound
                        if enemy_defeat_sound:
                            enemy_defeat_sound.play()
                    else:
                        # Game over but don't freeze
                        print("Game over - collision with enemy")
                        self.state = 'game_over'
                        # Play game over sound
                        if game_over_sound:
                            game_over_sound.play()
                        if self.recording:
                            self.stop_recording()
            
            # Remove enemies after iteration is complete
            for enemy in enemies_to_remove:
                if enemy in self.enemies:
                    self.enemies.remove(enemy)
            
            # Check coin collisions
            for coin in self.coins:
                if not coin.collected and self.player.rect.colliderect(coin.rect):
                    coin.collected = True
                    self.player.coins += 1
                    self.player.score += 50
                    # Play star sound
                    if star_sound:
                        star_sound.play()
                    
            # Check if all coins collected
            if all(coin.collected for coin in self.coins) and not self.enemies:
                self.state = 'win'
                # Play level complete sound
                if level_complete_sound:
                    level_complete_sound.play()
                self.stop_recording()
                
            # Record current state for replay
            self.record_state()
                
        elif self.state == 'replay':
            self.update_replay()
                
    def draw(self):
        screen.fill(SKY_COLOR)
        
        if self.state == 'menu':
            # Draw title
            title_text = title_font.render('PLATFORM GAME', True, TEXT_COLOR)
            screen.blit(title_text, (SCREEN_WIDTH/2 - title_text.get_width()/2, 100))
            
            # Draw play button
            button_rect = pygame.Rect(SCREEN_WIDTH/2 - 100, 300, 200, 50)
            mouse_pos = pygame.mouse.get_pos()
            button_color = BUTTON_HOVER_COLOR if button_rect.collidepoint(mouse_pos) else BUTTON_COLOR
            pygame.draw.rect(screen, button_color, button_rect)
            pygame.draw.rect(screen, TEXT_COLOR, button_rect, 2)
            
            # Button text
            button_text = font.render('PLAY GAME', True, TEXT_COLOR)
            screen.blit(button_text, (button_rect.centerx - button_text.get_width()/2, 
                                     button_rect.centery - button_text.get_height()/2))
            
            # Instructions
            inst_text = font.render('Arrow Keys: Move, Space: Jump', True, TEXT_COLOR)
            screen.blit(inst_text, (SCREEN_WIDTH/2 - inst_text.get_width()/2, 400))
            
            # Replay button (if replay data exists)
            if len(self.replay_states) > 0:
                replay_rect = pygame.Rect(SCREEN_WIDTH/2 - 100, 370, 200, 50)
                replay_color = BUTTON_HOVER_COLOR if replay_rect.collidepoint(mouse_pos) else BUTTON_COLOR
                pygame.draw.rect(screen, replay_color, replay_rect)
                pygame.draw.rect(screen, TEXT_COLOR, replay_rect, 2)
                
                replay_text = font.render('WATCH REPLAY', True, TEXT_COLOR)
                screen.blit(replay_text, (replay_rect.centerx - replay_text.get_width()/2, 
                                         replay_rect.centery - replay_text.get_height()/2))
            
        elif self.state == 'playing' or self.state == 'game_over' or self.state == 'win' or self.state == 'replay':
            # Draw platforms
            for platform in self.platforms:
                pygame.draw.rect(screen, GROUND_COLOR, platform)
                
            # Draw coins
            for coin in self.coins:
                coin.draw()
                
            # Draw enemies
            for enemy in self.enemies:
                enemy.draw()
                
            # Draw player
            self.player.draw()
            
            # Draw HUD
            score_text = font.render(f'Score: {self.player.score}', True, TEXT_COLOR)
            screen.blit(score_text, (20, 20))
            
            stars_text = font.render(f'Stars: {self.player.coins}', True, TEXT_COLOR)
            screen.blit(stars_text, (20, 50))
            
            # Replay indicator
            if self.state == 'replay':
                replay_text = font.render(f'REPLAY {self.replay_index}/{len(self.replay_states)} ({self.replay_speed}x)', True, TEXT_COLOR)
                screen.blit(replay_text, (SCREEN_WIDTH - replay_text.get_width() - 20, 20))
                
                # Replay controls help
                controls_text = font.render('R: Restart, Up/Down: Speed, ESC: Exit', True, TEXT_COLOR)
                screen.blit(controls_text, (SCREEN_WIDTH - controls_text.get_width() - 20, 50))
            
            if self.state == 'game_over':
                # Game over overlay
                overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 128))
                screen.blit(overlay, (0, 0))
                
                # Game over text
                game_over_text = title_font.render('GAME OVER', True, TEXT_COLOR)
                screen.blit(game_over_text, (SCREEN_WIDTH/2 - game_over_text.get_width()/2, 200))
                
                # Restart text
                restart_text = font.render('Press SPACE to continue', True, TEXT_COLOR)
                screen.blit(restart_text, (SCREEN_WIDTH/2 - restart_text.get_width()/2, 300))
                
                # Replay text
                replay_text = font.render('Press R to watch replay', True, TEXT_COLOR)
                screen.blit(replay_text, (SCREEN_WIDTH/2 - replay_text.get_width()/2, 340))
                
            if self.state == 'win':
                # Win overlay
                overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 128))
                screen.blit(overlay, (0, 0))
                
                # Win text
                if self.current_level < self.max_levels:
                    win_text = title_font.render(f'LEVEL {self.current_level} COMPLETE!', True, TEXT_COLOR)
                else:
                    win_text = title_font.render('YOU COMPLETED THE GAME!', True, TEXT_COLOR)
                screen.blit(win_text, (SCREEN_WIDTH/2 - win_text.get_width()/2, 200))
                
                # Score text
                final_score_text = font.render(f'Score: {self.player.score}', True, TEXT_COLOR)
                screen.blit(final_score_text, (SCREEN_WIDTH/2 - final_score_text.get_width()/2, 300))
                
                # Next level or continue text
                if self.current_level < self.max_levels:
                    next_text = font.render('Press SPACE for next level', True, TEXT_COLOR)
                else:
                    next_text = font.render('Press SPACE to continue', True, TEXT_COLOR)
                screen.blit(next_text, (SCREEN_WIDTH/2 - next_text.get_width()/2, 350))
                
                # Replay text
                replay_text = font.render('Press R to watch replay', True, TEXT_COLOR)
                screen.blit(replay_text, (SCREEN_WIDTH/2 - replay_text.get_width()/2, 390))
        
        # Debug info
        debug_text = font.render(f'Game State: {self.state} | Level: {self.current_level}/{self.max_levels}', True, (255, 0, 0))
        screen.blit(debug_text, (SCREEN_WIDTH - 350, SCREEN_HEIGHT - 30))
        
        pygame.display.update()
        
    def run(self):
        while True:
            self.handle_events()
            self.update()
            self.draw()
            clock.tick(60)

# Run the game
if __name__ == '__main__':
    game = Game()
    game.run()
