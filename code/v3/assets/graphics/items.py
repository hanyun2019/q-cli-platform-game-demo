"""
Simple ASCII art representation of item sprites
This is used to generate simple sprite images for the game
"""

COIN = """
   YY   
  YYYY  
 YYYYYY 
YYYYYYYY
YYYYYYYY
 YYYYYY 
  YYYY  
   YY   
"""

BRICK = """
BBBBBBBB
BBBBBBBB
BBBBBBBB
BBBBBBBB
BBBBBBBB
BBBBBBBB
BBBBBBBB
BBBBBBBB
"""

QUESTION_BLOCK = """
YYYYYYYY
YOOOOOY
YOOOOOY
YOOQOOY
YOOOOOY
YOOOOOY
YOOOOOY
YYYYYYYY
"""

# Color mapping
COLOR_MAP = {
    'Y': (255, 255, 0),  # Yellow
    'B': (165, 42, 42),  # Brown (brick color)
    'O': (255, 165, 0),  # Orange
    'Q': (0, 0, 0),      # Black question mark
    ' ': None            # Transparent
}
