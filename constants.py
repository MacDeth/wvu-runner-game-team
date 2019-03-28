# ---- Settings ----
WIDTH = 1000
HEIGHT = 500
FPS = 30
TITLE = "Trans-Allegheny Lunatic Asylum Escape"
FONT_NAME = 'arial'
HS_FILE = "CS475_Asylum_Progress.txt"
# When sprtiesheet is finished:
#SPRITE_FILE = ".png"

# Colors
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BROWN = (133, 87, 35)
YELLOW = (255, 204, 0)
GREEN = (11, 102, 35)
BLACK = (0, 0, 0)
SKY = (102, 178, 255)
GRAY = (49, 51, 53)
BGCOLOR = GRAY

# Player Sprite Parameters
PLAYER_ACC = 0.8
# PLAYER_FRICTION = -0.09
PLAYER_FRICTION = -0.06
PLAYER_GRAVITY = 1
PLAYER_JUMP = 26

# Power Up Boosts
BOOST_POWER = 30
POWER_SPAWN = 10

# Collide Object Spawn (Wheel Chairs, etc)
ENEMY_FREQ = 6000

# Managing Sprite Layering for when Drawn
BACK_ART_LAYER = 0
DOOR_LAYER = 1
PLATFORM_LAYER = 2
OBSTACLE_LAYER = 2
POWER_LAYER = 2
DARKNESS_LAYER = 3
PLAYER_LAYER = 3
FOREGROUND_ART_LAYER = 4

# Initial Screen Platforms (This can be moved, but they are used
# when a new game is made which occurs after entering a door)
PLATFORM_LIST = [(0, HEIGHT - 40),
                 (WIDTH / 2 - 50, HEIGHT * 3 / 4),
                 (125, HEIGHT - 350),
                 (350, 200),
                 (175, 100)]