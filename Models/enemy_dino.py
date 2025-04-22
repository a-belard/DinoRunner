from Models.dino import Dino
from cmu_graphics import *
import random

class EnemyDino(Dino):
    def __init__(self, app, x, y):
        super().__init__(app, x, y)
        
        # Position enemy for better visibility - closer to view
        # Keep x at most 200 pixels off the right edge
        self.x = min(x, app.width + 200)
        
        # Enemy specific attributes
        self.isEnemy = True
        self.targetDino = app.model.dino
        self.maxHealth = 100
        self.health = self.maxHealth
        self.damage = 20
        
        # Get battle settings
        try:
            import Models.database_manager as db
            battle_settings = db.get_battle_settings()
            self.damage = battle_settings.get('enemy_fire_damage', 15)
        except:
            self.damage = 15
        
        # AI behavior state
        self.state = "approach"
        self.stateTimer = 0
        self.stateDuration = 120
        self.thinkTimer = 0
        self.thinkInterval = 30
        
        # Load enemy-specific appearance
        self.loadEnemyAppearance()
        
        # Debug print
        print(f"Enemy dino created at ({self.x}, {self.y}), targeting player at ({self.targetDino.x}, {self.targetDino.y})")
    
    def loadEnemyAppearance(self):
        # Make enemy face player initially
        self.isFacingRight = False
        
        # Print frame counts to ensure animations are loaded
        print(f"Enemy loaded with {len(self.walking_frames)} walking frames, " +
              f"{len(self.idle_frames)} idle frames, " +
              f"{len(self.die_frames)} die frames, " +
              f"{len(self.attack_frames)} attack frames")
        
        # Create default death frame if none exist
        if len(self.die_frames) == 0:
            print("No death frames found for enemy! Creating default death frame.")
            # Use any available frame as a fallback
            if len(self.idle_frames) > 0:
                self.die_frames = [self.idle_frames[0]]
                self.left_die_frames = [self.left_idle_frames[0]]
            elif len(self.walking_frames) > 0:
                self.die_frames = [self.walking_frames[0]]
                self.left_die_frames = [self.left_walking_frames[0]]
    
    def update(self, events=None):
        # If dead, only update the death animation and nothing else
        if self.isDead:
            # Update animation timer for death animation
            self.animationTimer += 1
            if self.animationTimer >= 10:
                self.animationTimer = 0
                self.deathAnimationFrame += 1
                
                # Check if death animation is complete
                if self.deathAnimationFrame >= len(self.die_frames):
                    self.isDeathAnimationPlaying = False
                    self.deathAnimationComplete = True
                    print("Enemy death animation complete, enemy will be removed.")
            return
        
        # Update AI state timers
        self.stateTimer += 1
        self.thinkTimer += 1
        
        # Change state if duration expired
        if self.stateTimer >= self.stateDuration:
            self.chooseNewState()
            self.stateTimer = 0
        
        # Think and act based on current state
        if self.thinkTimer >= self.thinkInterval:
            self.think()
            self.thinkTimer = 0
            
        # Handle jumping physics
        if self.isJumping:
            self.yVelocity += self.gravity
            self.y += self.yVelocity
            
            if self.y >= self.groundY - self.height:
                self.y = self.groundY - self.height
                self.isJumping = False
                self.yVelocity = 0
                self.isRunning = True

        # Animation update
        self.animationTimer += 1
        if self.animationTimer >= 10:
            self.animationTimer = 0
            self.state_frame_index = (self.state_frame_index + 1) % len(self.getStateFrames())

        # Update active fires
        for fire in self.active_fires[:]:
            fire.update()
            if not fire.is_active:
                self.active_fires.remove(fire)
                
        # Handle attack progress
        if self.isAttacking:
            self.attackTotalFrames += 1
            
            # Begin attack sequence if not already in progress
            if not self.attackInProgress and self.attackTotalFrames > 5:
                self.attackInProgress = True
                
            # Continue animation for full duration
            if self.attackTotalFrames > 30:
                self.isAttacking = False
                self.attackInProgress = False
                self.attackComplete = True
                self.isRunning = True
                
        # Fire delay timer
        if self.should_create_fire and self.isAttacking:
            self.fire_timer += 1
            if self.fire_timer >= 10:
                self.should_create_fire = False
                self.create_fire()
                print("Enemy created fire!")
    
    def think(self):
        # Skip if dead
        if self.isDead:
            return
            
        # Get distance to player
        distance = self.x - self.targetDino.x
        abs_distance = abs(distance)
        
        # Set facing direction towards player
        self.isFacingRight = distance < 0
        
        # Act based on current state
        if self.state == "approach":
            # Move toward player more aggressively
            if abs_distance > 150:
                if distance > 0:
                    self.moveBack()
                else:
                    self.moveForward()
            else:
                # Close enough to attack
                if random.random() < 0.5:
                    self.state = "attack"
                    self.stateTimer = 0
                
        elif self.state == "attack":
            # Attack if player is in range and not too close
            if abs_distance < 350 and random.random() < 0.6:
                # Trigger attack animation and fire creation
                self.attack()
                
            # Move to maintain optimal attack distance
            if abs_distance < 100:
                # Too close, back away a bit
                if distance > 0:
                    self.moveForward()
                else:
                    self.moveBack()
            elif abs_distance > 250:
                # Too far, move closer
                if distance > 0:
                    self.moveBack()
                else:
                    self.moveForward()
            
        elif self.state == "retreat":
            # Move away from player
            if abs_distance < 300:
                if distance > 0:
                    self.moveForward()
                else:
                    self.moveBack()
            else:
                # Far enough away, switch to approach
                self.state = "approach"
                self.stateTimer = 0
        
        # Random jumps - less frequent to make aiming more predictable
        if random.random() < 0.02:
            self.jump()
            
    def attack(self):
        # Override parent attack method for enemy-specific behavior
        if not self.isDead and not self.isAttacking:
            self.isAttacking = True
            self.isRunning = False
            self.isIdle = False
            self.state_frame_index = 0
            self.attackComplete = False
            self.attackInProgress = False
            self.attackTotalFrames = 0
            
            # Set flag to create fire after delay
            self.should_create_fire = True
            self.fire_timer = 0
            
            print(f"Enemy attacking! Creating fire in direction: {'right' if self.isFacingRight else 'left'}")
            
    def chooseNewState(self):
        # Weight the state choices to favor attacking
        if self.state == "approach":
            # 80% chance to attack, 20% to retreat
            if random.random() < 0.8:
                self.state = "attack"
            else:
                self.state = "retreat"
        elif self.state == "attack":
            # 30% chance to keep attacking, 40% to approach, 30% to retreat
            r = random.random()
            if r < 0.3:
                self.state = "attack"
            elif r < 0.7:
                self.state = "approach"
            else:
                self.state = "retreat"
        else:  # retreat
            # 70% chance to approach again, 30% to attack from retreat
            if random.random() < 0.7:
                self.state = "approach"
            else:
                self.state = "attack"
            
        # Randomize duration based on state
        if self.state == "attack":
            self.stateDuration = random.randint(60, 120)
        elif self.state == "retreat":
            self.stateDuration = random.randint(30, 90)
        else:
            self.stateDuration = random.randint(90, 180)
    
    def takeDamage(self, amount):
        # Don't take damage if already dead
        if self.isDead:
            return False
            
        # Apply damage
        self.health -= amount
        print(f"Enemy took {amount} damage! Health: {self.health}/{self.maxHealth}")
        
        if self.health <= 0:
            self.health = 0
            self.isDead = True
            # Clear any active fires when dying
            self.active_fires = []
            self.startDeathAnimation()
            print("Enemy has been defeated!")
            
        return self.isDead
    
    def drawHealthBar(self):
        barWidth = 60
        barHeight = 8
        
        # Position above the dino
        barX = self.x + (self.width - barWidth) / 2
        barY = self.y - 20
        
        # Draw background
        drawRect(barX, barY, barWidth, barHeight, fill='darkRed')
        
        # Draw health
        healthWidth = (self.health / self.maxHealth) * barWidth
        if healthWidth > 0:
            drawRect(barX, barY, healthWidth, barHeight, fill='green')
            
        # Draw border
        drawRect(barX, barY, barWidth, barHeight, fill=None, border='black')
    
    def draw(self):
        # If dead but animation not complete, show death animation
        if self.isDead:
            # Draw death animation
            self.drawDead()
            return
        
        # Otherwise use standard draw method
        super().draw()
        
        # Draw health bar if not dead
        if not self.isDead:
            self.drawHealthBar()
            
    def drawDead(self):
        frameIndex = min(self.deathAnimationFrame, len(self.die_frames) - 1)
        
        if self.isFacingRight:
            drawImage(self.die_frames[frameIndex], self.x, self.y, 
                    width=self.width, height=self.height, align='left-top',
                    opacity=70)
        else:
            drawImage(self.left_die_frames[frameIndex], self.x, self.y, 
                    width=self.width, height=self.height, align='left-top',
                    opacity=70)
    
    def create_fire(self):
        # Create fire in front of enemy dino
        direction = 1 if self.isFacingRight else -1
        mouth_x = self.x + (self.width * 0.8 if self.isFacingRight else self.width * 0.2)
        mouth_y = self.y + (self.height * 0.4)
        
        # Create fire marked as enemy fire with is_enemy=True flag
        from Models.fire import Fire
        fire = Fire(x=mouth_x, y=mouth_y, width=60, height=40, direction=direction, is_enemy=True)
        self.active_fires.append(fire)
        print(f"Enemy created fire at ({mouth_x}, {mouth_y}) going {'right' if direction > 0 else 'left'}")
    
    def startDeathAnimation(self):
        # Override parent method to add custom enemy death behavior
        self.isDead = True
        self.isDeathAnimationPlaying = True
        self.deathAnimationFrame = 0
        self.deathAnimationComplete = False
        
        # Ensure all active states are reset
        self.isAttacking = False
        self.isRunning = False
        self.isJumping = False
        self.isIdle = False 