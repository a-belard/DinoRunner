from cmu_graphics import *
from Models.game_model import GameModelManager
from Controllers.game_controller import GameController
from Views.game_view import GameView

def onAppStart(app):
    app.timer = 0
    
    #### GAME STATE VARIABLES ####
    app.isStartScreen = True 
    app.isPaused = False
    app.isGameOver = False
    app.isLevelComplete = False
    app.appearanceMode = "light"
    app.level = 1
    app.selectedLevel = 1

    app.groundY = app.height - 30
    
    # Create models, views and controllers after setting up game state
    app.model = GameModelManager(app)
    app.controller = GameController(app)
    app.view = GameView(app)

    # set up sounds
    app.themeMusic = Sound("assets/theme.mp3")
    app.themeMusic.setVolume(0.5)
    app.themeMusic.play(loop=True)
    app.themeMusic.setVolume(0.3)

    app.meteorSound = Sound("assets/meteor.mp3")
    app.meteorSound.setVolume(0.5)


def onKeyPress(app, key):
    app.controller.handleKeyPress(key)

def onKeyHold(app, keys):
    app.controller.handleKeyHold(keys)

def onKeyRelease(app, key):
    app.controller.handleKeyRelease(key)

def onMousePress(app, mouseX, mouseY):
    app.controller.handleMousePress(mouseX, mouseY)

def onMouseRelease(app, mouseX, mouseY):
    app.controller.handleMouseRelease(mouseX, mouseY)

def onStep(app):
    # When level is complete, treat it like a pause for animation
    if app.isStartScreen or app.isPaused or app.isGameOver or app.isLevelComplete:
        # Update timer at a reduced rate for smoother animations even when not active
        if app.timer % 3 == 0:  # Only increment every 3rd frame when not active
            app.timer += 1
    else:
        app.timer += 1  # Normal rate when active
    
    if not app.isLevelComplete:
        app.controller.update()

def redrawAll(app):
    app.view.draw()

def main():
    runApp(800, 600)

if __name__ == '__main__':
    main()
