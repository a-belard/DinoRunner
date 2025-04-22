from cmu_graphics import *
from .obstacle import Obstacle
from PIL import Image
import os
import math

class WiFiMeteor(Obstacle):
    def __init__(self, x, y, app, width=70, height=70, speed=7):
        super().__init__(x, y, width, height, speed, color="purple")
        self.app = app
        self.type = "meteor"
        self.color = "purple"
        self.animationTimer = 0
        self.frame_index = 0
        self.loadFrames()
        
        # Calculate speed components based on distance to travel
        self.targetX = 100  # Target x-coordinate where meteor will land
        self.targetY = self.app.groundY  # Ground level
        
        # Calculate distance to target
        dx = self.targetX - x
        dy = self.targetY - y
        distance = math.sqrt(dx**2 + dy**2)
        
        # Normalize direction and multiply by speed
        self.xSpeed = abs(dx / distance * speed * 1.3)
        self.ySpeed = abs(dy / distance * speed * 2.3)
        
        self.rotation = 10
        
        # Play sound when meteor is created
        self.app.meteorSound.play(loop=False)
         
        
    def loadFrames(self):
        """Load all animation frames from the wifi_meteor folder"""
        meteor_dir = 'assets/wifi_meteor'
        self.meteor_frames = []
        
        if os.path.exists(meteor_dir):
            files = [f for f in os.listdir(meteor_dir) if f.endswith('.gif')]

            files.sort(key=lambda x: int(x.split('.')[0]))
            for file in files:
                file_path = os.path.join(meteor_dir, file)
                image = Image.open(file_path)
                self.meteor_frames.append(CMUImage(image))
    
    def update(self):
        # Update position
        self.x -= self.xSpeed
        self.y += self.ySpeed
        
        # Update animation
        self.animationTimer += 1
        if self.animationTimer % 3 == 0 and len(self.meteor_frames) > 0:
            self.frame_index = (self.frame_index + 1) % len(self.meteor_frames)
            
        # Mark as dead when off-screen (either left or bottom)
        if self.x < -50 or self.y > self.app.groundY:
            self.isDead = True
        
    def draw(self):
        if len(self.meteor_frames) > 0:
            # Use current frame for meteor animation
            frameIndex = self.frame_index % len(self.meteor_frames)
            drawImage(self.meteor_frames[frameIndex], self.x, self.y, 
                     width=self.width, height=self.height,
                     rotateAngle=self.rotation)