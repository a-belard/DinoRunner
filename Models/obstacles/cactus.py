from cmu_graphics import *
from .obstacle import Obstacle
from PIL import Image
import os
import random

class Cactus(Obstacle):
    def __init__(self, x, y, width=60, height=60, speed=5):
        super().__init__(x, y, width, height, speed, color="darkgreen")
        self.type = "cactus"
        self.loadImages()
        
    def loadImages(self):
        cactus_dir = 'assets/cactus'
        self.cactus_images = []
        
        if os.path.exists(cactus_dir):
            files = [f for f in os.listdir(cactus_dir) if f.endswith('.png') or f.endswith('.gif')]
            
            for file in files:
                file_path = os.path.join(cactus_dir, file)
                image = Image.open(file_path)
                self.cactus_images.append(CMUImage(image))
        
        # If we have images, select a random one
        if len(self.cactus_images) > 0:
            self.current_image = random.choice(self.cactus_images)
        else:
            self.current_image = None
            
    def update(self):
        super().update()
        
    def draw(self):
        if self.current_image:
            drawImage(self.current_image, self.x, self.y, width=self.width, height=self.height)
        else:
            drawRect(self.x, self.y, self.width, self.height, fill=self.color)
            drawLabel("Cactus", self.x + self.width/2, self.y - 10, 
                     fill='white', bold=True, size=12)
                     
    def getCollisionRect(self):
        return (self.x, self.y, self.width, self.height)
