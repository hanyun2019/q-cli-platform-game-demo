"""
Simple ASCII art representation of enemy sprites
This is used to generate simple sprite images for the game
"""

GOOMBA = """
   BBB   
  BBBBB  
 BBBBBBB 
BrBrBrBrBr
BrBrWWWBrBr
BrWWBrWWBr
 BrBrBrBr 
  BrBrBr  
"""

KOOPA = """
   GG   
  GGGG  
 GGGGGG 
GGGGGGGG
GGWWWWGG
GWWGGWWG
 GGGGGG 
  YYYY  
"""

# Color mapping
COLOR_MAP = {
    'B': (0, 0, 255),    # Blue
    'Br': (165, 42, 42), # Brown
    'W': (255, 255, 255),# White
    'G': (0, 255, 0),    # Green
    'Y': (255, 255, 0),  # Yellow
    ' ': None            # Transparent
}
