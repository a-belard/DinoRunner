from Models.base_model import GameModel
from Models.dino import Dino
from Models.environment import Environment
from Models.obstacles import ObstacleManager
from Models.enemy_manager import EnemyManager
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
        self.enemyManager = EnemyManager(app)
        
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
        
        # Update environment
        if hasattr(self, 'environment'):
            self.environment.update()
        
        # Update obstacles or enemies based on level
        if self.app.level == 1:
            # Level 1: Use obstacles
            if hasattr(self, 'obstacleManager'):
                self.obstacleManager.update()
        else:
            # Level 2: Use enemies
            if hasattr(self, 'enemyManager'):
                self.enemyManager.update()
                
                # Check for enemy-fire collisions
                if hasattr(self.dino, 'active_fires') and self.dino.active_fires:
                    self.enemyManager.check_collision_with_fires(self.dino.active_fires)
                
                # Check for enemy-player collisions and enemy fire-player collisions
                self.enemyManager.check_collision_with_player(self.dino)
                
                # Check enemy fire collisions with player
                for enemy in self.enemyManager.enemies:
                    if hasattr(enemy, 'active_fires') and enemy.active_fires:
                        for fire in enemy.active_fires:
                            if self.check_enemy_fire_collision_with_player(fire, self.dino):
                                # Damage player and deactivate fire
                                if hasattr(self.dino, 'takeDamage'):
                                    self.dino.takeDamage(enemy.damage)
                                    print(f"Player hit by enemy fire! Health: {self.dino.health}/{self.dino.maxHealth}")
                                fire.is_active = False
                
                # Check if all enemies defeated to complete the level
                if self.enemyManager.all_enemies_defeated():
                    self.app.isLevelComplete = True
        
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
        
        # Draw level-specific elements
        if self.app.level == 1:
            # Level 1: Draw obstacles
            self.obstacleManager.draw()
        else:
            # Level 2: Draw enemies
            if hasattr(self, 'enemyManager') and self.app.level == 2:
                # Make sure enemy manager updates properly
                if len(self.enemyManager.enemies) == 0 and self.enemyManager.enemies_defeated == 0:
                    print("Game model detected no enemies in level 2, spawning enemy...")
                    self.enemyManager.spawn_enemy()
                self.enemyManager.draw()
                print(f"Drawing {len(self.enemyManager.enemies)} enemies from game model")

    def checkCollisions(self):
        """Check for collisions between dino and obstacles or enemies"""
        # Level 1: Check obstacle collisions
        if self.app.level == 1:
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
        
        # No collision
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
        if not self.app.isGameOver and not self.app.isPaused and not self.app.isStartScreen:
            if self.app.level == 1:
                # Level 1: Check if all obstacles completed
                if hasattr(self, 'obstacleManager') and self.obstacleManager.isLevelComplete():
                    print("Setting level complete flag from game model - Level 1 complete")
                    self.app.isLevelComplete = True
            else:
                # Level 2: Check if all enemies defeated
                if hasattr(self, 'enemyManager') and self.enemyManager.all_enemies_defeated():
                    print("Setting level complete flag from game model - Level 2 complete")
                    self.app.isLevelComplete = True

    def check_enemy_fire_collision_with_player(self, fire, player):
        """Check if enemy fire collides with player"""
        # Simple rectangle collision check
        fireLeft = fire.x - fire.width/2
        fireRight = fire.x + fire.width/2
        fireTop = fire.y - fire.height/2
        fireBottom = fire.y + fire.height/2
        
        playerLeft = player.x
        playerRight = player.x + player.width
        playerTop = player.y
        playerBottom = player.y + player.height
        
        # Check for overlap
        if (fireRight >= playerLeft and 
            fireLeft <= playerRight and
            fireBottom >= playerTop and
            fireTop <= playerBottom):
            return True
            
        return False

