from cmu_graphics import *
from PIL import Image
from Views.components.buttons import KeyButton
import os

class GameView:
    def __init__(self, app):
        self.app = app
        self.model = app.model
        
        # Colors
        self.backgroundColor = rgb(240, 240, 240)  # Light gray
        self.textColor = rgb(200, 200, 200) 
        
        # Start screen colors and images
        self.startScreenBgColor = rgb(25, 25, 112)  # Midnight Blue
        self.startScreenTextColor = rgb(255, 255, 255)  # White
        
        # Load background image
        bgImage = Image.open('assets/bg.jpg')
        self.backgroundImage = CMUImage(bgImage)
        

        fire_icon_path = 'assets/split_fire/0.gif'  # Using the first fire frame as icon
        fire_icon = Image.open(fire_icon_path)
        self.fire_icon = CMUImage(fire_icon)

        
        # Level selection buttons
        self.levelButtons = [
            {'x': app.width//2, 'y': app.height//2 + 20, 'width': 120, 'height': 40, 'level': 1, 'text': 'Easy'},
            {'x': app.width//2, 'y': app.height//2 + 80, 'width': 120, 'height': 40, 'level': 2, 'text': 'Battle'},
            # {'x': app.width//2, 'y': app.height//2 + 140, 'width': 120, 'height': 40, 'level': 3, 'text': 'Hard'}
        ]

        keys = ['UP', 'DOWN', 'LEFT', 'RIGHT', 'SPACE', 'ESC', 'R']
        self.keyButtons = {}
        for i, key in enumerate(keys):
            x = app.width - 100
            y = 50 + i * 60
            button = KeyButton(key, x, y)
            self.keyButtons[key] = button
    
    def drawButton(self, key, x, y, width, height):
        key = self.keyButtons.get(key)
        if key:
            key.x = x
            key.y = y
            key.width = width
            key.height = height
            key.draw()


    def draw(self):
        # Draw environment only when not showing special screens
        if not self.app.isStartScreen and not self.app.isLevelComplete and not self.app.isGameOver:
            self.model.environment.draw()
            
            # Draw obstacles
            self.model.obstacleManager.draw()
            
            # Draw the dinosaur
            self.model.dino.draw()
        
        ##################################
        ##################################
        ##################################
        ##################################
################################## GAME CONTROL ##################################
        ##################################
        ##################################
        ##################################
        ##################################

        # Draw UI elements pause, score, level
        if not self.app.isStartScreen:
            self.drawUI()
        
        # Draw overlays if needed - draw level complete LAST to ensure it's on top
        if self.app.isStartScreen:
            self.drawStartScreen()
        elif self.app.isPaused and not self.app.isGameOver:
            self.drawPaused()
        elif self.app.isGameOver:
            self.drawGameOver()
        
        # Always check isLevelComplete flag separately to ensure it gets priority
        if self.app.isLevelComplete:
            print("Drawing level complete screen")
            self.drawLevelComplete()

    def drawObstacleCounts(self):
        pass

    def drawStartScreen(self):
        # Draw background image
        if self.backgroundImage:
            drawImage(self.backgroundImage, 0, 0, width=self.model.width, height=self.model.height)
        else:
            # draw to rectangle if image not available
            drawRect(0, 0, self.model.width, self.model.height, fill="black", opacity=80)

        drawLabel("Dino Runner", self.model.width//2, 
                     self.model.height//2 - 100, size=50, 
                     fill="white", bold=True)
        
        # Draw level selection buttons
        for button in self.levelButtons:
            isCurrent = self.app.selectedLevel == button['level']
            # Button background
            buttonColor = rgb(60, 60, 180) if isCurrent else rgb(40, 40, 140)
            drawRect(button['x'] - button['width']//2, 
                    button['y'] - button['height']//2,
                    button['width'], button['height'],
                    fill=buttonColor,
                    border=self.startScreenTextColor,
                    borderWidth=2)
            # Button text
            drawLabel(button['text'], button['x'], button['y'],
                     fill=self.startScreenTextColor,
                     size=20, bold=isCurrent)
        
        # Draw instructions
        drawLabel("Use UP/DOWN to select level", self.model.width//2, 
                 self.model.height - 80, size=18, fill=self.startScreenTextColor)
        
        drawLabel("Press ENTER to start", self.model.width//2, 
                 self.model.height - 50, size=18, fill=self.startScreenTextColor)
    
    def drawUI(self):
        # Score
        drawLabel(self.model.getScoreText(), 
                 self.model.width - 80, 30, size=20,
                 fill=self.textColor, align='right', bold=True)
        
        # High score
        drawLabel(self.model.getHighScoreText(), 
                 80, 30, size=20,
                 fill=self.textColor, align='left', bold=True)
                 
        # Current level
        drawLabel(self.model.getLevelText(),
                 self.model.width//2, 30, size=20,
                 fill=self.textColor, align='center', bold=True)
        
        # Fire attacks counter with icon
        remaining_attacks = self.model.dino.max_fire_count - self.model.dino.total_fires_used
        
        # Position for the fire icon and count
        icon_x = self.model.width - 120
        icon_y = 60
        count_x = self.model.width - 95
        count_y = 60
        
        # Draw fire icon (image)
        drawImage(self.fire_icon, icon_x, icon_y, width=40, height=35, align='center')

        # Draw the count
        drawLabel(f": {remaining_attacks}", count_x, count_y, size=20,
                 fill="red" if remaining_attacks == 0 else self.textColor, align='left', bold=True)
        
        # Obstacle counts
        if not self.app.isStartScreen and not self.app.isGameOver and not self.app.isPaused:
            self.drawObstacleCounts()
    
    def drawPaused(self):
        # Draw background image
        if self.backgroundImage:
            drawImage(self.backgroundImage, 0, 0, width=self.model.width, height=self.model.height, opacity=70)
        else:
            # Fallback to rectangle if image not available
            drawRect(0, 0, self.model.width, self.model.height, fill='black', opacity=50)
        
        # Draw pause text
        drawLabel("PAUSED", self.model.width//2, self.model.height//2, 
                 size=40, fill='white', bold=True)
        drawLabel("Press ESC to resume", self.model.width//2, 
                 self.model.height//2 + 50, size=20, fill='white')
        drawLabel("Press R to restart", self.model.width//2, 
                 self.model.height//2 + 80, size=20, fill='white')
    
    def drawGameOver(self):
        # Draw background image
        if self.backgroundImage:
            drawImage(self.backgroundImage, 0, 0, width=self.app.width, height=self.app.height)
            drawRect(0, 0, self.app.width, self.app.height, fill='red', opacity=60)
        else:
            # Fallback to rectangle if image not available
            drawRect(0, 0, self.app.width, self.app.height, fill='black', opacity=70)
        
        # Draw game over text
        drawLabel("GAME OVER", self.model.width//2, 120, 
                 size=40, fill='white', bold=True)
        
        
        drawLabel(f"{int(self.model.score)}", self.model.width//2, 
                 self.model.height//2 + 10, size=60, fill='white')
        
        drawLabel("Press          to restart", self.model.width//2, 
                 self.model.height - 100, size=25, fill='white')
        
        # Draw restart key
        self.drawButton('R', self.model.width//2 - 20, 
                 self.model.height - 100, width=50, height=50)

    def drawLevelComplete(self):
        # Draw full background image like the start screen
        if self.backgroundImage:
            drawImage(self.backgroundImage, 0, 0, width=self.app.width, height=self.app.height)
            # green overlay
            drawRect(0, 0, self.app.width, self.app.height, fill='green', opacity=30)
        else:
            # Fallback to solid color if image not available
            drawRect(0, 0, self.app.width, self.app.height, fill='darkgreen')
        
        # Draw large banner in center
        bannerHeight = 300
        drawRect(0, self.app.height/2 - bannerHeight/2, self.app.width, bannerHeight, fill='black', opacity=70)
        
        # Draw level complete text
        level = self.model.currentLevel
        drawLabel(f"LEVEL {level} COMPLETE!", self.model.width//2, self.app.height/2 - 100, 
                 size=40, fill='white', bold=True)
        
        # Next level or continue button
        if self.app.level < 2:  # If there's a next level
            drawLabel("Press ENTER to continue to next level", self.model.width//2, 
                     self.app.height/2 + 80, size=22, fill='white', bold=True)
        # If this was the last level
        else:  
            drawRect(self.model.width//2 - 200, self.app.height/2 + 50, 400, 60, 
                    fill='green', opacity=70, border='white', borderWidth=2)
            drawLabel("Congratulations! All levels completed!", self.model.width//2, 
                     self.app.height/2 + 80, size=20, fill='white', bold=True)

        

