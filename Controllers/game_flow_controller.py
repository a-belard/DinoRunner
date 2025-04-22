class GameFlowController:
    def __init__(self, gameController):
        self.controller = gameController
        self.app = gameController.app
        self.model = gameController.model

    def handleStartGame(self, key):
        if self.app.isStartScreen:
            # Level selection with up/down keys
            if key == 'up':
                self.app.selectedLevel = max(1, self.app.selectedLevel - 1)
            elif key == 'down':
                self.app.selectedLevel = min(3, self.app.selectedLevel + 1)
            # Start game with enter key
            elif key == 'enter':
                self.app.isStartScreen = False
                self.app.isPaused = False
                self.app.isGameOver = False
                self.app.level = self.app.selectedLevel
                
                # Update obstacle counts for the selected level
                if hasattr(self.model, 'obstacleManager'):
                    self.model.obstacleManager.updateLevel(self.app.level)
                
                # Ensure dino is in running state
                if hasattr(self.model, 'dino'):
                    self.model.dino.isRunning = True
                    self.model.dino.isIdle = False
        
        # Handle level completion
        elif self.app.isLevelComplete and key == 'enter':
            if self.app.level < 2:  # If there's a next level
                # Advance to next level
                self.advanceToNextLevel()
            else:
                # Return to main menu if all levels are completed
                self.app.isLevelComplete = False
                self.app.isStartScreen = True
                self.app.level = 1
                self.app.selectedLevel = 1

        # DEBUG: Force level completion with 'c' key
        elif not self.app.isStartScreen and not self.app.isPaused and not self.app.isGameOver and not self.app.isLevelComplete and key == 'c':
            print("DEBUG: Forcing level completion screen")
            self.app.isLevelComplete = True

    def handlePause(self, key):
        if key == 'esc':
            self.app.isPaused = not self.app.isPaused
            
    def handleRestart(self, key):
        if key == 'r':
            self.resetGame()
            
    def resetGame(self):
        # Reset game state
        self.app.isGameOver = False
        self.app.isPaused = False
        self.app.isLevelComplete = False  # Also reset level completion flag
        self.app.timer = 0
        
        # Create a new model instance with the current level
        self.controller.model = type(self.model)(self.app)
        
        self.app.model = self.controller.model
        
        self.app.view.model = self.controller.model
        
        # Reset the dino controller
        self.controller.dinoController.model = self.controller.model
        self.controller.dinoController.dino = self.controller.model.dino
        
        self.model = self.controller.model
        
        # Reset the score
        self.controller.model.score = 0
        
        # Update obstacle counts for the current level
        if hasattr(self.model, 'obstacleManager'):
            self.model.obstacleManager.updateLevel(self.app.level)
            
            # Also reset the level completion detection variables
            if hasattr(self.model.obstacleManager, 'levelCompleteDetected'):
                self.model.obstacleManager.levelCompleteDetected = False
                self.model.obstacleManager.completionDelayTimer = 0
        
        # Ensure death animation state is reset
        if hasattr(self.controller.model, 'dino'):
            self.controller.model.dino.isDead = False
            self.controller.model.dino.isDeathAnimationPlaying = False
            self.controller.model.dino.deathAnimationComplete = False
            self.controller.model.dino.deathAnimationFrame = 0

        
    def checkGameOver(self):
        if hasattr(self.model, 'player') and self.model.player.isDead:
            self.app.isGameOver = True   

    def update(self):
        # Check game over condition regardless of pause state
        if not self.app.isGameOver and not self.app.isPaused:
            self.checkGameOver()

    def advanceToNextLevel(self):
        """Advance to the next level after completing the current one"""
        # Clear level completion state
        self.app.isLevelComplete = False
        
        # Increment level
        self.app.level += 1
        self.app.selectedLevel = self.app.level
        
        # Update obstacle manager for the new level without resetting
        if hasattr(self.model, 'obstacleManager'):
            self.model.obstacleManager.updateLevel(self.app.level)
            
            # Reset obstacle counters for the new level
            self.model.obstacleManager.birdsPassed = 0
            self.model.obstacleManager.cactiPassed = 0
            self.model.obstacleManager.meteorsPassed = 0
            self.model.obstacleManager.birdsSpawned = 0
            self.model.obstacleManager.cactiSpawned = 0
            self.model.obstacleManager.meteorsSpawned = 0
            
            # Reset level completion delay timer
            self.model.obstacleManager.levelCompleteDetected = False
            self.model.obstacleManager.completionDelayTimer = 0
            
        # Update current level in model
        self.model.currentLevel = self.app.level
        
        # Make sure the dino is running when starting the new level
        if hasattr(self.model, 'dino'):
            self.model.dino.isRunning = True
            self.model.dino.isIdle = False
