from cmu_graphics import *
from Models.base_model import GameObject
from PIL import Image
import os

class Fire(GameObject):
    def __init__(self, x, y, width=60, height=40, direction=1, speed=8, distance=200, is_enemy=False):
        super().__init__(x, y, width, height)
        self.direction = direction
        self.animation_frame = 0
        self.is_active = True
        self.animation_speed = 3
        self.animation_timer = 0
        self.speed = speed
        self.start_x = x
        self.max_distance = distance
        self.is_enemy = is_enemy
        
        # Load fire frames
        self.loadFrames()
        
        # Position fire based on direction
        self.offsetX = 40 if direction > 0 else -40
        self.x += self.offsetX
        self.start_x = self.x
        
    def loadFrames(self):
        self.fire_frames = []
        fire_dir = 'assets/split_fire'
        
        if os.path.exists(fire_dir):
            files = [f for f in os.listdir(fire_dir) if f.endswith('.gif')]
            files.sort(key=lambda x: int(x.split('.')[0]) if x.split('.')[0].isdigit() else 0)
            
            for file in files:
                file_path = os.path.join(fire_dir, file)
                try:
                    image = Image.open(file_path)
                    
                    # Flip the image if facing left
                    if self.direction < 0:
                        image = image.transpose(Image.FLIP_LEFT_RIGHT)
                        
                    self.fire_frames.append(CMUImage(image))
                except Exception as e:
                    print(f"Error loading fire image: {e}")
        
        self.total_frames = len(self.fire_frames)
        print(f"Loaded {self.total_frames} fire frames")
    
    def update(self):
        self.animation_timer += 1
        
        # Move fire in the direction it's facing
        self.x += self.speed * self.direction
        
        # Deactivate if traveled too far
        current_distance = abs(self.x - self.start_x)
        if current_distance >= self.max_distance:
            self.is_active = False
        
        # Advance frame every animation_speed frames
        if self.animation_timer % self.animation_speed == 0:
            self.animation_frame += 1
            
            # Loop the animation while moving
            if self.animation_frame >= self.total_frames:
                self.animation_frame = 0
    
    def draw(self):
        if not self.is_active or len(self.fire_frames) == 0:
            return
        
        # Ensure frame index is valid
        frame_index = min(self.animation_frame, len(self.fire_frames) - 1)
        
        # Draw the fire - use red tint for enemy fire
        if self.is_enemy:
            # Draw with red tint for enemy fire
            drawImage(self.fire_frames[frame_index], self.x, self.y, 
                    width=self.width, height=self.height, align='center', opacity=100, 
                    rotateAngle=0) 
        else:
            # Normal fire for player
            drawImage(self.fire_frames[frame_index], self.x, self.y, 
                    width=self.width, height=self.height, align='center') 