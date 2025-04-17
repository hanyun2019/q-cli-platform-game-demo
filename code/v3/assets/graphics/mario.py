"""
Simple ASCII art representation of Mario sprites
This is used to generate simple sprite images for the game
"""

MARIO_STANDING = """
  RRRR  
 RRRRRR 
 YYBrBr 
YYYBrBrY
YYBrBrBr
 BrBrBr 
  RRRRR 
 RRRBBB 
"""

MARIO_WALKING = """
  RRRR  
 RRRRRR 
 YYBrBr 
YYYBrBrY
YYBrBrBr
 BrBrBr 
RRRRRR  
 BBB    
"""

MARIO_JUMPING = """
  RRRR  
 RRRRRR 
 YYBrBr 
YYYBrBrY
YYBrBrBr
 BrRRRR 
  RRRRRR
   BBB  
"""

# Color mapping
COLOR_MAP = {
    'R': (255, 0, 0),    # Red
    'Y': (255, 255, 0),  # Yellow
    'B': (0, 0, 255),    # Blue
    'Br': (165, 42, 42), # Brown
    ' ': None            # Transparent
}
