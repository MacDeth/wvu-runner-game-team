# Trans-Allegheny Lunatic Asylum Semester Project
# CS 475
# First Pass: Skyler Roth
# Basic Side-Scrolling and 3 Level Selection

# Made in Python 3.6
import pygame as pg
import random
from os import path


# Vector for player movement
vec = pg.math.Vector2

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
POWER_LAYER = 2
ENEMY_LAYER = 3
PLAYER_LAYER = 3
FOREGROUND_ART_LAYER = 4

# Initial Screen Platforms (This can be moved, but they are used
# when a new game is made which occurs after entering a door)
PLATFORM_LIST = [(0, HEIGHT - 40),
                 (WIDTH / 2 - 50, HEIGHT * 3 / 4),
                 (125, HEIGHT - 350),
                 (350, 200),
                 (175, 100)]


class Spritesheet(pg.sprite.Sprite):
    # Load the sprite sheet PNG
    def __init__(self, filename):
        self.spritesheet = pg.image.load(filename).convert()

    def get_image(self, x, y, width, height):
        # Grab PNG images:
        image = pg.Surface((width, height))
        image.blit(self.spritesheet, (0, 0), (x, y, width, height))
        # Can scale sprites to get a certain aspect ratio:
        image = pg.transform.scale(image, (width // 2, height // 2))
        return image

    def get_raw_image(self, x, y, width, height):
        # Grab PNG images without scaling:
        image = pg.Surface((width, height))
        image.blit(self.spritesheet, (0, 0), (x, y, width, height))
        return image


class Player(pg.sprite.Sprite):
    def __init__(self, game):
        # Set Player Sprite Layer
        self._layer = PLAYER_LAYER
        self.groups = game.all_sprites
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game

        # Make the player a basic yellow rectangle
        self.image = pg.Surface((50, 100))
        self.image.fill(YELLOW)

        # Boolean States Used for Determining Animation States
        self.walking = False
        self.jumping = False
        self.current_frame = 0
        self.last_update = 0

        # Use Load Image when Spritesheet is Done
        #self.load_images()
        #self.image = self.standing_frames[0]
        self.rect = self.image.get_rect()

        # Position, Velocity, and Acceleration Vectors for Movement
        self.pos = vec(WIDTH / 2, HEIGHT / 2)
        self.vel = vec(0, 0)
        self.acc = vec(0, 0)

    def load_images(self):
        # Load Image Sheets and then Pass Them to "get_image" for specific frame extraction
        # Standing Animation
        self.standing_frames = [self.game.spritesheet.get_image(0, 50, 200, 120),
                                self.game.spritesheet.get_image(200, 50, 200, 120),
                                self.game.spritesheet.get_image(400, 50, 200, 120)]
        for frame in self.standing_frames:
            frame.set_colorkey(0)

        # Walking Animation
        self.walking_frames_l = [self.game.spritesheet.get_image(0, 250, 200, 120),
                                 self.game.spritesheet.get_image(200, 250, 200, 120)]
        self.walking_frames_r = []
        for frame in self.walking_frames_l:
            frame.set_colorkey(BLACK)
            # Only draw one half of walking right animation and then flip it for left animation:
            self.walking_frames_r.append(pg.transform.flip(frame, True, False))

        # Jumping Animation
        self.jump_frames_l = self.game.spritesheet.get_image(400, 600, 200, 180)
        self.jump_frames_r = pg.transform.flip(self.jump_frames_l, True, False)
        self.jump_frames_l.set_colorkey(0)
        self.jump_frames_r.set_colorkey(0)

    def jump(self):
        # Jump Only if Platform Collision
        # The following sets the x position the player is moved to upon collision, had weird bouncing issues when using sprites but unnecessary for box
        self.rect.x -= 2
        hits = pg.sprite.spritecollide(self, self.game.platforms, False)
        self.rect.x += 2

        if hits and not self.jumping:
            self.jumping = True
            self.vel.y = -PLAYER_JUMP

    def jump_stop(self):
        if self.jumping:
            if self.vel.y < -8:
                self.vel.y = -8;

    def slide(self):
        self.image = pg.Surface((100, 50))
        self.image.fill(YELLOW)
        self.rect = self.image.get_rect()

    def slide_stop(self):
        self.image = pg.Surface((50, 100))
        self.image.fill(YELLOW)
        self.rect = self.image.get_rect()

    def update(self):
        self.animate()
        self.acc = vec(0, PLAYER_GRAVITY)
        keys = pg.key.get_pressed()
        if keys[pg.K_LEFT]:
            self.acc.x = -PLAYER_ACC
        if keys[pg.K_RIGHT]:
            self.acc.x = PLAYER_ACC

        # Moving the sprite
        # Factor in friction X Direction
        self.acc.x += self.vel.x * PLAYER_FRICTION
        self.vel += self.acc

        # Return to idle animation:
        # If velocity is small, then set it to 0
        if abs(self.vel.x) < 0.1:
            self.vel.x = 0

        self.pos += self.vel + 0.5 * self.acc
        # Update Drawn Position
        # No off screen sprite
        #if self.pos.x > WIDTH + self.rect.width / 2:
        #    self.pos.x = 0 - self.rect.width / 2
        #if self.pos.x < 0 - self.rect.width / 2:
        #    self.pos.x = WIDTH + self.rect.width / 2
        self.rect.midbottom = self.pos


    def animate(self):
        '''
        now = pg.time.get_ticks()
        if self.vel.x != 0:
            self.walking = True
        else:
            self.walking = False

        # Walking Time
        if self.walking:
            # 200 is arbitrarily chosen, depending on #frames in spritesheet
            if now - self.last_update > 200:
                self.last_update = now
                self.current_frame = (self.current_frame + 1) % len(self.walking_frames_l)
                bottom = self.rect.bottom
                if self.vel.x > 0:
                    self.image = self.walking_frames_r[self.current_frame]
                else:
                    self.image = self.walking_frames_l[self.current_frame]
                self.rect = self.image.get_rect()
                self.rect.bottom = bottom

        # Jumping Time
        if self.jumping:
            if now - self.last_update > 188:
                self.last_update = now
                # self.current_frame = (self.current_frame + 1) % len(self.walking_frames_l)
                bottom = self.rect.bottom
                if self.vel.x > 0 and self.vel.y < 0:
                    self.image = self.jump_frames_r
                elif self.vel.x < 0 and self.vel.y < 0:
                    self.image = self.jump_frames_l
                else:
                    self.image = self.standing_frames[0]
                self.rect = self.image.get_rect()
                self.rect.bottom = bottom

        if not self.jumping and not self.walking:
            if now - self.last_update > 350:
                self.last_update = now
                self.current_frame = (self.current_frame + 1) % len(self.standing_frames)
                bottom = self.rect.bottom
                self.image = self.standing_frames[self.current_frame]
                self.rect = self.image.get_rect()
                self.rect.bottom = bottom
                '''
        # More accurate collision mask for player
        self.mask = pg.mask.from_surface(self.image)


# Background Image Objects that you want to move through background
class Background(pg.sprite.Sprite):
    def __init__(self, game):
        self._layer = BACK_ART_LAYER
        self.groups = game.all_sprites, game.background
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        # Choose a random background object to display, use when sprites are done
        #self.image = random.choice(self.game.web_images)
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        # My background images were 800 x 800 and I wanted them aligned to the square game field:
        self.rect.x = 0
        self.rect.y = -800

    def update(self):
        # If the top of background objects go off the screen, remove them.
        if self.rect.right < 0:
            self.kill()


class Platform(pg.sprite.Sprite):
    def __init__(self, game, x, y):
        self._layer = PLATFORM_LAYER
        self.groups = game.all_sprites, game.platforms
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        # Use when sprites are available
        '''
        images = [self.game.spritesheet.get_image(400, 200, 200, 60),
                  self.game.spritesheet.get_image(600, 200, 200, 90),
                  self.game.spritesheet.get_image(0, 400, 200, 60)]
        '''
        #self.image = random.choice(images)
        #self.image.set_colorkey(BLACK)
        self.image = pg.Surface((200, 50))
        self.image.fill(GREEN)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        # Randomly generate a boost with a newly spawned platform:
        if random.randrange(100) < POWER_SPAWN:
            Power(self.game, self)

class Floor(pg.sprite.Sprite):
    def __init__(self, game):
        self._layer = PLATFORM_LAYER
        self.groups = game.all_sprites, game.platforms
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        # Use when sprites are available
        '''
        images = [self.game.spritesheet.get_image(400, 200, 200, 60),
                  self.game.spritesheet.get_image(600, 200, 200, 90),
                  self.game.spritesheet.get_image(0, 400, 200, 60)]
        '''
        #self.image = random.choice(images)
        #self.image.set_colorkey(BLACK)
        self.image = pg.Surface((WIDTH + 300, 50))
        self.image.fill(GREEN)
        self.rect = self.image.get_rect()
        self.rect.x = -150
        self.rect.y = HEIGHT - 50


class Wall(pg.sprite.Sprite):
    def __init__(self, game, x):
        self._layer = PLATFORM_LAYER
        self.groups = game.all_sprites, game.walls
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        # Use when sprites are available
        '''
        images = [self.game.spritesheet.get_image(400, 200, 200, 60),
                  self.game.spritesheet.get_image(600, 200, 200, 90),
                  self.game.spritesheet.get_image(0, 400, 200, 60)]
        '''
        #self.image = random.choice(images)
        #self.image.set_colorkey(BLACK)
        self.image = pg.Surface((150, 2 * HEIGHT))
        self.image.fill(BLACK)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.bottom = HEIGHT - 50


class Power(pg.sprite.Sprite):
    # Not sure if we want to add a power feature, like a boost?
    def __init__(self, game, plat):
        self._layer = POWER_LAYER
        self.groups = game.all_sprites, game.powerups
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        # Powerups are spawned with an associated platform:
        self.plat = plat
        # May want more than one powerup type?
        self.type = random.choice(['boost'])
        self.current_frame = 0
        self.last_update = 0
        # When and if sprite is made for boost:
        '''
        self.image_choice = random.randrange(1, 3)
        if self.image_choice == 1:
            self.images = [self.game.spritesheet.get_image(600, 0, 200, 190),
                           self.game.spritesheet.get_image(600, 600, 200, 190)]
        else:
            self.images = [self.game.spritesheet.get_image(0, 600, 200, 200),
                           self.game.spritesheet.get_image(200, 600, 200, 200)]

        for frame in self.images:
            frame.set_colorkey(BLACK)
        # self.image = random.choice(self.images)
        self.image = self.images[self.current_frame]
        '''
        self.image = pg.Surface((10, 10))
        self.image.fill(SKY)
        self.rect = self.image.get_rect()
        self.rect.centerx = self.plat.rect.centerx
        self.rect.bottom = self.plat.rect.top - 80

    def update(self):
        now = pg.time.get_ticks()
        # Set power object with respect to platform
        self.rect.bottom = self.plat.rect.top - 80

        #if now - self.last_update > 200:
        #    self.last_update = now
        #    self.current_frame = (self.current_frame + 1) % len(self.images)
        #self.image = self.images[self.current_frame]

        # Remove sprite when platform is killed off screen
        if not self.game.platforms.has(self.plat):
            self.kill()


class Enemy(pg.sprite.Sprite):
    # Remade for our black smoke, maybe more depending on level:
    def __init__(self, game):
        self._layer = ENEMY_LAYER
        self.groups = game.all_sprites, game.mobs
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.current_frame = 0
        self.last_update = 0

        # Use when spritesheet ready:
        '''
        self.images = [self.game.spritesheet.get_image(200, 400, 200, 200),
                       self.game.spritesheet.get_image(400, 400, 200, 200),
                       self.game.spritesheet.get_image(600, 400, 200, 200)]
        for frame in self.images:
            frame.set_colorkey(BLACK)
        self.image = self.images[self.current_frame]
        '''
        self.image = pg.Surface((200, HEIGHT))
        self.image.fill(BLACK)

        self.rect = self.image.get_rect()
        self.rect.centerx = -500
        #self.rect.centerx = random.choice([-100, WIDTH + 100])
        #self.vx = random.randrange(1, 4)
        #if self.rect.centerx > WIDTH:
        #    self.vx *= -1
        # Setting velocity in x-dir
        self.vx = 12
        self.rect.y = 0
        # Can make it speed up in future:
        self.vy = 0
        self.dy = 0

    def update(self):
        now = pg.time.get_ticks()
        self.rect.x += self.vx
        self.vy += self.dy
        center = self.rect.center
        '''
        if now - self.last_update > 200:
            self.last_update = now
            self.current_frame = (self.current_frame + 1) % len(self.images)
        self.image = self.images[self.current_frame]
        '''
        self.rect = self.image.get_rect()
        # Advanced collision mask, if we want a very specific darkness and player hitbox:
        self.mask = pg.mask.from_surface(self.image)
        self.rect.center = center
        self.rect.y += self.vy
        #if self.rect.left > WIDTH + 100:
        #    self.kill()


class Collide_Objects(pg.sprite.Sprite):
    def __init__(self, game):
        self._layer = PLATFORM_LAYER
        self.groups = game.all_sprites, game.mobs
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.current_frame = 0
        self.last_update = 0

        # Use when spritesheet ready:
        '''
        self.images = [self.game.spritesheet.get_image(200, 400, 200, 200),
                       self.game.spritesheet.get_image(400, 400, 200, 200),
                       self.game.spritesheet.get_image(600, 400, 200, 200)]
        for frame in self.images:
            frame.set_colorkey(BLACK)
        self.image = self.images[self.current_frame]
        '''
        self.image = pg.Surface((random.randrange(100, 150), (random.randrange(75, 100))))
        self.image.fill(RED)
        self.rect = self.image.get_rect()
        self.rect.centerx = random.randrange(WIDTH + 100, WIDTH + 250)
        self.rect.centery = random.randrange(0, HEIGHT - 100)
        # Can make objects that fall, chase, etc, with the following parameters, just modify Collide_Object __init__:
        #self.vx = random.randrange(1, 4)
        #if self.rect.centerx > WIDTH:
        #    self.vx *= -1
        self.vx = 0
        self.vy = 0
        self.dy = 0

    def update(self):
        now = pg.time.get_ticks()
        self.rect.x += self.vx
        self.vy += self.dy
        center = self.rect.center
        '''
        if now - self.last_update > 200:
            self.last_update = now
            self.current_frame = (self.current_frame + 1) % len(self.images)
        self.image = self.images[self.current_frame]
        self.rect = self.image.get_rect()
        '''
        # Advanced collision mask, if we want a specific object (wheel chairs, patient beds, saw?) and player hitbox:
        self.mask = pg.mask.from_surface(self.image)
        self.rect.center = center
        self.rect.y += self.vy
        # For objects that fall or rise, need them to be destroyed:
        if self.rect.top > HEIGHT or self.rect.bottom < -50:
            self.kill()
        if self.rect.right < 0:
            self.kill()


class Door(pg.sprite.Sprite):
    def __init__(self, game, x, y, number, key):
        self._layer = DOOR_LAYER
        self.locked = not key
        self.number = number
        self.groups = game.all_sprites, game.doors
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.current_frame = 0
        self.last_update = 0

        # Use when spritesheet ready:
        '''
        self.images = [self.game.spritesheet.get_image(200, 400, 200, 200),
                       self.game.spritesheet.get_image(400, 400, 200, 200),
                       self.game.spritesheet.get_image(600, 400, 200, 200)]
        for frame in self.images:
            frame.set_colorkey(BLACK)
        self.image = self.images[self.current_frame]
        '''
        self.image = pg.Surface((100, 220))
        self.image.fill(BROWN)
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.bottom = y
        self.vx = 0
        self.vy = 0
        self.dy = 0

    def update(self):
            now = pg.time.get_ticks()
            center = self.rect.center
            self.rect.center = center
            self.rect.y += self.vy


class Key(pg.sprite.Sprite):
    # Not sure if we want to add a power feature, like a boost?
    def __init__(self, game, x, y):
        self._layer = POWER_LAYER
        self.groups = game.all_sprites, game.powerups
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        # Key animation?
        self.current_frame = 0
        self.last_update = 0
        # When and if sprite is made for key:
        '''
        self.image_choice = random.randrange(1, 3)
        if self.image_choice == 1:
            self.images = [self.game.spritesheet.get_image(600, 0, 200, 190),
                           self.game.spritesheet.get_image(600, 600, 200, 190)]
        else:
            self.images = [self.game.spritesheet.get_image(0, 600, 200, 200),
                           self.game.spritesheet.get_image(200, 600, 200, 200)]

        for frame in self.images:
            frame.set_colorkey(BLACK)
        # self.image = random.choice(self.images)
        self.image = self.images[self.current_frame]
        '''
        self.image = pg.Surface((15, 30))
        self.image.fill(YELLOW)
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.bottom = y

    def update(self):
        now = pg.time.get_ticks()
        #if now - self.last_update > 200:
        #    self.last_update = now
        #    self.current_frame = (self.current_frame + 1) % len(self.images)
        #self.image = self.images[self.current_frame]


class Game:
    def __init__(self):
        # Initialize Game Window
        # Create Starting Window:
        pg.init()
        pg.mixer.init()
        self.screen = pg.display.set_mode((WIDTH, HEIGHT))
        pg.display.set_caption(TITLE)
        self.clock = pg.time.Clock()
        self.running = True
        self.font_name = pg.font.match_font(FONT_NAME)
        self.interacting = False
        self.entering = False
        self.door1_key = False
        self.door2_key = False
        self.door3_key = False
        self.door1_fact = True
        self.door2_fact = True
        self.door3_fact = True
        self.load_data()
        self.last_update = 0

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
        self.background_images = []
        '''
        for i in range(1, 4):
            self.background_images.append(pg.image.load(path.join(img_dir, 'XXXX.png'.format(i))).convert())
        # Loading Image
        self.spritesheet = Spritesheet(path.join(img_dir, SPRITE_FILE))
        '''

# --NEW-- AFTER ENTERING A ROOM NEW IS CALLED -> RUN -> EVENTS & UPDATE & DRAW
    def new(self):
        # Restart Game and Start Everything anew after entering a door
        self.score = 0
        self.all_sprites = pg.sprite.LayeredUpdates()
        self.platforms = pg.sprite.Group()
        self.powerups = pg.sprite.Group()
        self.mobs = pg.sprite.Group()
        self.background = pg.sprite.Group()
        self.player = Player(self)

        # Initial Screen Platforms (Make this the area as soon as player enters door, before randomly generating level:
        for plat in PLATFORM_LIST:
            Platform(self, *plat)
        Enemy(self)
        Floor(self)
        # Mob timer will be needed to spawn objects needing jumped/slid over/under:
        self.mob_timer = 0
        self.run()

    def run(self):
        # Game Loop
        self.playing = True

        while self.playing:
            self.clock.tick(FPS)
            self.events()
            self.update()
            self.draw()

    def update(self):
        # Game loop update
        # Update all content to be displayed to gamer
        self.all_sprites.update()
        now = pg.time.get_ticks()

        # If we want to spawn additional objects to harm player:
        if now - self.mob_timer > ENEMY_FREQ + random.choice([-1000, -500, 0, 500, 1000]):
            self.mob_timer = now
            Collide_Objects(self)

        # Check for platform collisions while falling
        if self.player.vel.y > 0:
            hits = pg.sprite.spritecollide(self.player, self.platforms, False)
            if hits:
                lower_platform = hits[0]
                for hit in hits:
                    if hit.rect.bottom > lower_platform.rect.bottom:
                        lower_platform = hit
                if self.player.pos.x < lower_platform.rect.right + 10 and self.player.pos.x > lower_platform.rect.left - 10:
                    # Only move to platform top if feet higher than platform top
                    if self.player.pos.y < lower_platform.rect.bottom:
                        self.player.pos.y = lower_platform.rect.top + 1
                        self.player.vel.y = 0
                        self.player.jumping = False

        # If player reaches rightmost 1/2 of screen
        if self.player.rect.centerx >= WIDTH / 2:
            self.player.pos.x -= max(abs(self.player.vel.x), 2)
            for bck_obj in self.background:
                bck_obj.rect.x -= max(abs(self.player.vel.x) / 2, 2)
            for mob in self.mobs:
                mob.rect.x -= max(abs(self.player.vel.x), 2)
            for power in self.powerups:
                power.rect.x -= max(abs(self.player.vel.x), 2)
            for plat in self.platforms:
                plat.rect.x -= max(abs(self.player.vel.x), 2)
                if plat.rect.right < 0:
                    plat.kill()
                    self.score += 10

        # Enemy Collision
        mob_hits = pg.sprite.spritecollide(self.player, self.mobs, False)
        if mob_hits:
            self.playing = False

        # Boost Collision
        pow_hits = pg.sprite.spritecollide(self.player, self.powerups, True)
        for pow in pow_hits:
            if pow.type == "boost":
                self.player.vel.x = BOOST_POWER
                # Jumping through platforms when boosted will not snap to platform:
                self.player.jumping = False

        # Need new platforms
        while len(self.platforms) < 8:
            width = random.randrange(50, 800)
            # More platformer like:
            Platform(self, random.randrange(WIDTH, WIDTH + width), random.randrange(200, HEIGHT - 100))
            # More runner like:
            #Platform(self, WIDTH + 50, HEIGHT - 50)

        # Player Falls off Screen
        if self.player.rect.bottom > HEIGHT:
            for sprite in self.all_sprites:
                sprite.rect.y -= max(self.player.vel.y, 10)
                if sprite.rect.bottom > 0:
                    sprite.kill()
        if len(self.platforms) == 0:
            self.playing = False

# --LEVEL SELECT-- ROOM WITH 3 DOORS TO CHOOSE. LEVEL_SELECT IS CALLED ->
    # LVL_SELECT_RUN -> EVENTS & LVL_SELECT_UPDATE & LVL_SELECT_DRAW
    def level_select(self):
        self.all_sprites = pg.sprite.LayeredUpdates()
        self.platforms = pg.sprite.Group()
        self.background = pg.sprite.Group()
        # Powerups includes key, can be changed in future:
        self.powerups = pg.sprite.Group()
        self.walls = pg.sprite.Group()
        self.doors = pg.sprite.Group()
        self.player = Player(self)

        # Draw central room with three doors to choose from:
        # Choosing doors in an inefficient way:
        if not self.door1_key:
            # If key 1 not picked up, draw it in central room:
            Key(self, WIDTH / 2, HEIGHT / 8)

        Door(self, WIDTH / 8, HEIGHT - 50, 1, self.door1_key)
        Door(self, WIDTH / 2, HEIGHT - 50, 2, self.door2_key)
        Door(self, WIDTH - 100, HEIGHT - 50, 3, self.door3_key)
        Wall(self, -325)
        Wall(self, WIDTH)
        Floor(self)
        self.lvl_select_run()

    def lvl_select_run(self):
        # Game Loop
        self.playing = True

        while self.playing:
            self.clock.tick(FPS)
            self.events()
            self.lvl_select_update()
            self.lvl_select_draw()

    def lvl_select_update(self):
        # Game loop update
        # Update all content to be displayed to gamer
        self.all_sprites.update()

        # Key Collision
        key_hits = pg.sprite.spritecollide(self.player, self.powerups, True)
        if key_hits:
            self.door1_key = True

        # With key player enters door, if correct key permits:
        door_hits = pg.sprite.spritecollide(self.player, self.doors, False)
        if door_hits and self.interacting:
            for door in door_hits:
                if door.number == 1 and self.door1_key:
                    door.locked = False
                elif door.number == 2 and self.door2_key:
                    door.locked = False
                elif door.number == 3 and self.door3_key:
                    door.locked = False

        if door_hits and self.entering:
            for door in door_hits:
                if not door.locked:
                    if door.number == 1 and self.door1_fact:
                        self.load_door1()
                        self.door1_fact = False
                        self.entering = False
                    elif door.number == 2 and self.door2_fact:
                        self.load_door2()
                        self.door2_fact = False
                        self.entering = False
                    elif door.number == 3 and self.door3_fact:
                        self.load_door3()
                        self.door3_fact = False
                        self.entering = False
                    self.playing = False

        # Check for wall interaction:
        wall_hits = pg.sprite.spritecollide(self.player, self.walls, False)
        if wall_hits:
            if self.player.vel.x < 0:
                self.player.acc.x = 0
                self.player.vel.x = 0
                self.player.pos.x = self.player.rect.right
            else:
                self.player.acc.x = 0
                self.player.vel.x = 0
                self.player.pos.x = self.player.rect.left

        # Check for platform collisions while falling
        # May want platforms in main area?
        if self.player.vel.y > 0:
            hits = pg.sprite.spritecollide(self.player, self.platforms, False)
            if hits:
                lower_platform = hits[0]
                for hit in hits:
                    if hit.rect.bottom > lower_platform.rect.bottom:
                        lower_platform = hit
                if self.player.pos.x < lower_platform.rect.right + 10 and self.player.pos.x > lower_platform.rect.left - 10:
                    # Only move to platform top if feet higher than platform top
                    if self.player.pos.y < lower_platform.rect.bottom:
                        self.player.pos.y = lower_platform.rect.top + 1
                        self.player.vel.y = 0
                        self.player.jumping = False

        # The following results in some weird effects with the walls and floor moving incorrectly, something to look into later:
        # If player reaches rightmost 1/3 of screen
        if self.player.rect.centerx >= WIDTH * 3/4:
            self.player.pos.x -= max(abs(self.player.vel.x), 2)
            for bck_obj in self.background:
                bck_obj.rect.x -= max(abs(self.player.vel.x) / 2, 2)
            for plat in self.platforms:
                plat.rect.x -= max(abs(self.player.vel.x), 2)
            for door in self.doors:
                door.rect.x -= max(abs(self.player.vel.x), 2)
            for power in self.powerups:
                power.rect.x -= max(abs(self.player.vel.x), 2)
            for wall in self.walls:
                wall.rect.x -= max(abs(self.player.vel.x), 2)

        # If player reaches leftmost 1/4 of screen
        if self.player.rect.centerx <= WIDTH / 4:
            self.player.pos.x += max(abs(self.player.vel.x), 2)
            for bck_obj in self.background:
                bck_obj.rect.x += max(abs(self.player.vel.x) / 2, 2)
            for plat in self.platforms:
                plat.rect.x += max(abs(self.player.vel.x), 2)
            for door in self.doors:
                door.rect.x += max(abs(self.player.vel.x), 2)
            for power in self.powerups:
                power.rect.x += max(abs(self.player.vel.x), 2)
            for wall in self.walls:
                wall.rect.x += max(abs(self.player.vel.x), 2)

        # Player Falls off Screen
        if self.player.rect.bottom > HEIGHT:
            for sprite in self.all_sprites:
                sprite.rect.y -= max(self.player.vel.y, 10)
                if sprite.rect.bottom > 0:
                    sprite.kill()
        if len(self.platforms) == 0:
            self.playing = False

# --EVENTS-- SHARED BY BOTH LEVEL SELECTION & NEW GAME
    def events(self):
        # Game loop events
        for event in pg.event.get():
            # Jumping ability Check
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_UP:
                    self.player.jump()
            # Jump can be controlled, little to big jump
            if event.type == pg.KEYUP:
                if event.key == pg.K_UP:
                    self.player.jump_stop()

            # Slide Check
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_DOWN:
                    self.player.slide()

            if event.type == pg.KEYUP:
                if event.key == pg.K_DOWN:
                    self.player.slide_stop()

            # Check for quitting game event:
            if event.type == pg.QUIT:
                self.playing = False
                self.running = False

            # Check for interacting:
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_i:
                    self.interacting = True

            if event.type == pg.KEYUP:
                if event.key == pg.K_i:
                    self.interacting = False

            # Check for entering:
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_e:
                    self.entering = True

            if event.type == pg.KEYUP:
                if event.key == pg.K_e:
                    self.entering = False

    def draw(self):
        # Draw loop elements after updating
        # Draw background and sprites:
        self.screen.fill(BGCOLOR)
        self.all_sprites.draw(self.screen)
        self.draw_text(str(self.score), 22, WHITE, WIDTH / 2, 15)
        # Flip display after drawing:
        pg.display.flip()

    def lvl_select_draw(self):
        self.screen.fill(BGCOLOR)
        self.all_sprites.draw(self.screen)
        door_hits = pg.sprite.spritecollide(self.player, self.doors, False)
        if door_hits and self.interacting:
            for door in door_hits:
                if door.locked:
                    self.draw_text("Locked.", 22, WHITE, door.rect.centerx, door.rect.bottom - 150)
                else:
                    self.draw_text("Unlocked. E to Enter", 22, WHITE, door.rect.centerx, door.rect.bottom - 150)
        pg.display.flip()

    def show_start_screen(self):
        # Start up screen
        self.screen.fill(BGCOLOR)
        self.draw_text("Trans-Allegheny Lunatic Asylum Escape", 48, WHITE, WIDTH / 2, HEIGHT / 4)
        self.draw_text("Left & Right Arrow Keys to Move & Up Arrow Key to Jump", 22, WHITE, WIDTH / 2, HEIGHT / 2)
        self.draw_text("Down Arrow Key to Slide & i to Interact", 22, WHITE, WIDTH / 2, HEIGHT / 2 + 50)
        self.draw_text("Press Any Key to Begin!", 22, WHITE, WIDTH / 2, HEIGHT * 3 / 4)
        self.draw_text("High Score: " + str(self.highscore), 22, WHITE, WIDTH / 2, 15)
        pg.display.flip()
        self.wait_for_key()

    def load_intro(self):
        # After start screen introduction.
        self.screen.fill(BGCOLOR)
        self.draw_text("You took the dare to explore the building knowing it is off limits.", 22, WHITE, WIDTH / 2, HEIGHT / 2 - 25)
        self.draw_text("Upon entering, the floor gave and you fell into a room of three doors.", 22, WHITE, WIDTH / 2, HEIGHT / 2)
        self.draw_text(" You think it best to look for a way out... you hear something lurking in the distance.", 22, WHITE, WIDTH / 2, HEIGHT / 2 + 25)
        self.draw_text("Press Any Key to Continue!", 16, WHITE, WIDTH / 2, HEIGHT * 3 / 4)
        pg.display.flip()
        self.wait_for_key()

    def load_door1(self):
        # After start screen introduction.
        self.screen.fill(BGCOLOR)
        self.draw_text("Door 1 Random Facts and History.", 22, WHITE, WIDTH / 2, HEIGHT / 2 - 25)
        self.draw_text("Press Any Key to Continue!", 16, WHITE, WIDTH / 2, HEIGHT * 3 / 4)
        pg.display.flip()
        self.wait_for_key()

    def load_door2(self):
        # After start screen introduction.
        self.screen.fill(BGCOLOR)
        self.draw_text("Door 2 Random Facts and History.", 22, WHITE, WIDTH / 2, HEIGHT / 2 - 25)
        self.draw_text("Press Any Key to Continue!", 16, WHITE, WIDTH / 2, HEIGHT * 3 / 4)
        pg.display.flip()
        self.wait_for_key()

    def load_door3(self):
        # After start screen introduction.
        self.screen.fill(BGCOLOR)
        self.draw_text("Door 3 Random Facts and History.", 22, WHITE, WIDTH / 2, HEIGHT / 2 - 25)
        self.draw_text("Press Any Key to Continue!", 16, WHITE, WIDTH / 2, HEIGHT * 3 / 4)
        pg.display.flip()
        self.wait_for_key()

    def wait_for_key(self):
        pg.event.wait()
        waiting = True
        while waiting:
            self.clock.tick(FPS)
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    waiting = False
                    self.running = False
                if event.type == pg.KEYUP:
                    waiting = False

    def show_go_screen(self):
        # Game over screen only if you lose, not if you close program
        if not self.running:
            # Player Closed Application, so skip the Game Over screen
            return
        self.screen.fill(BGCOLOR)
        self.draw_text("You Did Not Escape", 48, WHITE, WIDTH / 2, HEIGHT / 4)
        self.draw_text("SCORE: " + str(self.score), 22, WHITE, WIDTH / 2, HEIGHT / 2)
        self.draw_text("Want to Run Again? Press Any Key to Play Again", 22, WHITE, WIDTH / 2, HEIGHT * 3 / 4)
        if self.score > self.highscore:
            self.highscore = self.score
            self.draw_text("You Have Never Survived Longer!", 35, WHITE, WIDTH / 2, HEIGHT / 2 + 50)
            with open(path.join(self.dir, HS_FILE), 'r+') as file:
                file.write(str(self.score))
        else:
            self.draw_text("High Score: " + str(self.highscore), 22, WHITE, WIDTH / 2, HEIGHT / 2 + 50)

        pg.display.flip()
        self.wait_for_key()

    def draw_text(self, text, size, color, xpos, ypos):
        font = pg.font.Font(self.font_name, size)
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect()
        text_rect.midtop = (xpos, ypos)
        self.screen.blit(text_surface, text_rect)

# --CREATE GAME AND GO THROUGH EVENTS--
g = Game()
g.show_start_screen()
g.load_intro()
while g.running:
    g.level_select()
    g.new()
    g.show_go_screen()

pg.quit()
