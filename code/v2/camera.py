import pygame

class Camera:
    def __init__(self, width, height):
        self.camera = pygame.Rect(0, 0, width, height)
        self.width = width
        self.height = height
        self.offset_x = 0
        self.offset_y = 0
        
    def apply(self, entity):
        """Returns the entity's rectangle offset by camera position"""
        return entity.rect.move(self.camera.topleft)
    
    def apply_rect(self, rect):
        """Returns a rectangle offset by camera position"""
        return rect.move(self.camera.topleft)
        
    def update(self, target):
        """Updates camera position based on target entity"""
        # Track target horizontally with smooth movement
        x = -target.rect.centerx + int(self.width / 2)
        y = -target.rect.centery + int(self.height / 2)
        
        # Limit scrolling to game world
        # x = min(0, x)  # left
        # x = max(-(self.width), x)  # right
        # y = min(0, y)  # top
        # y = max(-(self.height), y)  # bottom
        
        # Apply camera position with smooth movement
        self.camera = pygame.Rect(x, y, self.width, self.height)
        
        # Store offset for parallax effects
        self.offset_x = x
        self.offset_y = y
