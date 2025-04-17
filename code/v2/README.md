# Cyberpunk Platform Game (Enhanced Version)

A classic platform game with a post-industrial cyberpunk aesthetic, built using Pygame, now with enhanced 3D visual effects, sound effects, and a scrolling camera system.

## Features

- Enhanced 3D visual effects:
  - 3D platforms with depth and shading
  - Dynamic lighting system with glowing effects
  - Particle effects for movement, jumping, and collecting
  - Parallax scrolling background with multiple layers
  - Shadows and visual depth

- Sound effects:
  - Jump sounds
  - Collection sounds
  - Landing sounds

- Advanced camera system:
  - Smooth camera tracking
  - Parallax scrolling for depth perception
  - Camera follows player movement

- Gameplay features:
  - Cyberpunk-themed platforms with neon colors and circuit patterns
  - Animated stars as collectibles
  - Procedurally generated level that extends as you play
  - Improved physics with momentum and friction
  - Visual feedback for all player actions

## Requirements

- Python 3.x
- Pygame library

## Installation

1. Make sure you have Python installed
2. Create a virtual environment (recommended):
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install Pygame:
   ```
   pip install pygame
   ```

## How to Play

Run the game with:
```
python main.py
```

### Controls
- Left/Right Arrow Keys: Move left/right
- Space: Jump
- Escape: Quit the game

## Game Mechanics

- Collect stars to increase your score
- The level generates infinitely as you move right
- Platforms have different colors and 3D effects
- The background features a cyberpunk city skyline with parallax scrolling
- Dynamic lighting creates an immersive atmosphere

## Code Structure

The game is now organized into multiple modules:
- `main.py` - Main game loop and core gameplay
- `camera.py` - Camera tracking system
- `sound_manager.py` - Sound effect handling
- `visual_effects.py` - 3D effects, particles, and lighting

## Customization

You can customize the game by:
- Modifying the constants at the top of the main.py file
- Adding your own sprites in the assets folder
- Adding custom sound effects in the assets/sounds folder
- Adjusting visual effects parameters in visual_effects.py
