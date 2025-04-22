from cmu_graphics import *
import random
from PIL import Image

class Environment:
    def __init__(self, app):
        self.app = app
        self.width = app.width
        self.height = app.height
        
        self.groundY = app.height - 45
        self.groundHeight = 40

        # Fixed environment colors
        self.skyColor = rgb(16, 42, 84)  # Dark blue
        self.groundColor = rgb(83, 83, 83)  # Dark gray
        self.cloudColor = rgb(255, 255, 255)  # White
        self.cloudSpeed = 0.8
            
        # Clouds
        self.clouds = []
        for i in range(3):
            # randomly placed from the left side of the screen
            x = random.randint(0, self.width)
            # randomly placed in the sky (50 -> 150 height)
            y = random.randint(50, 150)
            size = random.randint(20, 40)
            self.clouds.append((x, y, size))

        # Ground animation
        bgImage = Image.open('assets/ground.png')
        self.groundImg = CMUImage(bgImage)
        self.groundX = 0
        self.groundSpeed = 2  # Speed of ground movement
    
    def update(self):
        # Move clouds
        for i in range(len(self.clouds)):
            x, y, size = self.clouds[i]
            # move clouds
            x -= self.cloudSpeed
            if x < -50:
                x = self.width + 50
                y = random.randint(50, 150)
            self.clouds[i] = (x, y, size)
            
        # Update ground position for scrolling effect
        self.groundX -= self.groundSpeed
        
        # Reset ground position when it has scrolled one full width
        # This creates a seamless loop
        if self.groundX <= -self.width:
            self.groundX = 0
    
    def draw(self):
        # Draw sky
        drawRect(0, 0, self.width, self.height, fill=self.skyColor)
        
        # Draw clouds
        for x, y, size in self.clouds:
            self.drawCloud(x, y, size, self.cloudColor)
        
        # Draw scrolling ground
        drawImage(self.groundImg, self.groundX, self.groundY, width=self.app.width, height=self.groundHeight)
        drawImage(self.groundImg, self.groundX + self.app.width, self.groundY, width=self.app.width, height=self.groundHeight)
    
    def drawCloud(self, x, y, size, color):
        # Simple clouds using circles
        drawCircle(x, y, size * 0.6, fill=color)
        drawCircle(x + size * 0.4, y - size * 0.2, size * 0.4, fill=color)
        drawCircle(x + size * 0.8, y, size * 0.5, fill=color)
        drawCircle(x + size * 0.4, y + size * 0.2, size * 0.45, fill=color)
