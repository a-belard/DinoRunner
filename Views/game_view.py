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
        
        # Load fire icon for UI
        fire_icon_path = 'assets/split_fire/0.gif'  # Using the first fire frame as icon
        fire_icon = Image.open(fire_icon_path)
        self.fire_icon = CMUImage(fire_icon)

        # Level selection buttons
        self.levelButtons = [
            {'x': app.width//2, 'y': app.height//2 + 20, 'width': 120, 'height': 40, 'level': 1, 'text': 'Easy'},
            {'x': app.width//2, 'y': app.height//2 + 80, 'width': 120, 'height': 40, 'level': 2, 'text': 'Battle'},
            # {'x': app.width//2, 'y': app.height//2 + 140, 'width': 120, 'height': 40, 'level': 3, 'text': 'Hard'}
        ]
        
        # Controls button
        self.controlsButton = {
            'x': app.width//2,
            'y': app.height//2 + 140,
            'width': 120,
            'height': 40,
            'text': 'Controls'
        }

        # Initialize keyboard buttons
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
        if not self.app.isStartScreen and not self.app.isLevelComplete and not self.app.isGameOver and not self.app.isControlsScreen:
            self.model.environment.draw()
            
            # Draw obstacles or enemies based on level
            if self.app.level == 1:
                # Draw obstacles
                self.model.obstacleManager.draw()
            else:
                # Draw enemies - make sure they're drawn in level 2
                if hasattr(self.model, 'enemyManager'):
                    self.model.enemyManager.draw()
                    # Force spawn an enemy if none exist
                    if len(self.model.enemyManager.enemies) == 0 and self.app.level == 2:
                        print("No enemies found in level 2! Forcing enemy spawn...")
                        self.model.enemyManager.spawn_enemy()
            
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
        if not self.app.isStartScreen and not self.app.isControlsScreen:
            self.drawUI()
        
        # Draw overlays if needed - draw level complete LAST to ensure it's on top
        if self.app.isStartScreen:
            self.drawStartScreen()
        elif self.app.isControlsScreen:
            self.drawControlsScreen()
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
        
        # Draw Controls button
        drawRect(self.controlsButton['x'] - self.controlsButton['width']//2, 
                self.controlsButton['y'] - self.controlsButton['height']//2,
                self.controlsButton['width'], self.controlsButton['height'],
                fill=rgb(40, 40, 140),
                border=self.startScreenTextColor,
                borderWidth=2)
        drawLabel(self.controlsButton['text'], self.controlsButton['x'], self.controlsButton['y'],
                 fill=self.startScreenTextColor,
                 size=20, bold=False)
                 
        # Single instruction at the bottom
        drawLabel("Press ENTER to start", self.model.width//2, 
                 self.model.height - 50, size=18, fill=self.startScreenTextColor)
    
    def drawControlsScreen(self):
        # Draw background image
        if self.backgroundImage:
            drawImage(self.backgroundImage, 0, 0, width=self.model.width, height=self.model.height)
        
        drawRect(0, 0, self.model.width, self.model.height, fill="black", opacity=70)

        # Draw title
        drawLabel("GAME CONTROLS", self.model.width//2, 
                 self.model.height//2 - 180, size=40, 
                 fill="white", bold=True)
        
        # Draw control instructions
        controls = [
            {"key": "W / UP", "action": "Jump"},
            {"key": "S / DOWN", "action": "Duck"},
            {"key": "A / LEFT", "action": "Move Left"},
            {"key": "D / RIGHT", "action": "Move Right"},
            {"key": "SPACE", "action": "Attack (Shoot Fire)"},
            {"key": "R", "action": "Restart Game"}
        ]
        
        startY = self.model.height//2 - 100
        spacing = 50
        
        for i, control in enumerate(controls):
            # Draw key
            drawRect(self.model.width//2 - 180, startY + i * spacing - 15, 100, 30, 
                    fill=rgb(40, 40, 140), border='white')
            drawLabel(control["key"], self.model.width//2 - 130, startY + i * spacing, 
                     fill='white', size=16, bold=True)
            
            # Draw action
            drawLabel(control["action"], self.model.width//2 + 20, startY + i * spacing, 
                     fill='white', size=18, align='left')

            
        # Back button
        backButtonY = self.model.height - 50
        drawRect(self.model.width//2 - 60, backButtonY - 15, 120, 30, 
                fill=rgb(40, 40, 140), border='white', borderWidth=2)
        drawLabel("Back to Menu", self.model.width//2, backButtonY, 
                fill='white', size=14)
    
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
        
        # Fire attacks counter
        remaining_attacks = self.model.dino.max_fire_count - self.model.dino.total_fires_used
        
        # Position for fire icon and count
        icon_x = self.model.width - 120
        icon_y = 60
        count_x = self.model.width - 95
        count_y = 60
        
        # Draw fire icon
        drawImage(self.fire_icon, icon_x, icon_y, width=40, height=35, align='center')

        # Draw count - show "∞" for unlimited in level 2
        if self.app.level == 2:
            drawLabel(": ∞", count_x, count_y, size=20, 
                    fill="gold", align='left', bold=True)
        else:
            drawLabel(f": {remaining_attacks}", count_x, count_y, size=20,
                    fill="red" if remaining_attacks == 0 else self.textColor, 
                    align='left', bold=True)
        
        # Show obstacle counts during gameplay
        if not self.app.isStartScreen and not self.app.isGameOver and not self.app.isPaused:
            self.drawObstacleCounts()
    
    def drawPaused(self):
        # Draw background
        if self.backgroundImage:
            drawImage(self.backgroundImage, 0, 0, width=self.model.width, height=self.model.height, opacity=70)
        else:
            drawRect(0, 0, self.model.width, self.model.height, fill='black', opacity=50)
        
        # Pause text and instructions
        drawLabel("PAUSED", self.model.width//2, self.model.height//2, 
                 size=40, fill='white', bold=True)
        drawLabel("Press ESC to resume", self.model.width//2, 
                 self.model.height//2 + 50, size=20, fill='white')
        drawLabel("Press R to restart", self.model.width//2, 
                 self.model.height//2 + 80, size=20, fill='white')
    
    def drawGameOver(self):
        # Draw background
        if self.backgroundImage:
            drawImage(self.backgroundImage, 0, 0, width=self.app.width, height=self.app.height)
            drawRect(0, 0, self.app.width, self.app.height, fill='red', opacity=60)
        else:
            drawRect(0, 0, self.app.width, self.app.height, fill='black', opacity=70)
        
        # Game over text and score
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
        # Draw background
        if self.backgroundImage:
            drawImage(self.backgroundImage, 0, 0, width=self.app.width, height=self.app.height)
            drawRect(0, 0, self.app.width, self.app.height, fill='green', opacity=30)
        else:
            drawRect(0, 0, self.app.width, self.app.height, fill='darkgreen')
        
        # Draw banner
        bannerHeight = 300
        drawRect(0, self.app.height/2 - bannerHeight/2, self.app.width, bannerHeight, fill='black', opacity=70)
        
        # Level complete text
        level = self.model.currentLevel
        drawLabel(f"LEVEL {level} COMPLETE!", self.model.width//2, self.app.height/2 - 100, 
                 size=40, fill='white', bold=True)
        
        # Next level or finish
        if self.app.level < 2:
            drawLabel("Press ENTER to continue to next level", self.model.width//2, 
                     self.app.height/2 + 80, size=22, fill='white', bold=True)
        else:
            drawRect(self.model.width//2 - 200, self.app.height/2 + 50, 400, 60, 
                    fill='green', opacity=70, border='white', borderWidth=2)
            drawLabel("Congratulations! All levels completed!", self.model.width//2, 
                     self.app.height/2 + 80, size=20, fill='white', bold=True)

        

