import csv
import os

# to mitigate errors, 
# I'm creating a folder called assuming maybe it is not there
if not os.path.exists("data"):
    os.makedirs("data")

# files (form of a database)
LEVEL_1_FILE = "data/level_1.csv"
LEVEL_2_FILE = "data/level_2.csv"
BATTLE_FILE = "data/battle.csv"
HIGHSCORE_FILE = "data/highscore.csv"

# Default settings for Level 1
DEFAULT_LEVEL_1 = {
    "name": "Easy",
    "spawnInterval": 120,
    "cactusSpeed": 4,
    "birdSpeed": 5,
    "birdProbability": 0.3,
    "meteorProbability": 0.2,
    "birdCount": 1,
    "cactusCount": 1,
    "meteorCount": 1
}

# Default settings for Level 2 (Battle mode)
DEFAULT_LEVEL_2 = {
    "name": "Battle",
    "spawnInterval": 80,
    "cactusSpeed": 6,
    "birdSpeed": 7,
    "birdProbability": 0.5,
    "meteorProbability": 0.3,
    "birdCount": 15,
    "cactusCount": 15,
    "meteorCount": 15
}

# Default settings for Battle mode
DEFAULT_BATTLE = {
    "enemies_count": 3,
    "life": 100,
    "damage": 20,
    "enemy_fire_damage": 15,
    "player_fire_damage": 25,
    "spawn_interval": 300
}

# Create the level 1 settings file if it doesn't exist
def create_level_1_file():
    with open(LEVEL_1_FILE, "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["setting", "value"])
        for key, value in DEFAULT_LEVEL_1.items():
            writer.writerow([key, value])

# Create the level 2 settings file if it doesn't exist
def create_level_2_file():
    with open(LEVEL_2_FILE, "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["setting", "value"])
        for key, value in DEFAULT_LEVEL_2.items():
            writer.writerow([key, value])

# Create the battle settings file if it doesn't exist
def create_battle_file():
    with open(BATTLE_FILE, "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["setting", "value"])
        for key, value in DEFAULT_BATTLE.items():
            writer.writerow([key, value])

# Create the highscore file if it doesn't exist
def create_highscore_file():
    with open(HIGHSCORE_FILE, "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["highscore"])
        writer.writerow([0])

if not os.path.exists(LEVEL_1_FILE):
    create_level_1_file()

if not os.path.exists(LEVEL_2_FILE):
    create_level_2_file()

if not os.path.exists(BATTLE_FILE):
    create_battle_file()

if not os.path.exists(HIGHSCORE_FILE):
    create_highscore_file()

def get_level_settings(level=1):
    settings = DEFAULT_LEVEL_1.copy() if level == 1 else DEFAULT_LEVEL_2.copy()
    
    level_file = LEVEL_1_FILE if level == 1 else LEVEL_2_FILE
    
    with open(level_file, "r") as file:
        reader = csv.reader(file)
        next(reader)  
        
        for row in reader:
            if len(row) < 2:
                continue
                
            key = row[0]
            value = row[1]
            
            if key in ["spawnInterval", "cactusSpeed", "birdSpeed", 
                       "birdCount", "cactusCount", "meteorCount", "maxFireCount"]:
                settings[key] = float(value)
            elif key in ["birdProbability", "meteorProbability"]:
                settings[key] = float(value)
            else:
                settings[key] = value
        
    # Create the settings object 
    return {
        "name": settings["name"],
        "spawnInterval": settings["spawnInterval"],
        "baseSpeed": {
            "cactus": settings["cactusSpeed"],
            "bird": settings["birdSpeed"]
        },
        "birdProbability": settings["birdProbability"],
        "meteorProbability": settings["meteorProbability"],
        "birdCount": int(settings.get("birdCount", DEFAULT_LEVEL_1["birdCount"] if level == 1 else DEFAULT_LEVEL_2["birdCount"])),
        "cactusCount": int(settings.get("cactusCount", DEFAULT_LEVEL_1["cactusCount"] if level == 1 else DEFAULT_LEVEL_2["cactusCount"])),
        "meteorCount": int(settings.get("meteorCount", DEFAULT_LEVEL_1["meteorCount"] if level == 1 else DEFAULT_LEVEL_2["meteorCount"])),
        "maxFireCount": int(settings.get("maxFireCount", 3 if level == 1 else 5))
    }

# Get the high score
def get_highscore():
    with open(HIGHSCORE_FILE, "r") as file:
        reader = csv.reader(file)
        next(reader)  
        row = next(reader, None)
        if row:
            return int(float(row[0]))
    
    return 0  # Default highscore if not found

# Update the high score
def update_highscore(score):
    # Only update if the new score is higher
    current_score = get_highscore()
    if score <= current_score:
        return False
    
    with open(HIGHSCORE_FILE, "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["highscore"]) 
        writer.writerow([score])  
    return True 

def get_battle_settings():
    """Get enemy and battle settings"""
    settings = DEFAULT_BATTLE.copy()
    
    try:
        with open(BATTLE_FILE, "r") as file:
            reader = csv.reader(file)
            next(reader)  # Skip header
            
            for row in reader:
                if len(row) < 2:
                    continue
                    
                key = row[0].strip()
                value = row[1].strip()
                
                if key in ["enemies_count", "life", "damage", "enemy_fire_damage", "player_fire_damage", "spawn_interval"]:
                    settings[key] = int(value)
                else:
                    settings[key] = value
    except Exception as e:
        print(f"Error loading battle settings: {e}")
    
    return {
        "enemies_count": settings.get("enemies_count", 3),
        "life": settings.get("life", 100),
        "damage": settings.get("damage", 20),
        "enemy_fire_damage": settings.get("enemy_fire_damage", 15),
        "player_fire_damage": settings.get("player_fire_damage", 25),
        "spawn_interval": settings.get("spawn_interval", 300)
    } 