from cmu_graphics import *
from .obstacle import Obstacle
from PIL import Image
import os

class Bird(Obstacle):
    def __init__(self, x, y, width, height, speed=6):
        super().__init__(x, y, width, height, speed, color="blue")
        self.type = "bird"
        self.color = "blue"
        self.animationTimer = 0
        self.frame_index = 0
        self.loadFrames()
        
    def loadFrames(self):
        """Load all animation frames from the bird folder"""
        flying_dir = 'assets/bird/flying'
        self.flying_frames = []
        
        if os.path.exists(flying_dir):
            files = [f for f in os.listdir(flying_dir) if f.endswith('.gif')]
            files.sort(key=lambda x: int(x.split('.')[0]))
            
            for file in files:
                file_path = os.path.join(flying_dir, file)
                image = Image.open(file_path)
                self.flying_frames.append(CMUImage(image))
                
    def update(self):
        super().update()
        
        self.animationTimer += 1
        
        if self.animationTimer % 2 == 0 and len(self.flying_frames) > 0:
            self.frame_index = (self.frame_index + 1) % len(self.flying_frames)
        
    def draw(self):
        if len(self.flying_frames) > 0:
            frameIndex = self.frame_index % len(self.flying_frames)
            drawImage(self.flying_frames[frameIndex], self.x, self.y, 
                     width=self.width, height=self.height)
        else:
            drawRect(self.x, self.y, self.width, self.height, fill=self.color)
            drawLabel("Bird", self.x + self.width/2, self.y - 10, 
                     fill='white', bold=True, size=12)