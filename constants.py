# ---- Settings ----
import pygame

pygame.init()

WIDTH = 1280
HEIGHT = 720
FPS = 30
TITLE = "Trans-Allegheny Lunatic Asylum Escape"
FONT_NAME = 'syncopate'
HS_FILE = "CS475_Asylum_Progress.txt"

# IMAGE LOADING:
SPRITE_FILE = "Player.png"
START_IMG = 'AsylumHomeStart.jpg'
Death_IMG = 'AsylumHomeDeath.jpg'
DARKNESS_IMG = 'darkness.png'
DARKNESS2_IMG = 'darkness2.png'
DOOR_IMG = 'Door.png'
KEY_IMG = 'Key.png'
PLATFORM1_IMG = 'platform1.png'
PLATFORM2_IMG = 'platform2.png'
PLATFORM3_IMG = 'platform3.png'

# Level 1 Assets
#WARD1_IMG = 'Ward1.png'
#WARD2_IMG = 'Ward2.png'
BOOKCASE_IMG = 'BookCase.png'
LIGHT_IMG = 'light1.png'
LIGHT2_IMG = 'light2.png'
WHEELCHAIR_IMG = 'Wheelchair.png'
WHEELCHAIR_IMG2 = 'Wheelchair2.png'
STRETCHER_IMG = 'Stretcher.png'

# Colors
WHITE = (255, 255, 255)
RED = (255, 0, 0)
DARK_RED = (150, 0, 0)
BROWN = (133, 87, 35)
YELLOW = (255, 204, 0)
GREEN = (11, 102, 35)
BLACK = (0, 0, 0)
SKY = (102, 178, 255)
GRAY = (49, 51, 53)
BGCOLOR = WHITE

# Player Sprite Parameters
PLAYER_ACC = 0.9
# PLAYER_FRICTION = -0.09
PLAYER_FRICTION = -0.06
PLAYER_GRAVITY = 1
PLAYER_JUMP = 30

# Power Up Boosts
BOOST_POWER = 30
POWER_SPAWN = 10
COLLIDE_SPAWN = 10

# Key Spawn time, in milliseconds
LVL1_TIME_LIMIT = 60 * 1000 # a minute
LVL2_TIME_LIMIT = LVL1_TIME_LIMIT * 2 # two minutes
LVL3_TIME_LIMIT = LVL2_TIME_LIMIT * 2 # four minutes
KEY_RETRY = 10 * 1000 # ten seconds

# Managing Sprite Layering for when Drawn
BACK_ART_LAYER = 0
DOOR_LAYER = 1
PLATFORM_LAYER = 2
OBSTACLE_LAYER = 2
POWER_LAYER = 2
ENEMY_LAYER = 2
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
