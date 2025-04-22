from .cactus import Cactus
from .bird import Bird
from .wifi_meteor import WiFiMeteor
import Models.database_manager as db
import random

class ObstacleManager:
    def __init__(self, app):
        self.app = app
        self.width = app.width
        self.height = app.height
        self.groundY = app.height - 30
        self.obstacles = []
        self.spawnTimer = 0
        
        self.currentLevel = app.level
        settings = db.get_level_settings(self.currentLevel)
        self.spawnInterval = settings["spawnInterval"]
        
        self.birdsPassed = 0
        self.cactiPassed = 0
        self.meteorsPassed = 0
        self.maxBirds = settings["birdCount"]
        self.maxCacti = settings["cactusCount"]
        self.maxMeteors = settings["meteorCount"]
        
        self.birdsSpawned = 0
        self.cactiSpawned = 0
        self.meteorsSpawned = 0
        
        # Level completion delay timer
        self.levelCompleteDetected = False
        self.completionDelayTimer = 0
        self.completionDelayFrames = 300  # Wait 100 frames before showing completion screen
    
    def update(self):
        # Don't update if level is complete
        if hasattr(self.app, 'isLevelComplete') and self.app.isLevelComplete:
            return
        
        settings = db.get_level_settings(self.currentLevel)
        
        # If level completion has been detected but screen not shown yet, increment timer
        if self.levelCompleteDetected and not self.app.isLevelComplete:
            self.completionDelayTimer += 1
            if self.completionDelayTimer >= self.completionDelayFrames:
                print(f"Completion delay reached after {self.completionDelayTimer} frames. Showing level complete screen!")
                self.app.isLevelComplete = True
                return
        
        for obstacle in self.obstacles:
            obstacle.update()
        
        # Count destroyed obstacles
        for obstacle in self.obstacles:
            if obstacle.isDead and not obstacle.counted:
                if obstacle.type == "bird":
                    self.birdsPassed += 1
                elif obstacle.type == "cactus":
                    self.cactiPassed += 1
                elif obstacle.type == "meteor":
                    self.meteorsPassed += 1
                obstacle.counted = True
                print(f"Obstacle {obstacle.type} passed! Total passed: {self.birdsPassed + self.cactiPassed + self.meteorsPassed}")
                
        # Remove dead obstacles from list
        self.obstacles = [obs for obs in self.obstacles if not obs.isDead]
        
        # Print obstacle status every 50 frames for debugging
        if self.app.timer % 50 == 0:
            print(f"OBSTACLE STATUS: Spawned: Birds={self.birdsSpawned}/{self.maxBirds}, Cacti={self.cactiSpawned}/{self.maxCacti}, Meteors={self.meteorsSpawned}/{self.maxMeteors}")
            print(f"OBSTACLE STATUS: Passed: Birds={self.birdsPassed}/{self.maxBirds}, Cacti={self.cactiPassed}/{self.maxCacti}, Meteors={self.meteorsPassed}/{self.maxMeteors}")
            print(f"Active obstacles: {len(self.obstacles)}")
            
            # Force check level completion
            isComplete = self.isLevelComplete()
            print(f"Level completion check result: {isComplete}")
        
        # Only check level completion if all obstacles have been spawned
        allSpawned = (self.birdsSpawned >= self.maxBirds and 
                      self.cactiSpawned >= self.maxCacti and 
                      self.meteorsSpawned >= self.maxMeteors)
                      
        if allSpawned:
            # Check if all obstacles are gone and level is complete
            isComplete = self.isLevelComplete()
            
            # If level complete and not already detected, start the delay timer
            if isComplete and not self.levelCompleteDetected and not self.app.isGameOver:
                print("LEVEL COMPLETE DETECTED! Starting delay timer...")
                self.levelCompleteDetected = True
                self.completionDelayTimer = 0
        
        # Spawn new obstacles if not all have been spawned yet
        self.spawnTimer += 1
        if self.spawnTimer >= self.spawnInterval:
            if (self.birdsSpawned < self.maxBirds or 
                self.cactiSpawned < self.maxCacti or 
                self.meteorsSpawned < self.maxMeteors):
                self.spawnObstacle()
            self.spawnTimer = 0
            
    def updateLevel(self, level):
        """Update obstacle counts when level changes"""
        self.currentLevel = level
        
        # Get new obstacle counts from config
        settings = db.get_level_settings(level)
        
        # Update maximums
        self.maxBirds = settings["birdCount"]
        self.maxCacti = settings["cactusCount"]
        self.maxMeteors = settings["meteorCount"]
        
        # Reset spawn counters for new level
        self.birdsSpawned = min(self.birdsSpawned, self.maxBirds)
        self.cactiSpawned = min(self.cactiSpawned, self.maxCacti)
        self.meteorsSpawned = min(self.meteorsSpawned, self.maxMeteors)
        
        # Update level settings
        self.spawnInterval = settings["spawnInterval"]
    
    def spawnObstacle(self):
        settings = db.get_level_settings(self.currentLevel)
        
        if (self.birdsSpawned >= self.maxBirds and 
            self.cactiSpawned >= self.maxCacti and 
            self.meteorsSpawned >= self.maxMeteors):
            return
            
        canSpawnBird = self.birdsSpawned < self.maxBirds
        canSpawnCactus = self.cactiSpawned < self.maxCacti
        canSpawnMeteor = self.meteorsSpawned < self.maxMeteors
        
        birdProb = settings["birdProbability"]
        meteorProb = settings["meteorProbability"]
        
        availableTypes = []
        if canSpawnBird:
            availableTypes.append("bird")
        if canSpawnCactus:
            availableTypes.append("cactus")
        if canSpawnMeteor:
            availableTypes.append("meteor")
            
        if not availableTypes:
            return
            
        randomVal = random.random()
        if len(availableTypes) == 1:
            obstacleType = availableTypes[0]
        elif len(availableTypes) == 2:
            if "meteor" in availableTypes and "bird" in availableTypes:
                obstacleType = "meteor" if randomVal < meteorProb else "bird"
            elif "meteor" in availableTypes and "cactus" in availableTypes:
                obstacleType = "meteor" if randomVal < meteorProb else "cactus"
            else:
                obstacleType = "bird" if randomVal < birdProb else "cactus"
        else:
            if randomVal < meteorProb:
                obstacleType = "meteor"
            elif randomVal < meteorProb + birdProb:
                obstacleType = "bird"
            else:
                obstacleType = "cactus"

        if obstacleType == "cactus":
            width = 60
            height = 60 
            x = self.app.width + 20
            
            y = self.app.groundY - height
            
            speed = settings["baseSpeed"]["cactus"]
            
            obstacle = Cactus(
                x=x,
                y=y,
                width=width,
                height=height,
                speed=speed
            )
            
            obstacle.counted = False
            self.cactiSpawned += 1
            
        elif obstacleType == "bird":
            width = 60
            height = 50
            
            y_options = [self.app.groundY - 120, self.app.groundY - 80, self.app.groundY - 40]
            y = random.choice(y_options)
            
            speed = settings["baseSpeed"]["bird"]
            
            obstacle = Bird(
                x=self.app.width + 20, 
                y=y,
                width=width,
                height=height,
                speed=speed
            )
            
            obstacle.counted = False
            self.birdsSpawned += 1
            
        elif obstacleType == "meteor":
            width = 45
            height = 70
            
            x = self.app.width * (0.3 + 0.7 * random.random())
            y = 0
            
            speed = settings["baseSpeed"]["bird"] * 1.2
            
            obstacle = WiFiMeteor(
                x=x,
                y=y,
                app=self.app,
                width=width,
                height=height,
                speed=speed
            )
            
            obstacle.counted = False
            self.meteorsSpawned += 1

        self.obstacles.append(obstacle)
    
    def getObstacleCountsText(self):
        return f"Birds: {self.birdsPassed}/{self.maxBirds} | Cacti: {self.cactiPassed}/{self.maxCacti} | Meteors: {self.meteorsPassed}/{self.maxMeteors}"
        
    def draw(self):
        for obstacle in self.obstacles:
            obstacle.draw()

    def isLevelComplete(self):
        """Check if level is complete (simpler criteria)"""
        # Check if all obstacles have been spawned
        allSpawned = (self.birdsSpawned >= self.maxBirds and 
                      self.cactiSpawned >= self.maxCacti and 
                      self.meteorsSpawned >= self.maxMeteors)
        
        # Check if enough obstacles have been passed/destroyed
        # We'll be more lenient - consider level complete if at least 90% of obstacles are passed
        totalObstaclesToSpawn = self.maxBirds + self.maxCacti + self.maxMeteors
        totalObstaclesPassed = self.birdsPassed + self.cactiPassed + self.meteorsPassed
        
        # At least 90% of obstacles must be passed
        sufficientObstaclesPassed = (totalObstaclesPassed >= 0.9 * totalObstaclesToSpawn)
        
        # Check if there are no active obstacles left on screen
        noObstaclesLeft = len(self.obstacles) == 0
        
        # For debugging - print in console
        if allSpawned and (sufficientObstaclesPassed or noObstaclesLeft):
            print(f"Level completion check: allSpawned={allSpawned}, sufficientObstaclesPassed={sufficientObstaclesPassed}, noObstaclesLeft={noObstaclesLeft}")
            print(f"Birds: {self.birdsPassed}/{self.maxBirds}, Cacti: {self.cactiPassed}/{self.maxCacti}, Meteors: {self.meteorsPassed}/{self.maxMeteors}")
            print(f"Total passed: {totalObstaclesPassed}/{totalObstaclesToSpawn} ({(totalObstaclesPassed/totalObstaclesToSpawn)*100:.1f}%)")
        
        # Return true if all obstacles have been spawned and either:
        # 1) Enough obstacles have been passed, or
        # 2) There are no obstacles left on screen
        return allSpawned and (sufficientObstaclesPassed or noObstaclesLeft)