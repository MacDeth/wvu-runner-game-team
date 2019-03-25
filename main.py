# Trans-Allegheny Lunatic Asylum Semester Project
# CS 475
# First Pass: Skyler Roth
# Basic Side-Scrolling and 3 Level Selection

# Made in Python 3.6
import pygame as pg
import random
from os import path
from entities import *
from constants import *

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
        self.platform_collision()

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
        for e in mob_hits:
            # The only mobs that are on the platform layer are obstacles
            if e._layer == PLATFORM_LAYER:
                # TODO: Change this maybe? It can really launch the player
                self.player.vel.x -= BOOST_POWER / 2
            else: # it's an enemy mob
                self.playing = False
                break

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
        Wall(self, -225)
        Wall(self, WIDTH + 225)
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
        # May want platforms in main area?
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
                file.write(str(self.score) + '\n')
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

    def platform_collision(self):
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
    g.show_start_screen()
    g.load_intro()
    while g.running:
        g.level_select()
        g.new()
        g.show_go_screen()

    pg.quit()

if __name__ == "__main__":
    main()
