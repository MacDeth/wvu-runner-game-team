# Trans-Allegheny Lunatic Asylum Semester Project
# CS 475
# First Pass: Skyler Roth
# Basic Side-Scrolling and 3 Level Selection

# Made in Python 3.6
import pygame as pg
import random
from os import path, listdir
from enum import Enum
from entities import *
from constants import *

class LevelState(Enum):
    LEVEL_SELECT = 1
    LEVEL_ONE = 2
    LEVEL_TWO = 3
    LEVEL_THREE = 4
    GAME_OVER = 5

class Game:
    def __init__(self):
        pg.init()
        pg.mixer.init()

        # make sure we start out on the level select screen
        self.level_state = LevelState.LEVEL_SELECT
        
        # Sprite groups
        self.all_sprites = pg.sprite.LayeredUpdates()
        self.platforms   = pg.sprite.Group()
        self.background  = pg.sprite.Group()
        self.powerups    = pg.sprite.Group() # includes key
        self.walls       = pg.sprite.Group()
        self.doors       = pg.sprite.Group()
        self.mobs        = pg.sprite.Group()
        self.lights      = pg.sprite.Group()
        self.screen      = pg.display.set_mode((WIDTH, HEIGHT))
        
        # Flag         Bit  Default
        # playing     = 9      0
        # running     = 8      1
        # interacting = 7      0
        # entering    = 6      0
        # door1_key   = 5      0
        # door2_key   = 4      0
        # door3_key   = 3      0
        # door1_fact  = 2      1
        # door2_fact  = 1      1
        # door3_fact  = 0      1
        self.flags = 263
        
        self.clock = pg.time.Clock()
        self.last_update = 0
        self.score = 0
        
        # Load assets scores and save
        self.load_data()
        
        # if the player has a controller
        self.controller = None
        if pg.joystick.get_count():
            pg.joystick.init()
            self.controller = pg.joystick.Joystick(0)
            self.controller.init()
            if self.controller.get_name().upper().strip() != 'USB Gamepad'.upper():
                self.controller = None
        
        # Title screen
        self.font_name = pg.font.match_font(FONT_NAME)
        pg.display.set_caption(TITLE)

    def load_data(self):
        # Load all assets, score, and save
        self.dir = path.dirname(__file__)
        img_dir = path.join(self.dir, 'img')

        # Create file to save the high score
        with open(path.join(self.dir, HS_FILE), 'r+') as file:
            try:
                self.highscore = int(file.read())
            except:
                self.highscore = 0
                
        # Background Object Image Loading:
        bckgrd_dir = path.join(img_dir, 'background')
        self.background_images = [pg.transform.scale(
            pg.image.load(path.join(bckgrd_dir, filename)).convert(),
            (WIDTH, HEIGHT + 50))
                                  for filename in listdir(bckgrd_dir)]
        
#         for i in range(1, 4):
#             self.background_images.append(pg.image.load(path.join(img_dir, '.png'.format(i))).convert())

        #Loading sound
        self.snd_dir = path.join(self.dir, 'sound')
        self.locked_sound = pg.mixer.Sound(path.join(self.snd_dir, 'locked.wav'))
        self.unlocked_sound = pg.mixer.Sound(path.join(self.snd_dir, 'opendoor.wav'))
        self.key_sound = pg.mixer.Sound(path.join(self.snd_dir, 'key.wav'))
        self.intro_sound = pg.mixer.Sound(path.join(self.snd_dir, 'intro_song.wav'))
        self.gameplay_sound = pg.mixer.Sound(path.join(self.snd_dir, 'gameplay_sound.wav'))
            
        # Loading Spritesheet Image
        self.spritesheet = Spritesheet(path.join(img_dir, SPRITE_FILE))

        # LOAD BACKGROUND IMAGES                                    
        self.start_img = pg.image.load(path.join(img_dir, START_IMG)).convert_alpha()
        self.start_img = pg.transform.scale(self.start_img, (1380, 1080))
        self.death_img = pg.image.load(path.join(img_dir, Death_IMG)).convert_alpha()
        self.death_img = pg.transform.scale(self.death_img, (1380, 1080))
        #self.ward1_img = pg.image.load(path.join(img_dir, WARD1_IMG)).convert_alpha()
        #self.ward2_img = pg.image.load(path.join(img_dir, WARD2_IMG)).convert_alpha()

        self.platform1_img = pg.image.load(path.join(img_dir, PLATFORM1_IMG)).convert_alpha()
        self.platform1_img = pg.transform.scale(self.platform1_img, (200, 50))
        self.platform2_img = pg.image.load(path.join(img_dir, PLATFORM2_IMG)).convert_alpha()
        self.platform2_img = pg.transform.scale(self.platform2_img, (200, 50))
        self.platform3_img = pg.image.load(path.join(img_dir, PLATFORM3_IMG)).convert_alpha()
        self.platform3_img = pg.transform.scale(self.platform3_img, (200, 50))

        self.bookcase_img = pg.image.load(path.join(img_dir, BOOKCASE_IMG)).convert_alpha()
        self.bookcase_img = pg.transform.scale(self.bookcase_img, (300, 250))

        self.wheelchair1_img = pg.image.load(path.join(img_dir, WHEELCHAIR_IMG)).convert_alpha()
        self.wheelchair1_img = pg.transform.scale(self.wheelchair1_img, (200, 200))

        self.wheelchair2_img = pg.image.load(path.join(img_dir, WHEELCHAIR_IMG2)).convert_alpha()
        self.wheelchair2_img = pg.transform.scale(self.wheelchair2_img, (150, 150))

        self.stretcher_img = pg.image.load(path.join(img_dir, STRETCHER_IMG)).convert_alpha()
        self.stretcher_img = pg.transform.scale(self.stretcher_img, (350, 200))

        self.light1_img = pg.image.load(path.join(img_dir, LIGHT_IMG)).convert_alpha()
        self.light1_img = pg.transform.scale(self.light1_img, (75, 125))

        self.light2_img = pg.image.load(path.join(img_dir, LIGHT2_IMG)).convert_alpha()
        self.light2_img = pg.transform.scale(self.light2_img, (75, 125))

        self.darkness_img = pg.image.load(path.join(img_dir, DARKNESS_IMG)).convert_alpha()
        self.darkness_img = pg.transform.scale(self.darkness_img, (WIDTH, HEIGHT))

        self.darkness2_img = pg.image.load(path.join(img_dir, DARKNESS2_IMG)).convert_alpha()
        self.darkness2_img = pg.transform.scale(self.darkness2_img, (WIDTH, HEIGHT))

        self.key_img = pg.image.load(path.join(img_dir, KEY_IMG)).convert_alpha()
        self.key_img = pg.transform.scale(self.key_img, (50, 100))
        
        self.door_img = pg.image.load(path.join(img_dir, DOOR_IMG)).convert_alpha()
        self.door_img = pg.transform.scale(self.door_img, (200, 350))


# --NEW-- AFTER ENTERING A ROOM NEW IS CALLED -> RUN -> EVENTS & UPDATE & DRAW
    def lvl_init(self):
        # Restart Game and Start Everything anew after entering a door
        self.score = 0
        self.all_sprites.empty()
        self.platforms.empty()
        self.powerups.empty()
        self.mobs.empty()
        self.lights.empty()
        self.background.empty()
        self.player = Player(self)

        # Initial Screen Platforms (Make this the area as soon as player enters door, before randomly generating level:
        for plat in PLATFORM_LIST:
            Platform(self, *plat)
        Darkness(self)
        Floor(self)
        # Mob timer will be needed to spawn objects needing jumped/slid over/under:
        # self.mob_timer = 0 # now handled by LVL1_ENEMY_PERIOD
        self.lvl_run()

    def lvl_run(self):
        # Game Loop
        # playing = True
        self.flags = self.flags | 512
        start_ticks = pg.time.get_ticks()
        
        # while playing
        while (self.flags & 512):
            self.clock.tick(FPS)
            self.process_events()
            self.lvl_update(start_ticks)
            self.draw()

    def lvl_update(self, start_ticks):
        # Game loop update
        # Update all content to be displayed to gamer
        self.all_sprites.update()
        
        # stuff won't spawn immediately if you've been playing for a while
        # if we subtract the amount of ticks when the game was started
        now = pg.time.get_ticks() - start_ticks

        # If we want to spawn additional objects to harm player:
        #if now % LVL1_ENEMY_PERIOD < 10: #- self.mob_timer > ENEMY_FREQ + random.choice([-1000, -500, 0, 500, 1000]):
            # self.mob_timer = now
        #    Obstacles(self)

        if (self.level_state == LevelState.LEVEL_ONE and \
                now >= LVL1_TIME_LIMIT and now % KEY_RETRY <= 45) or \
                (self.level_state == LevelState.LEVEL_TWO and \
                now >= LVL2_TIME_LIMIT and now % KEY_RETRY <= 45) or \
                (self.level_state == LevelState.LEVEL_THREE and \
                now >= LVL3_TIME_LIMIT and now % KEY_RETRY <= 45):
            Key(self, WIDTH, HEIGHT / 2)

        # Check for platform collisions while falling
        self.platform_collision()

        # If player reaches rightmost 1/2 of screen
        if self.player.rect.centerx >= WIDTH / 2:
            self.player.pos.x -= max(abs(self.player.vel.x), 2)
            for bck_obj in self.background:
                bck_obj.move((-max(abs(self.player.vel.x) / 2, 2), 0))
            for mob in self.mobs:
                mob.move((-max(abs(self.player.vel.x), 2), 0))
            for power in self.powerups:
                power.move((-max(abs(self.player.vel.x), 2), 0))
            for light in self.lights:
                light.rect.x -= max(abs(self.player.vel.x), 2)
                if light.rect.right < 0:
                    light.kill()
            for plat in self.platforms:
                plat.move((-max(abs(self.player.vel.x), 2), 0))
                plat.rect.x -= max(abs(self.player.vel.x), 2)
                if plat.rect.right < 0:
                    plat.kill()
                    self.score += 10

        # Darkness Collision
        mob_hits = pg.sprite.spritecollide(self.player, self.mobs, False)
        for e in mob_hits:
            # The only mobs that are on the platform layer are obstacles
            if e._layer == PLATFORM_LAYER:
                # change the state of the obstacle to "used"
                if not e.used:
                    self.player.vel.x -= BOOST_POWER #/ 2
                    if self.player.vel.x < 0:
                        self.player.vel.x = 0
                    e.used = True
            else: # it's an enemy mob
                self.level_state = LevelState.GAME_OVER
                # playing = False
                self.flags = self.flags & ~512
                break

        # Boost Collision
        pow_hits = pg.sprite.spritecollide(self.player, self.powerups, True)
        for pow in pow_hits:
            if pow.type == 'boost':
                self.player.vel.x = BOOST_POWER
                # Jumping through platforms when boosted will not snap to platform:
                self.player.jumping = False
            # TODO: perhaps don't immediately teleport the player to the level select
            elif pow.type == 'key': # they won the level by collecting a key
                if self.level_state == LevelState.LEVEL_ONE:
                    # collecting a key in lvl1 lets you enter lvl2
                    # door2_key = True 
                    self.flags = self.flags | 16
                elif self.level_state == LevelState.LEVEL_TWO:
                    # collecting a key in lvl2 lets you enter lvl3
                    # door3_key = true
                    self.flags = self.flags | 8 

                # bring them back to the level selection screen
                self.level_state = LevelState.LEVEL_SELECT
                
                # playing = False
                self.flags = self.flags & ~512
                return

        # Need lvl_init platforms

        while len(self.platforms) < 10:
            #width = random.randrange(50, 800)
            # More platformer like:
            #Platform(self, random.randrange(WIDTH, WIDTH + width), random.randrange(200, HEIGHT - 100))
            # More runner like:
            #Platform(self, WIDTH + 50, HEIGHT - 50)
            #More Consistent Spawning?
            #Platform(self, random.randrange(WIDTH - 200, WIDTH + width), random.randrange(200, HEIGHT - 100))
            width = random.randrange(WIDTH + 50, WIDTH * 2)
            height = random.randrange(200, HEIGHT - 50)
            flag = True
            for plat in self.platforms:
                if (width <= plat.rect.x + 200 and width >= plat.rect.x - 200):
                    if (height >= plat.rect.y + 100 or height <= plat.rect.y - 100):
                        continue #or (height <= plat.rect.y + 50 and height >= plat.rect.y - 50):
                    flag = False
                    break

            if flag:
                Platform(self,width,height)

        # Spawn background
        bckgrd_sprites = self.background.sprites()
        
        # Initial background
        if len(bckgrd_sprites) is 0:
            bckgrd = Background(self)
            bckgrd.rect.x = 0
            bckgrd.pos.x = 0.0

        # Subsequent Backgrounds
        if len(self.background) < 2:
            Background(self)

        # Need new lights
        while len(self.lights) < 1:
            Light(self, random.randrange(WIDTH + 100, 2 * WIDTH), random.randrange(0, 80))

        # Player Falls off Screen
        if self.player.rect.bottom > HEIGHT:
            for sprite in self.all_sprites:
                sprite.rect.y -= max(self.player.vel.y, 10)
                if sprite.rect.bottom > 0:
                    sprite.kill()
        if len(self.platforms) == 0:
            self.level_state = LevelState.GAME_OVER
            # playing = False
            self.flags = self.flags & ~512

# --LEVEL SELECT-- ROOM WITH 3 DOORS TO CHOOSE. LEVEL_SELECT IS CALLED ->
    # LVL_SELECT_RUN -> EVENTS & LVL_SELECT_UPDATE & LVL_SELECT_DRAW
    def lvl_select_init(self):
        self.all_sprites.empty()
        self.platforms.empty()
        self.background.empty()
        self.powerups.empty()
        self.walls.empty()
        self.doors.empty()
        self.lights.empty()
        self.player = Player(self)

        # Draw central room with three doors to choose from:
        # Choosing doors in an inefficient way:
        # door1_key
        if not (self.flags & 32):
            # If key 1 not picked up, draw it in central room:
            Key(self, WIDTH / 2, HEIGHT / 8 + 100)

        Door(self, WIDTH / 8, HEIGHT - 25, 1, (self.flags & 32) is 32) # door1_key
        Door(self, WIDTH / 2, HEIGHT - 25, 2, (self.flags & 16) is 16) # door2_key
        Door(self, WIDTH - 100, HEIGHT - 25, 3, (self.flags & 8) is 8) #door3_key
        Wall(self, -225)
        Wall(self, WIDTH + 225)
        Floor(self)

        self.lvl_select_run()

    def lvl_select_run(self):
        # Game Loop
        # playing = True
        self.flags = self.flags | 512
        
        # while playing
        while (self.flags & 512):
            self.clock.tick(FPS)
            self.process_events()
            self.lvl_select_update()
            
            # not playing
            if not (self.flags & 512):
                break
            self.draw()

    def lvl_select_update(self):
        # Game loop update
        # Update all content to be displayed to gamer
        self.all_sprites.update()

        # Key Collision
        key_hits = pg.sprite.spritecollide(self.player, self.powerups, True)
        if key_hits:
            # door1_key = True
            self.flags = self.flags | 32
            self.key_sound.play()

        # With key player enters door, if correct key permits:
        door_hits = pg.sprite.spritecollide(self.player, self.doors, False)
        
        # door_hits is truthy and self.interacting == true
        if door_hits and (self.flags & 128):
            for door in door_hits:
                if door.number == 1 and (self.flags & 32): # door1_key
                    door.locked = False
                elif door.number == 2 and (self.flags & 16): # door2_key
                    door.locked = False
                elif door.number == 3 and (self.flags & 8): # door3_key
                    door.locked = False
                    
        # door_hits is truthy and entering == true
        if door_hits and (self.flags & 64):
            for door in door_hits:
                if not door.locked:
                    self.unlocked_sound.play()
                    if door.number == 1:
                        # door1_fact
                        if (self.flags & 4):
                            self.door_screen("Door 1 Random Facts and History.")
                        
                        # door1_fact = False
                        self.flags = self.flags & ~4
                        
                        # entering = False
                        self.flags = self.flags & ~64
                        self.level_state = LevelState.LEVEL_ONE
                    elif door.number == 2:
                        # door2_fact
                        if (self.flags & 2):
                            self.door_screen("Door 2 Random Facts and History.")
                        # door2_fact = False
                        self.flags = self.flags & ~2
                        
                        # entering = False
                        self.flags = self.flags & ~64
                        self.level_state = LevelState.LEVEL_TWO
                    elif door.number == 3:
                        # door3_fact
                        if (self.flags & 1):
                            self.door_screen("Door 3 Random Facts and History.")
                        # door3_fact = False
                        self.flags = self.flags & ~1
                        
                        # entering = False
                        self.flags = self.flags & ~64
                        self.level_state = LevelState.LEVEL_THREE
                    # playing = False
                    self.flags = self.flags & ~512

        # Check for wall interaction:
        wall_hits = pg.sprite.spritecollide(self.player, self.walls, False)
        if wall_hits:
            if self.player.rect.x < WIDTH / 2:
                self.player.acc.x = 0
                self.player.vel.x = 0
                self.player.rect.left = wall_hits[0].rect.right
                self.player.pos = vec(self.player.rect.midbottom)
            else:
                self.player.acc.x = 0
                self.player.vel.x = 0
                self.player.rect.right = wall_hits[0].rect.left
                self.player.pos = vec(self.player.rect.midbottom)

        # Check for platform collisions while falling
        # TODO: May want platforms in main area?
        self.platform_collision()

        # The following results in some weird effects with the walls and floor moving incorrectly, something to look into later:
        # If player reaches rightmost 1/3 of screen
        if self.player.rect.centerx >= WIDTH * 3/4:
            self.player.pos.x -= max(abs(self.player.vel.x), 2)
            for bck_obj in self.background:
                bck_obj.move((-max(abs(self.player.vel.x) / 2, 2), 0))
            for plat in self.platforms:
                plat.move((-max(abs(self.player.vel.x), 2), 0))
            for door in self.doors:
                door.move((-max(abs(self.player.vel.x), 2), 0))
            for power in self.powerups:
                power.move((-max(abs(self.player.vel.x), 2), 0))
            for wall in self.walls:
                wall.move((-max(abs(self.player.vel.x), 2), 0))
            for light in self.lights:
                light.move((-max(abs(self.player.vel.x), 2), 0))

        # If player reaches leftmost 1/4 of screen
        if self.player.rect.centerx <= WIDTH / 4:
            self.player.pos.x += max(abs(self.player.vel.x), 2)
            for bck_obj in self.background:
                bck_obj.move((max(abs(self.player.vel.x) / 2, 2), 0))
            for plat in self.platforms:
                plat.move((max(abs(self.player.vel.x), 2), 0))
            for door in self.doors:
                door.move((max(abs(self.player.vel.x), 2), 0))
            for power in self.powerups:
                power.move((max(abs(self.player.vel.x), 2), 0))
            for wall in self.walls:
                wall.move((max(abs(self.player.vel.x), 2), 0))
            for light in self.lights:
                light.move((-max(abs(self.player.vel.x), 2), 0))

        # Player Falls off Screen
        if self.player.rect.bottom - 50 > HEIGHT:
            for sprite in self.all_sprites:
                sprite.rect.y -= max(self.player.vel.y, 10)
                if sprite.rect.bottom > 0:
                    sprite.kill()
        if len(self.platforms) == 0:
            self.level_state = LevelState.GAME_OVER
            # playing = False
            self.flags = self.flags & ~512

    def process_events(self):
        # Game loop process_events
        for event in pg.event.get():
            # Jumping ability Check
            # Controller
            if event.type == pg.JOYBUTTONDOWN:
                if event.button == controller.BUTTON_A:
                    self.player.jump()
            
            # Keyboard
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_UP:
                    self.player.jump()
                    
            # Jump can be controlled, little to big jump
            # Controller
            if event.type == pg.JOYBUTTONUP:
                if event.button == controller.BUTTON_A:
                    self.player.jump_stop()
            
            # Keyboard
            if event.type == pg.KEYUP:
                if event.key == pg.K_UP:
                    self.player.jump_stop()

            # Slide Check
            # Controller
            if event.type == pg.JOYBUTTONDOWN:
                if event.button == controller.BUTTON_B:
                    self.player.slide()
                    
            if event.type == pg.JOYBUTTONUP:
                if event.button == controller.BUTTON_B:
                    self.player.slide_stop()
            
            # Keyboard
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_DOWN:
                    self.player.slide()

            if event.type == pg.KEYUP:
                if event.key == pg.K_DOWN:
                    self.player.slide_stop()

            # Check for quitting game event:
            if event.type == pg.QUIT:
                # playing = False
                self.flags = self.flags & ~512
                
                # Running flag = false
                self.flags = self.flags & ~256 

            # Check for interacting:
            # Controller
            if event.type == pg.JOYBUTTONDOWN:
                if event.button == controller.BUTTON_Y:
                    # interacting = true
                    self.flags = self.flags | 128
                    
            if event.type == pg.JOYBUTTONUP:
                if event.button == controller.BUTTON_Y:
                    # interacting = false
                    self.flags = self.flags & ~128
                    
            # Keyboard
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_i:
                    # interacting = true
                    self.flags = self.flags | 128

            if event.type == pg.KEYUP:
                if event.key == pg.K_i:
                    # interacting = false
                    self.flags = self.flags & ~128

            # Check for entering:
            # Controller
            if event.type == pg.JOYBUTTONDOWN:
                if event.button == controller.BUTTON_X:
                    # entering = True
                    self.flags = self.flags | 64
                    
            if event.type == pg.JOYBUTTONUP:
                if event.button == controller.BUTTON_X:
                    # entering = False
                    self.flags = self.flags & ~64
                    
            # Keyboard
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_e:
                    # entering = True
                    self.flags = self.flags | 64

            if event.type == pg.KEYUP:
                if event.key == pg.K_e:
                    # entering = False
                    self.flags = self.flags & ~64

    def draw(self):
        # Draw background and sprites:
        self.screen.fill(BGCOLOR)
        self.all_sprites.draw(self.screen)
        #self.draw_text(str(self.score), 22, BLACK, WIDTH / 2, 15)
        
        # Doors for level select
        if self.doors:
            door_hits = pg.sprite.spritecollide(self.player, self.doors, False)
            # door_hits is truthy and self.interacting == true
            if door_hits and (self.flags & 128):
                for door in door_hits:
                    if door.locked:
                        self.locked_sound.play()
                        self.draw_text("Locked.", 22, BLACK, door.rect.centerx, door.rect.bottom - 350)
                    else:
                        self.draw_text("Unlocked. E to Enter", 22, BLACK, door.rect.centerx, door.rect.bottom - 350)
        
        # Flip display after drawing:
        pg.display.flip()

    def start_screen(self):
        # Start up screen
        self.screen.blit(self.start_img, [-25, -80])
        self.draw_text('ASYLUM      ESCAPE', 150, GRAY, WIDTH / 2, HEIGHT / 8)
        #self.draw_text("Left & Right Arrow Keys to Move & Up Arrow Key to Jump", 22, GRAY, WIDTH / 2, HEIGHT / 2)
        #self.draw_text("Down Arrow Key to Slide & i to Interact", 22, GRAY, WIDTH / 2, HEIGHT / 2 + 50)
        self.draw_text("Use Any Key to Enter!", 22, GRAY, WIDTH / 2, HEIGHT / 8 + 110)
        self.draw_text("High Score: " + str(self.highscore), 22, GRAY, WIDTH / 2, 15)
        pg.display.flip()
        pg.mixer.music.load(path.join(self.snd_dir, 'intro_song.wav'))
        pg.mixer.music.play(loops=-1)
        self.wait_for_key()

    def intro_screen(self):
        # After start screen.
        pg.mixer.music.load(path.join(self.snd_dir, 'gameplay_sound.wav'))
        pg.mixer.music.play(loops=-1)
        self.screen.fill(BGCOLOR)
        self.draw_text("You took the dare to explore the building knowing it is off limits.", 22, BLACK, WIDTH / 2, HEIGHT / 2 - 25)
        self.draw_text("Upon entering, the floor gave and you fell into a room of three doors.", 22, BLACK, WIDTH / 2, HEIGHT / 2)
        self.draw_text(" You think it best to look for a way out... you hear something lurking in the distance.", 22, BLACK, WIDTH / 2, HEIGHT / 2 + 25)
        self.draw_text("Press Any Key to Continue!", 16, BLACK, WIDTH / 2, HEIGHT * 3 / 4)
        pg.display.flip()
        self.wait_for_key()

    def door_screen(self, facts):
        # After start screen introduction.
        self.screen.fill(BGCOLOR)
        self.draw_text(facts, 22, BLACK, WIDTH / 2, HEIGHT / 2 - 25)
        self.draw_text("Press Any Key to Continue!", 16, BLACK, WIDTH / 2, HEIGHT * 3 / 4)
        pg.display.flip()
        self.wait_for_key()

    def game_over_screen(self):
        # Game over screen only if you lose, not if you close program
        if not (self.flags & 256):
            # Player Closed Application, so skip the Game Over screen
            return

        self.level_state = LevelState.LEVEL_SELECT
        pg.mixer.music.load(path.join(self.snd_dir, 'intro_song.wav'))
        pg.mixer.music.play(loops=-1)
        self.screen.blit(self.death_img, [-25, -80])
        self.draw_text('YOU ARE TRAPPED', 100, WHITE, WIDTH / 2, HEIGHT / 8)
        self.draw_text("SCORE: " + str(self.score), 22, WHITE, WIDTH / 2, HEIGHT / 4 + 25)
        self.draw_text("Want to Run Again?                                                   "
                       '                Use Any Key to Play Again', 22, WHITE, WIDTH / 2, HEIGHT / 6 + 50)
        if self.score > self.highscore:
            self.highscore = self.score
            self.draw_text("You Almost Escaped!", 35, WHITE, WIDTH / 2, HEIGHT / 4 + 95)
            with open(path.join(self.dir, HS_FILE), 'r+') as file:
                file.write(str(self.score) + '\n')
        else:
            self.draw_text("High Score: " + str(self.highscore), 22, WHITE, WIDTH / 2, HEIGHT / 4 + 95)
        pg.display.flip()
        self.wait_for_key()
        pg.mixer.music.load(path.join(self.snd_dir, 'gameplay_sound.wav'))
        pg.mixer.music.play(loops=-1)

    def wait_for_key(self):
        pg.event.wait()
        waiting = True
        while waiting:
            self.clock.tick(FPS)
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    waiting = False
                    # Running = false
                    self.flags = self.flags & ~256
                if event.type == pg.KEYDOWN:
                    waiting = False
                if event.type == pg.JOYBUTTONDOWN:
                    waiting = False

    def draw_text(self, text, size, color, xpos, ypos):
        font = pg.font.Font(self.font_name, size)
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect()
        text_rect.midtop = (xpos, ypos)
        self.screen.blit(text_surface, text_rect)

    def platform_collision(self):
        if self.player.vel.y > 0:
            hits = pg.sprite.spritecollide(self.player, self.platforms, False)
            if hits:
                lower_platform = hits[0]
                for hit in hits:
                    if hit.rect.bottom > lower_platform.rect.bottom:
                        lower_platform = hit
                if self.player.pos.x < lower_platform.rect.right + 100 and self.player.pos.x > lower_platform.rect.left - 100:
                    # Only move to platform top if feet higher than platform top
                    if self.player.pos.y <= lower_platform.rect.bottom:
                        self.player.pos.y = lower_platform.rect.top + 1
                        self.player.rect.midbottom = self.player.pos
                        self.player.vel.y = 0
                        self.player.jumping = False

def main():
    # If the highscore file doesn't exist, create it.
    if not path.exists(HS_FILE):
        with open(HS_FILE, 'w') as file:
            file.write('0\n')

    # --CREATE GAME AND GO THROUGH EVENTS--
    g = Game()
    if (g.flags & 256):
        g.start_screen()
    
    if (g.flags & 256):
        g.intro_screen()
        
    while (g.flags & 256):
        if g.level_state == LevelState.LEVEL_SELECT:
            g.lvl_select_init()
        elif g.level_state == LevelState.LEVEL_ONE or \
                g.level_state == LevelState.LEVEL_TWO or \
                g.level_state == LevelState.LEVEL_THREE:
            g.lvl_init()
        elif g.level_state == LevelState.GAME_OVER:
            g.game_over_screen()

        # g.lvl_select_init()
        # if not g.running:
        #     break
        # g.lvl_init()
        # g.game_over_screen()

        if not (g.flags & 256):
            break

    pg.quit()

if __name__ == '__main__':
    main()
