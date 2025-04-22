from cmu_graphics import *
from Models.game_model import GameModelManager
from Controllers.game_controller import GameController
from Views.game_view import GameView

def onAppStart(app):
    app.timer = 0
    
    # GAME STATE VARIABLES
    app.isStartScreen = True 
    app.isPaused = False
    app.isGameOver = False
    app.isLevelComplete = False
    app.isControlsScreen = False
    app.appearanceMode = "light"
    app.level = 1
    app.selectedLevel = 1

    app.groundY = app.height - 30
    
    # Create models, views and controllers after setting up game state
    app.model = GameModelManager(app)
    app.controller = GameController(app)
    app.view = GameView(app)

    # Set up sounds
    app.themeMusic = Sound("assets/theme.mp3")
    app.themeMusic.setVolume(0.5)
    app.themeMusic.play(loop=True)
    app.themeMusic.setVolume(0.2)

    app.meteorSound = Sound("assets/meteor.mp3")
    app.meteorSound.setVolume(0.5)
    
    # Define initNewGame as a method to the app
    def initNewGame():
        """Initialize a new game with the selected level"""
        app.isControlsScreen = False
        app.isStartScreen = False
        app.isPaused = False
        app.isGameOver = False
        app.isLevelComplete = False
        
        # Set the level from selection
        app.level = app.selectedLevel
        
        # Update obstacle manager for the selected level
        if hasattr(app.model, 'obstacleManager'):
            app.model.obstacleManager.updateLevel(app.level)
        
        # Reset enemy manager if in battle mode
        if app.level == 2 and hasattr(app.model, 'enemyManager'):
            app.model.enemyManager.reset_enemies()
        
        # Ensure dino is in running state
        if hasattr(app.model, 'dino'):
            app.model.dino.isRunning = True
            app.model.dino.isIdle = False
            app.model.dino.health = app.model.dino.maxHealth  # Reset health

        # Reset score
        app.model.score = 0
    
    # Bind the function to the app object
    app.initNewGame = initNewGame

def onKeyPress(app, key):
    # Handle back key from controls screen
    if app.isControlsScreen and key == 'escape':
        app.isControlsScreen = False
        app.isStartScreen = True
        return
        
    app.controller.handleKeyPress(key)

def onKeyHold(app, keys):
    app.controller.handleKeyHold(keys)

def onKeyRelease(app, key):
    app.controller.handleKeyRelease(key)

def onMousePress(app, mouseX, mouseY):
    # Handle mouse press for buttons on start screen
    if app.isStartScreen:
        # Check for level selection buttons
        for button in app.view.levelButtons:
            if (abs(mouseX - button['x']) < button['width'] / 2 and
                abs(mouseY - button['y']) < button['height'] / 2):
                # Set the selected level and start game immediately
                app.selectedLevel = button['level']
                app.initNewGame()
                return
                
        # Check for controls button
        controlsButton = app.view.controlsButton
        if (abs(mouseX - controlsButton['x']) < controlsButton['width'] / 2 and
            abs(mouseY - controlsButton['y']) < controlsButton['height'] / 2):
            app.isStartScreen = False
            app.isControlsScreen = True
            return
    
    # Handle buttons on controls screen
    if app.isControlsScreen:
        # Level selection buttons
        levelY = app.height - 180
        levelButtonWidth = 120
        levelButtonHeight = 40
        levelButtonSpacing = 140
        
        # Level 1 button
        level1X = app.width//2 - levelButtonSpacing//2
        if (abs(mouseX - level1X) < levelButtonWidth//2 and 
            abs(mouseY - levelY) < levelButtonHeight//2):
            app.selectedLevel = 1
            return
            
        # Level 2 button
        level2X = app.width//2 + levelButtonSpacing//2
        if (abs(mouseX - level2X) < levelButtonWidth//2 and 
            abs(mouseY - levelY) < levelButtonHeight//2):
            app.selectedLevel = 2
            return
            
        # Play button
        playButtonY = app.height - 100
        if (abs(mouseX - app.width//2) < 80 and 
            abs(mouseY - playButtonY) < 20):
            app.initNewGame()
            return
        
        # Back button
        backButtonY = app.height - 50
        if (abs(mouseX - app.width//2) < 60 and 
            abs(mouseY - backButtonY) < 15):
            app.isControlsScreen = False
            app.isStartScreen = True
            return
    
    app.controller.handleMousePress(mouseX, mouseY)

def onMouseRelease(app, mouseX, mouseY):
    app.controller.handleMouseRelease(mouseX, mouseY)

def onStep(app):
    # Update timer based on game state
    if app.isStartScreen or app.isPaused or app.isGameOver or app.isLevelComplete or app.isControlsScreen:
        # Update timer at a reduced rate for smoother animations when not active
        if app.timer % 3 == 0:
            app.timer += 1
    else:
        app.timer += 1
    
    if not app.isLevelComplete:
        app.controller.update()

def redrawAll(app):
    app.view.draw()

def main():
    runApp(800, 600)

if __name__ == '__main__':
    main()
