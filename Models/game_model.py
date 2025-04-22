from Models.base_model import GameModel
from Models.dino import Dino
from Models.environment import Environment
from Models.obstacles import ObstacleManager
import Models.database_manager as db

class GameModelManager(GameModel):
    def __init__(self, app):
        super().__init__(app)
        self.dinoX = 100
        self.dinoY = app.groundY - 70 
        
        self.dino = Dino(app, self.dinoX, self.dinoY)
        
        self.dino.isRunning = True
        self.dino.isIdle = False
        
        self.environment = Environment(app)
        self.obstacleManager = ObstacleManager(app)
        
        self.score = 0
        self.highScore = db.get_highscore()
        
        self.currentLevel = app.level

    def update(self):
        super().update()
        
        if hasattr(self, 'dino') and self.dino is not None:
            # put to running state when game is active
            if not self.app.isPaused and not self.app.isGameOver and not self.app.isStartScreen:
                if not self.dino.isDead and not self.dino.isJumping:
                    self.dino.isRunning = True
                    self.dino.isIdle = False
            
            # Update dino
            self.dino.update()
        
        # Update environment and obstacles
        if hasattr(self, 'environment'):
            self.environment.update()
        
        if hasattr(self, 'obstacleManager'):
            self.obstacleManager.update()
        
        # Check for level completion
        self.checkLevelCompletion()
        
        # Update score and high score
        if self.score > self.highScore:
            self.highScore = self.score
            db.update_highscore(int(self.score))
    
    def getScoreText(self):
        return f"Score: {int(self.score)}"
    
    def getHighScoreText(self):
        return f"HI: {int(self.highScore)}"
        
    def getLevelText(self):
        level_settings = db.get_level_settings(self.currentLevel)
        return f"Level: {level_settings['name']}"

    def draw(self):
        self.dino.draw()
        self.environment.draw()

    def checkCollisions(self):
        """Check for collisions between dino and obstacles"""
        for obstacle in self.obstacleManager.obstacles:
            # Check dino collision with obstacles
            if self.dino.collidesWith(obstacle):
                # Set dying state and start animation
                self.dino.isDead = True
                self.dino.isRunning = False
                self.dino.isIdle = False
                return True
                
            # Check if any active fire hits the obstacle
            for fire in self.dino.active_fires:
                if fire.is_active and self.checkFireCollision(fire, obstacle):
                    # Mark obstacle as dead when hit by fire
                    obstacle.isDead = True
                    obstacle.counted = True  # Count it as passed
                    
                    # Also deactivate the fire upon hit
                    fire.is_active = False
        
        return False
        
    def checkFireCollision(self, fire, obstacle):
        """Check if fire collides with an obstacle"""
        # Simple rectangle collision check
        fireLeft = fire.x - fire.width/2
        fireRight = fire.x + fire.width/2
        fireTop = fire.y - fire.height/2
        fireBottom = fire.y + fire.height/2
        
        obstacleLeft = obstacle.x
        obstacleRight = obstacle.x + obstacle.width
        obstacleTop = obstacle.y
        obstacleBottom = obstacle.y + obstacle.height
        
        # Check for overlap
        if (fireRight >= obstacleLeft and 
            fireLeft <= obstacleRight and
            fireBottom >= obstacleTop and
            fireTop <= obstacleBottom):
            return True
            
        return False

    def checkLevelCompletion(self):
        """Check if level is complete and set appropriate flag"""
        if hasattr(self, 'obstacleManager') and not self.app.isGameOver and not self.app.isPaused and not self.app.isStartScreen:
            # If obstacleManager reports level complete, set the flag
            if self.obstacleManager.isLevelComplete():
                print("Setting level complete flag from game model")
                self.app.isLevelComplete = True

