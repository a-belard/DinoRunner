class GameModel:
    def __init__(self, app):
        self.app = app
        self.width = app.width
        self.height = app.height
        self.score = 0
        self.level = 1
        self.isPaused = False
        self.isGameOver = False

        self.groundColor = 'black'
        
    def update(self):
        pass

class GameObject:
    def __init__(self, x, y, width=20, height=20):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        
    def collidesWith(self, other):
        """Check if this object collides with another one"""
        return (abs(self.x - other.x) < (self.width + other.width) // 2 and
                abs(self.y - other.y) < (self.height + other.height) // 2)