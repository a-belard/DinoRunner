from cmu_graphics import drawImage, drawLabel, CMUImage
from PIL import Image

class KeyButton:
    def __init__(self, key: str, x, y, width=50, height=50):
        self.width = width
        self.height = height
        self.x = x
        self.y = y
        self.key = key
        img = Image.open("assets/key.png")
        self.image = CMUImage(img)

    def draw(self):
        drawImage(self.image, self.x, self.y, width=self.width, height=self.height, align='center')
        drawLabel(self.key, self.x, self.y, size=self.width * 0.5, fill='black', align='center', bold=True)

    
    