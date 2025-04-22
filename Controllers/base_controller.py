class BaseController:
    def __init__(self, app):
        self.app = app
        self.model = app.model
        
        # Input state
        self.keysPressed = set()
        self.mouseX = 0
        self.mouseY = 0
        self.isMousePressed = False
        
    def handleKeyPress(self, key):
        self.keysPressed.add(key)
            
    def handleKeyHold(self, keys):
        self.keysPressed = set(keys)
    
    def handleKeyRelease(self, key):
        if key in self.keysPressed:
            self.keysPressed.remove(key)
            
    def handleMousePress(self, mouseX, mouseY):
        self.mouseX = mouseX
        self.mouseY = mouseY
        self.isMousePressed = True
        
    def handleMouseRelease(self, mouseX, mouseY):
        self.mouseX = mouseX
        self.mouseY = mouseY
        self.isMousePressed = False