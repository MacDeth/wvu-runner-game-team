import pygame as pg
import random
from constants import *
import controller

# Vector for player movement
vec = pg.math.Vector2

class Spritesheet(pg.sprite.Sprite):
    # Load the sprite sheet PNG
    def __init__(self, filename):
        self.spritesheet = pg.image.load(filename).convert_alpha()

    def get_image(self, x, y, width, height):
        # Grab PNG images:
        image = self.spritesheet.subsurface(pg.Rect((x, y), (width, height)))
        # Can scale sprites to get a certain aspect ratio:
        image = pg.transform.scale(image, (width // 2, height // 2))
        return image

    def get_raw_image(self, x, y, width, height):
        # Grab PNG images without scaling:
        image = pg.Surface((width, height))
        image.blit(self.spritesheet, (0, 0), (x, y, width, height))
        return image

"""Player class"""
class Player(pg.sprite.Sprite):
    def __init__(self, game):
        # Set Player Sprite Layer
        self._layer = PLAYER_LAYER
        pg.sprite.Sprite.__init__(self)
        game.all_sprites.add(self, layer = PLAYER_LAYER)
        self.game = game

        # Boolean States Used for Determining Animation States
        self.walking = False
        self.jumping = False
        self.sliding = False
        self.current_frame = 0
        self.last_update = 0

        # Use Load Image when Spritesheet is Done
        self.load_images()
        self.image = self.standing_frames[0]
        self.rect = self.image.get_rect()

        # Position, Velocity, and Acceleration Vectors for Movement
        self.pos = vec(WIDTH / 2, HEIGHT / 2)
        self.vel = vec(0, 0)
        self.acc = vec(0, 0)
        
    def load_images(self):
        # Load Image Sheets and then Pass Them to "get_image" for specific frame extraction
        # Standing Animation
        self.standing_frames = [self.game.spritesheet.get_image(0, 1024, 512, 512),
                                self.game.spritesheet.get_image(512, 1024, 512, 512)]
       
        # Walking Animation
        self.walking_frames_r = [self.game.spritesheet.get_image(0, 0, 512, 512),
                                 self.game.spritesheet.get_image(512, 0, 512, 512),
                                 self.game.spritesheet.get_image(1024, 0, 512, 512),
                                 self.game.spritesheet.get_image(1536, 0, 512, 512),
                                 self.game.spritesheet.get_image(0, 512, 512, 512),
                                 self.game.spritesheet.get_image(512, 512, 512, 512),
                                 self.game.spritesheet.get_image(1024, 512, 512, 512),
                                 self.game.spritesheet.get_image(1536, 512, 512, 512)]
        self.walking_frames_l = []
        for frame in self.walking_frames_r:
            # Only draw one half of walking right animation and then flip it for left animation:
            self.walking_frames_l.append(pg.transform.flip(frame, True, False))

        # Jumping Animation
        self.jump_frames_r = self.game.spritesheet.get_image(0, 0, 512, 512)
        self.jump_frames_l = pg.transform.flip(self.jump_frames_r, True, False)
        
        # Sliding Animation
        self.sliding_frames_r = self.game.spritesheet.get_image(1024, 1280, 512, 256)
        self.sliding_frames_l = pg.transform.flip(self.sliding_frames_r, True, False)

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
        self.sliding = True

    def slide_stop(self):
        self.sliding = False

    def update(self):
        self.animate()
        self.acc = vec(0, PLAYER_GRAVITY)
        
        # Controller
        if self.game.controller is not None:
            dpad = self.game.controller.get_axis(controller.HORIZ_AXIS)
            if dpad < 0:
                self.acc.x = -PLAYER_ACC
            if dpad > 0:
                self.acc.x = PLAYER_ACC
            
        # Keyboard
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
        now = pg.time.get_ticks()
        if self.vel.x >= 4 or self.vel.x <= -4:
            self.walking = True
        else:
            self.walking = False

        # Walking Time
        if self.walking:
            # 200 is arbitrarily chosen, depending on #frames in spritesheet
            if now - self.last_update > 70:
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
            if now - self.last_update > 50:
                self.last_update = now
                # self.current_frame = (self.current_frame + 1) % len(self.walking_frames_l)
                bottom = self.rect.bottom
                if self.vel.x > 0 and self.vel.y < 0:
                    self.image = self.jump_frames_r
                elif self.vel.x < 0 and self.vel.y < 0:
                    self.image = self.jump_frames_l
                else:
                    #self.image = self.walking_frames_r[0]
                    pass
                self.rect = self.image.get_rect()
                self.rect.bottom = bottom

        if not self.jumping and not self.walking:
            if now - self.last_update > 250:
                self.last_update = now
                self.current_frame = (self.current_frame + 1) % len(self.standing_frames)
                bottom = self.rect.bottom
                self.image = self.standing_frames[self.current_frame]
                self.rect = self.image.get_rect()
                self.rect.bottom = bottom

        if self.sliding:
            if now - self.last_update > 50:
                self.last_update = now
                # self.current_frame = (self.current_frame + 1) % len(self.walking_frames_l)
                bottom = self.rect.bottom
                if self.vel.x > 0 or self.vel.y < 0:
                    self.image = self.sliding_frames_r
                elif self.vel.x < 0 or self.vel.y < 0:
                    self.image = self.sliding_frames_l
                else:
                    #self.image = self.walking_frames_r[0]
                    pass
                self.rect = self.image.get_rect()
                self.rect.bottom = bottom
                
        # More accurate collision mask for player
        self.mask = pg.mask.from_surface(self.image)

"""Background Image Objects that you want to move through background"""
class Background(pg.sprite.Sprite):
    def __init__(self, game):
        self._layer = BACK_ART_LAYER
        pg.sprite.Sprite.__init__(self, game.all_sprites, game.background)
        self.game = game
        # Choose a random background object to display, use when sprites are done
        #self.image = random.choice(self.game.web_images)
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        # My background images were 800 x 800 and I wanted them aligned to the square game field:
        self.rect.x = 0
        self.rect.y = -800

        # Float representation of position
        self.pos = vec(self.rect.x, self.rect.y)

    def update(self):
        # If the top of background objects go off the screen, remove them.
        if self.rect.right < 0:
            self.kill()

    def move(self, amt):
        self.pos += amt
        self.rect.x = self.pos.x
        self.rect.y = self.pos.y

class Platform(pg.sprite.Sprite):
    def __init__(self, game, x, y):
        self._layer = PLATFORM_LAYER
        pg.sprite.Sprite.__init__(self, game.all_sprites, game.platforms)
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
        self.image.fill(GRAY)

        # Set up rect
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

        # Float representation of position
        self.pos = vec(x, y)

        # Randomly generate a boost with a newly spawned platform:
        if random.randrange(100) < POWER_SPAWN:
            Power(self.game, self)

    def move(self, amt):
        self.pos += amt
        self.rect.x = self.pos.x
        self.rect.y = self.pos.y

class Floor(pg.sprite.Sprite):
    def __init__(self, game):
        self._layer = PLATFORM_LAYER
        pg.sprite.Sprite.__init__(self, game.all_sprites, game.platforms)
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
        self.image.fill(GRAY)
        self.rect = self.image.get_rect()
        self.rect.x = -150
        self.rect.y = HEIGHT - 50

        # Float representation of position
        self.pos = vec(self.rect.x, self.rect.y)

    def move(self, amt):
        self.pos += amt
        self.rect.x = self.pos.x
        self.rect.y = self.pos.y

class Wall(pg.sprite.Sprite):
    def __init__(self, game, x):
        self._layer = PLATFORM_LAYER
        pg.sprite.Sprite.__init__(self, game.all_sprites, game.walls)
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
        self.image.fill(GRAY)
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.centery = HEIGHT - 50

        # Float representation of position
        self.pos = vec(x, self.rect.centery)

    def move(self, amt):
        self.pos += amt
        self.rect.centerx = self.pos.x
        self.rect.centery = self.pos.y

class Power(pg.sprite.Sprite):
    # Not sure if we want to add a power feature, like a boost?
    def __init__(self, game, plat):
        self._layer = POWER_LAYER
        pg.sprite.Sprite.__init__(self, game.all_sprites, game.powerups)
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
        
        # Internal position
        self.pos = vec(self.rect.centerx, self.rect.bottom);

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
            
    def move(self, amt):
        self.pos += amt
        self.rect.centerx = self.pos.x
        self.rect.bottom = self.pos.y

class Darkness(pg.sprite.Sprite):
    # Remade for our black smoke, maybe more depending on level:
    def __init__(self, game):
        self._layer = DARKNESS_LAYER
        pg.sprite.Sprite.__init__(self, game.all_sprites, game.mobs)
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
        
        # Internal position
        self.pos = vec(self.rect.centerx, self.rect.y)

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
        self.pos = vec(self.rect.centerx, self.rect.y)
        
    def move(self, amt):
        self.pos += amt
        self.rect.centerx = self.pos.x
        self.rect.y = self.pos.y

class Obstacles(pg.sprite.Sprite):
    def __init__(self, game):
        self._layer = OBSTACLE_LAYER
        pg.sprite.Sprite.__init__(self, game.all_sprites, game.mobs)
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
        
        # Internal position
        self.pos = vec(self.rect.centerx, self.rect.centery)

        self.used = False
        self._used_indicator = False

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

        if self.used and not self._used_indicator: # only complete this fill once
            self.image.fill(DARK_RED)
            self._used_indicator = True
            
    def move(self, amt):
        self.pos += amt
        self.rect.centerx = self.pos.x
        self.rect.centery = self.pos.y


class Door(pg.sprite.Sprite):
    def __init__(self, game, x, y, number, key):
        self._layer = DOOR_LAYER
        self.locked = not key
        self.number = number
        pg.sprite.Sprite.__init__(self, game.all_sprites, game.doors)
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
        self.image = pg.Surface((150, 300))
        self.image.fill(BROWN)
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.bottom = y
        self.vx = 0
        self.vy = 0
        self.dy = 0
        
        # Internal position
        self.pos = vec(x, y)

    def update(self):
            now = pg.time.get_ticks()
            center = self.rect.center
            self.rect.center = center
            self.rect.y += self.vy

    def move(self, amt):
        self.pos += amt
        self.rect.centerx = self.pos.x
        self.rect.bottom = self.pos.y


class Key(pg.sprite.Sprite):
    # Not sure if we want to add a power feature, like a boost?
    def __init__(self, game, x, y):
        self._layer = POWER_LAYER
        pg.sprite.Sprite.__init__(self, game.all_sprites, game.powerups)
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

        # Set up rect
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.bottom = y

        # Float representation of position
        self.pos = vec(x, y)

    def update(self):
        now = pg.time.get_ticks()
        #if now - self.last_update > 200:
        #    self.last_update = now
        #    self.current_frame = (self.current_frame + 1) % len(self.images)
        #self.image = self.images[self.current_frame]

    def move(self, amt):
        self.pos += amt
        self.rect.centerx = self.pos.x
        self.rect.bottom = self.pos.y
