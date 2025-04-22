from Models.enemy_dino import EnemyDino
import Models.database_manager as db
import random

class EnemyManager:
    def __init__(self, app):
        self.app = app
        self.enemies = []
        
        # Load battle settings
        self.settings = db.get_battle_settings()
        
        # Spawn enemies based on settings
        self.max_enemies = self.settings.get('enemies_count', 3)
        self.enemy_health = self.settings.get('life', 100)
        self.player_fire_damage = self.settings.get('player_fire_damage', 25)
        self.enemy_fire_damage = self.settings.get('enemy_fire_damage', 15)
        self.enemy_damage = self.settings.get('damage', 20)
        
        # Initialize tracking variables
        self.enemies_defeated = 0
        self.spawn_timer = 0
        self.spawn_interval = self.settings.get('spawn_interval', 300)
        
        print(f"EnemyManager initialized with app.level={app.level}")
        
        # Spawn first enemy immediately if in level 2
        if app.level == 2:
            print("Level 2 detected! Spawning initial enemy...")
            self.spawn_enemy()
    
    def update(self):
        # Skip if not in battle mode (level 2)
        if self.app.level != 2:
            return
        
        # Check if we need to spawn first enemy - this helps when switching levels
        if len(self.enemies) == 0 and self.enemies_defeated == 0:
            print("No enemies present in level 2! Spawning initial enemy...")
            self.spawn_enemy()
            
        # Update existing enemies and track ones to remove
        enemies_to_remove = []
        
        for enemy in self.enemies:
            enemy.update()
            
            # Check for defeated enemies
            if enemy.isDead and enemy.isDeathAnimationFinished():
                # Mark for removal instead of removing directly to avoid modifying list during iteration
                enemies_to_remove.append(enemy)
        
        # Remove dead enemies outside the loop
        for enemy in enemies_to_remove:
            if enemy in self.enemies:
                self.enemies.remove(enemy)
                self.enemies_defeated += 1
                print("here", enemy)

        
        # Spawn new enemies if needed
        self.spawn_timer += 1
        if (self.spawn_timer >= self.spawn_interval and 
                len(self.enemies) < self.max_enemies and
                self.enemies_defeated + len(self.enemies) < self.max_enemies):
            self.spawn_enemy()
            self.spawn_timer = 0
        elif self.spawn_timer % 60 == 0:
            print(f"Waiting to spawn enemy: timer={self.spawn_timer}/{self.spawn_interval}, " +
                  f"enemies={len(self.enemies)}/{self.max_enemies}, " +
                  f"total={self.enemies_defeated + len(self.enemies)}/{self.max_enemies}")
    
    def spawn_enemy(self):
        # Position visibly on the right side of the screen
        # Place 80% of the way across the screen, not offscreen
        x = int(self.app.width * 0.8)
        y = self.app.groundY - 70
        
        enemy = EnemyDino(self.app, x, y)
        enemy.maxHealth = self.enemy_health
        enemy.health = enemy.maxHealth
        enemy.damage = self.enemy_damage
        
        self.enemies.append(enemy)
        print(f"Spawned enemy at ({x}, {y}) with health {enemy.health}/{enemy.maxHealth}")
        print(f"Current enemy count: {len(self.enemies)}, app.level={self.app.level}")
        print(f"Enemy direction: facing {'right' if enemy.isFacingRight else 'left'}")
        
        # Check if enemy is initialized correctly
        if hasattr(enemy, 'walking_frames') and len(enemy.walking_frames) > 0:
            print(f"Enemy has {len(enemy.walking_frames)} walking frames")
        else:
            print("Warning: Enemy has no walking frames")
    
    def check_collision_with_fires(self, fires):
        for enemy in self.enemies:
            for fire in fires:
                if fire.is_active and self.check_fire_collision(fire, enemy):
                    # Damage enemy and deactivate fire
                    enemy.takeDamage(self.player_fire_damage)
                    fire.is_active = False
                    print(f"Enemy hit! Health: {enemy.health}/{enemy.maxHealth}")
    
    def check_fire_collision(self, fire, enemy):
        # Simple rectangle collision check
        fireLeft = fire.x - fire.width/2
        fireRight = fire.x + fire.width/2
        fireTop = fire.y - fire.height/2
        fireBottom = fire.y + fire.height/2
        
        enemyLeft = enemy.x
        enemyRight = enemy.x + enemy.width
        enemyTop = enemy.y
        enemyBottom = enemy.y + enemy.height
        
        # Check for overlap
        if (fireRight >= enemyLeft and 
            fireLeft <= enemyRight and
            fireBottom >= enemyTop and
            fireTop <= enemyBottom):
            return True
            
        return False
    
    def check_collision_with_player(self, player):
        for enemy in self.enemies:
            # Skip if enemy is dead
            if enemy.isDead:
                continue
                
            # Only check collision during attack state
            if enemy.state == "attack":
                # Simple rectangle collision
                if (player.x < enemy.x + enemy.width and
                    player.x + player.width > enemy.x and
                    player.y < enemy.y + enemy.height and
                    player.y + player.height > enemy.y):
                    
                    # Check if enemy is actively attacking (has fires)
                    if len(enemy.active_fires) > 0:
                        # Damage player based on enemy's damage value
                        if hasattr(player, 'takeDamage'):
                            player.takeDamage(enemy.damage)
    
    def draw(self):
        for enemy in self.enemies:
            enemy.draw()
    
    def all_enemies_defeated(self):
        return self.enemies_defeated >= self.max_enemies and len(self.enemies) == 0 
        
    def reset_enemies(self):
        """Reset the enemy manager state when starting a new game or level"""
        # Clear all existing enemies
        self.enemies = []
        
        # Reset counters
        self.enemies_defeated = 0
        self.spawn_timer = 0
        
        # Reload settings in case they changed
        self.settings = db.get_battle_settings()
        self.max_enemies = self.settings.get('enemies_count', 3)
        self.enemy_health = self.settings.get('life', 100)
        self.player_fire_damage = self.settings.get('player_fire_damage', 25)
        self.enemy_fire_damage = self.settings.get('enemy_fire_damage', 15)
        self.enemy_damage = self.settings.get('damage', 20)
        self.spawn_interval = self.settings.get('spawn_interval', 300)
        
        # Spawn initial enemy if in level 2
        if self.app.level == 2:
            self.spawn_enemy() 