from Models.base_model import GameObject
from Models.fire import Fire
from cmu_graphics import *
from PIL import Image
import os
import Models.database_manager as db

class Dino(GameObject):
    def __init__(self, app, x, y):
        super().__init__(x, y, width=70, height=70)
        self.app = app
        
        self.isJumping = False
        self.isDucking = False
        self.isRunning = True
        self.isDead = False
        self.isIdle = False
        self.isAttacking = False
        self.attackInProgress = False
        self.attackComplete = False
        self.attackTotalFrames = 0
        self.isDeathAnimationPlaying = False
        self.deathAnimationFrame = 0
        self.deathAnimationComplete = False
        
        self.moveD = 5
        
        self.originalHeight = self.height
        self.gravity = 0.4
        self.jumpForce = -12
        self.yVelocity = 0
        self.groundY = self.app.groundY

        self.y = self.groundY - self.height
        
        self.loadFrames()
        
        self.state_frame_index = 0
        self.animationTimer = 0
        
        # Fire effect
        self.active_fires = []
        self.fire_delay = 20  # Frames to wait before creating fire
        self.fire_timer = 0
        self.should_create_fire = False
        self.current_fire_count = 0
        self.total_fires_used = 0  # Track total fires used (permanent counter)
        
        # Get max fire count from level settings
        level_settings = db.get_level_settings(self.app.level)
        self.max_fire_count = level_settings.get('maxFireCount')
        
    def loadFrames(self):
        walking_dir = 'assets/dino/walking'
        idle_dir = 'assets/dino/idle'
        die_dir = 'assets/dino/die'
        attack_dir = 'assets/dino/attack'
        
        self.walking_frames_pil = self.loadFramesFromDir(walking_dir)
        self.idle_frames_pil = self.loadFramesFromDir(idle_dir)
        self.die_frames_pil = self.loadFramesFromDir(die_dir)
        self.attack_frames_pil = self.loadFramesFromDir(attack_dir)
        
        self.isFacingRight = True
        self.left_walking_frames_pil = [frame.transpose(Image.FLIP_LEFT_RIGHT) for frame in self.walking_frames_pil]
        self.left_idle_frames_pil = [frame.transpose(Image.FLIP_LEFT_RIGHT) for frame in self.idle_frames_pil]
        self.left_die_frames_pil = [frame.transpose(Image.FLIP_LEFT_RIGHT) for frame in self.die_frames_pil]
        self.left_attack_frames_pil = [frame.transpose(Image.FLIP_LEFT_RIGHT) for frame in self.attack_frames_pil]
        
        self.walking_frames = [CMUImage(frame) for frame in self.walking_frames_pil]
        self.idle_frames = [CMUImage(frame) for frame in self.idle_frames_pil]
        self.die_frames = [CMUImage(frame) for frame in self.die_frames_pil]
        self.attack_frames = [CMUImage(frame) for frame in self.attack_frames_pil]
        
        self.left_walking_frames = [CMUImage(frame) for frame in self.left_walking_frames_pil]
        self.left_idle_frames = [CMUImage(frame) for frame in self.left_idle_frames_pil]
        self.left_die_frames = [CMUImage(frame) for frame in self.left_die_frames_pil]
        self.left_attack_frames = [CMUImage(frame) for frame in self.left_attack_frames_pil]

    def loadFramesFromDir(self, directory):
        frames = []
        if os.path.exists(directory):
            files = [f for f in os.listdir(directory) if f.endswith('.gif')]
            files.sort(key=lambda x: int(x.split('.')[0]))
            
            for file in files:
                file_path = os.path.join(directory, file)
                try:
                    img = Image.open(file_path)
                    frames.append(img)
                except Exception as e:
                    pass
                    
        return frames

    def jump(self):
        if not self.isJumping and not self.isDead:
            self.isJumping = True
            self.yVelocity = self.jumpForce
    
    def duck(self):
        if not self.isJumping and not self.isDead:
            self.isDucking = True
            self.height = 40
            self.y = self.groundY - self.height
    
    def stopDucking(self):
        if self.isDucking:
            self.isDucking = False
            self.height = self.originalHeight
            self.y = self.groundY - self.height
    
    def attack(self):
        if not self.isDead and not self.isAttacking and self.total_fires_used < self.max_fire_count:
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
            
            # No immediate fire creation here - we'll create it after the delay
    
    def stopAttack(self):
        # Only stop the attack if the animation has completed
        if self.isAttacking and (self.attackComplete or not self.attackInProgress):
            self.isAttacking = False
            self.attackInProgress = False
            self.isRunning = True
            self.isIdle = False
            self.state_frame_index = 0
            
    def moveForward(self):
        if not self.isDead:
            self.x = self.x + self.moveD
            self.isFacingRight = True

            if self.x > self.app.width:
                self.x = self.app.width - 20

    def moveBack(self):
        if not self.isDead:
            self.x = self.x - self.moveD
            self.isFacingRight = False

            if self.x < 0:
                self.x = 0

    def update(self, events=None):
        # Animation update
        self.animationTimer += 1
        if self.animationTimer >= 10:  # Change animation frame every 5 game ticks
            self.animationTimer = 0
            self.state_frame_index = (self.state_frame_index + 1) % len(self.getStateFrames())
        
        # Handle jumping physics
        if self.isJumping:
            self.yVelocity += self.gravity
            self.y += self.yVelocity
            
            if self.y >= self.groundY - self.height:
                self.y = self.groundY - self.height
                self.isJumping = False
                self.yVelocity = 0
                self.isRunning = True

        # Handle death animation
        if self.isDeathAnimationPlaying:
            if self.animationTimer == 0:
                self.deathAnimationFrame += 1
                if self.deathAnimationFrame >= len(self.die_frames):
                    self.isDeathAnimationPlaying = False
                    self.deathAnimationComplete = True

        # Handle attack progress
        if self.isAttacking:
            self.attackTotalFrames += 1
            
            # Begin attack sequence if not already in progress
            if not self.attackInProgress and self.attackTotalFrames > 5:
                self.attackInProgress = True
                
            # Continue animation for full duration
            if self.attackTotalFrames > 30:  # Extended duration to allow fire release and complete animation
                self.isAttacking = False
                self.attackInProgress = False
                self.attackComplete = True
                self.isRunning = True
                
        # Fire delay timer
        if self.should_create_fire and self.isAttacking:
            self.fire_timer += 1
            if self.fire_timer >= self.fire_delay:
                self.should_create_fire = False
                self.create_fire()
                
        # Update active fires
        for fire in self.active_fires[:]:
            fire.update()
            if not fire.is_active:
                self.active_fires.remove(fire)
            
        # Reset CURRENT fire count if all fires are gone
        # This allows animation to play correctly but doesn't reset the total counter
        if len(self.active_fires) == 0:
            self.current_fire_count = 0

    def draw(self):        
        if self.isDead:
            self.drawDead()
        elif self.isAttacking:
            self.drawAttack()
        elif self.isJumping:
            self.drawJump()
        elif self.isIdle:
            self.drawIdle()
        else:
            self.isRunning = True
            self.drawRun()
            
        # Draw active fires
        for fire in self.active_fires:
            fire.draw()

    def drawRun(self):
        frameIndex = self.state_frame_index % len(self.walking_frames)
        
        if self.isFacingRight:
            drawImage(self.walking_frames[frameIndex], self.x, self.y, width=self.width, height=self.height, align='top-left')
        else:
            drawImage(self.left_walking_frames[frameIndex], self.x, self.y, width=self.width, height=self.height, align='top-left')

    def drawJump(self):
        if self.isFacingRight:
            drawImage(self.idle_frames[0], self.x, self.y, width=self.width, height=self.height, align='top-left')
        else:
            drawImage(self.left_idle_frames[0], self.x, self.y, width=self.width, height=self.height, align='top-left')

    def drawDuck(self):
        pass

    def drawDead(self):
        frameIndex = min(self.deathAnimationFrame, len(self.die_frames) - 1)
        if self.isFacingRight:
            drawImage(self.die_frames[frameIndex], self.x, self.y, width=self.width, height=self.height, align='top-left')
        else:
            drawImage(self.left_die_frames[frameIndex], self.x, self.y, width=self.width, height=self.height, align='top-left')

    def drawIdle(self):
        if len(self.idle_frames) == 0:
            return
            
        frameIndex = self.state_frame_index % len(self.idle_frames)
        
        if self.isFacingRight:
            drawImage(self.idle_frames[frameIndex], self.x, self.y, width=self.width, height=self.height, align='top-left')
        else:
            drawImage(self.left_idle_frames[frameIndex], self.x, self.y, width=self.width, height=self.height, align='top-left')
            
    def drawAttack(self):
        if len(self.attack_frames) == 0:
            self.drawRun()
            return
            
        # Make sure the frame index doesn't exceed the number of frames
        frameIndex = min(self.state_frame_index, len(self.attack_frames) - 1)
        
        # Draw a visual indicator for debugging (uncomment if needed)
        # drawLabel("ATTACK", self.x, self.y - 20, fill='red', bold=True)
        
        if self.isFacingRight:
            drawImage(self.attack_frames[frameIndex], self.x, self.y, width=self.width, height=self.height, align='top-left')
        else:
            drawImage(self.left_attack_frames[frameIndex], self.x, self.y, width=self.width, height=self.height, align='top-left')

    def startDeathAnimation(self):
        self.isDead = True
        self.isDeathAnimationPlaying = True
        self.deathAnimationFrame = 0
        self.deathAnimationComplete = False

    def isDeathAnimationFinished(self):
        return self.isDead and self.deathAnimationComplete

    def create_fire(self):
        # Create fire in front of dino
        direction = 1 if self.isFacingRight else -1
        mouth_x = self.x + (self.width * 0.2 if self.isFacingRight else self.width)
        mouth_y = self.y + (self.height * 0.4)  # Position near mouth
        
        fire = Fire(x=mouth_x, y=mouth_y, width=60, height=40, direction=direction)
        self.active_fires.append(fire)
        self.current_fire_count += 1
        self.total_fires_used += 1  # Increment permanent counter

    def getStateFrames(self):
        if self.isDead and len(self.die_frames) > 0:
            return self.die_frames if self.isFacingRight else self.left_die_frames
        elif self.isAttacking and len(self.attack_frames) > 0:
            return self.attack_frames if self.isFacingRight else self.left_attack_frames
        elif self.isIdle and len(self.idle_frames) > 0:
            return self.idle_frames if self.isFacingRight else self.left_idle_frames
        else:
            return self.walking_frames if self.isFacingRight else self.left_walking_frames


