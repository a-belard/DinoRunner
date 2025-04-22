from Controllers.base_controller import BaseController
from Controllers.game_flow_controller import GameFlowController
from Controllers.dino_controller import DinoController

class GameController(BaseController):
    def __init__(self, app):
        super().__init__(app)
        self.gameFlowController = GameFlowController(self)
        self.dinoController = DinoController(self)
        self.keysPressed = set()
        self.mouseX = 0
        self.mouseY = 0
        self.isMousePressed = False
        
    def handleKeyPress(self, key):
        super().handleKeyPress(key)
        
        # Game flow controls
        self.gameFlowController.handleStartGame(key)
        self.gameFlowController.handlePause(key)
        self.gameFlowController.handleRestart(key)
        
        # Dino controls
        self.dinoController.handleKeyPress(key)
            
    def handleKeyHold(self, keys):
        """Handle keys being held down"""
        self.keysPressed = set(keys)
        
        # Dino controls
        self.dinoController.handleKeyHold(self.keysPressed)
    
    def handleKeyRelease(self, key):
        super().handleKeyRelease(key)
        self.dinoController.handleKeyRelease(key)
        
    def handleMousePress(self, mouseX, mouseY):
        self.mouseX = mouseX
        self.mouseY = mouseY
        self.isMousePressed = True
        
    def handleMouseRelease(self, mouseX, mouseY):
        self.mouseX = mouseX
        self.mouseY = mouseY
        self.isMousePressed = False
        
    def update(self):
        # Update controllers
        self.gameFlowController.update()
        
        # Update dino controller for animations
        if hasattr(self, 'dinoController') and hasattr(self.dinoController, 'update'):
            self.dinoController.update()
        
        # Update game elements when active
        if not (self.app.isStartScreen or self.app.isPaused or self.app.isGameOver or self.app.isControlsScreen):
            if hasattr(self.model, 'environment') and hasattr(self.model.environment, 'update'):
                self.model.environment.update()
            
            # Update game model
            if hasattr(self.model, 'update'):
                self.model.update()

            # Update score
            if hasattr(self.model, 'score'):
                self.model.score += 0.1
        
    def resetGame(self):
        self.gameFlowController.resetGame()