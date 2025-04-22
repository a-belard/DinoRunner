from Models.base_model import GameObject
from cmu_graphics import *

class Obstacle(GameObject):
    def __init__(self, x, y, width, height, speed=5, color="green"):
        super().__init__(x, y, width, height)
        self.speed = speed
        self.isDead = False
        self.color = color
        self.type = "obstacle"
        self.counted = False

    def update(self):
        self.x -= self.speed
        
        # Mark as dead when off-screen
        if self.x < -50:
            self.isDead = True