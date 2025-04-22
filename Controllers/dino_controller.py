class DinoController:
    def __init__(self, gameController):
        self.app = gameController.app
        self.model = gameController.model
        self.dino = self.model.dino
        
    def handleKeyPress(self, key):
        if key == 'up' or key == 'w':
            self.dino.jump()
        if key == 'down' or key == 's':
            self.dino.duck()
        if key == 'space' or key == 'x' or key == 'b':
            # Only trigger attack if not already attacking
            # Add safety checks for attributes
            is_attacking = getattr(self.dino, 'isAttacking', False)
            attack_in_progress = getattr(self.dino, 'attackInProgress', False)
            
            if not is_attacking and not attack_in_progress:
                self.dino.attack()
        if key == 'right' or key == 'd':
            self.dino.moveForward()
        if key == 'left' or key == 'a':
            self.dino.moveBack()
    
    def handleKeyHold(self, keys):
        if 'right' in keys or 'd' in keys:
            self.dino.moveForward()
        if 'left' in keys or 'a' in keys:
            self.dino.moveBack()
        if 'down' in keys or 's' in keys:
            self.dino.duck()
        # No attack on key hold - only on key press
    
    def handleKeyRelease(self, key):
        if key == 'down' or key == 's':
            self.dino.stopDucking()
        # Don't need to stop attack on key release - animation will complete naturally
        # if key == 'space' or key == 'x' or key == 'b' or key == 'a':
        #     self.dino.stopAttack()
    
    def update(self):
        self.dino.update()
            
        if self.dino.isDead:
            if self.dino.isDeathAnimationFinished():
                self.app.isGameOver = True
        elif self.model.checkCollisions():
            self.dino.startDeathAnimation()