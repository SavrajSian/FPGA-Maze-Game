from asyncio import format_helpers
import pygame, pygame.gfxdraw
import math, time, random
import numpy as np
import socket

pygame.init()

screen = pygame.display.set_mode((1280, 720))
pygame.display.set_caption(" ")  #################

vignette = pygame.image.load("assets/vignette.png")
hole_image = pygame.image.load("assets/hole.png")
goal_glow_image = pygame.image.load("assets/goal_glow.png").convert_alpha()
goal_white_image = pygame.image.load("assets/goal_white.png").convert_alpha()
ball_images = [pygame.image.load("assets/ball.png").convert_alpha(),
               pygame.image.load("assets/ball_y.png").convert_alpha(),
               pygame.image.load("assets/ball_g.png").convert_alpha(),
               pygame.image.load("assets/ball_b.png").convert_alpha()]
speedup_image = pygame.image.load("assets/speedup.png")
invert_image = pygame.image.load("assets/invert.png")
freeze_image = pygame.image.load("assets/freeze.png")
transparent = pygame.image.load(("assets/transparent.png"))
ball_colours = [(230, 230, 230), (255, 255, 170), (170, 255, 170), (170, 220, 255)]

ball_initial_pos = [[150, 100], [110, 140], [190, 140], [150, 180]]  # [X, Y]
dodgeball_initial_pos = [[100, 100], [1130, 100], [100, 570], [1130, 570]]

balls = [None, None, None, None]

class Ball:
    friction = 0.95  # gradual slowing
    restitution = 0.6  # bounce
    scores = [0, 0, 0, 0]
    won = []  # list to determine how many balls have won, and when to change level

    def __init__(self, ID):
        self.ID = ID
        self.acc = [0, 0]
        self.vel = [0, 0]
        if Level.active_level == dodgeball:
            self.pos = dodgeball_initial_pos[ID].copy()
        else:
            self.pos = ball_initial_pos[ID].copy()
        self.damping = 1000
        self.colour = ball_colours[ID]
        self.image = ball_images[ID].copy()
        self.rect = self.image.get_rect()
        self.size = 45
        self.halfsize = 20
        self.scaler = 1.0
        self.brightness = 255
        self.respawn_timer = 20  # ms
        self.kills = 0
        self.deaths = 0
        self.lives = 20
        self.speedup = 'False'
        self.invert = 'False'
        self.freeze = 'False'
        self.poweruptimer = 1000


    def respawn_animation(self):
        if self.respawn_timer == 20:
            self.pos[0] -= 10  # fixes ball drawn from top left
            self.pos[1] -= 10
            self.scaler = 1.9
        elif self.respawn_timer > 10:
            self.pos[0] += 2
            self.pos[1] += 2
            self.scaler -= 0.1
        elif self.respawn_timer > 5:
            if self.respawn_timer == 10:
                ParticleSystem.active_systems.append(
                    ParticleSystem(particle_no=20, colour=self.colour, lifetime=0.5, distance=200, size=3,
                                   coords=[self.pos[0] + self.rect.center[0], self.pos[1] + self.rect.center[1]]))
            self.pos[0] -= 1
            self.pos[1] -= 1
            self.scaler += 0.1
        else:
            self.pos[0] += 1
            self.pos[1] += 1
            self.scaler -= 0.1
            if self.respawn_timer == 1:
                ParticleSystem.active_systems.append(
                    ParticleSystem(particle_no=10, colour=self.colour, lifetime=0.5, distance=100, size=3,
                                   coords=[self.pos[0] + self.rect.center[0], self.pos[1] + self.rect.center[1]]))
        self.scaler = round(self.scaler, 2)
        self.respawn_timer = max(0, self.respawn_timer - 1)
        self.image = pygame.transform.smoothscale(ball_images[self.ID].copy(),
                                                  (self.size * self.scaler, self.size * self.scaler))

    def get_centre(self):
        return [self.pos[0] + self.rect.center[0], self.pos[1] + self.rect.center[1]]  # centre on global coords

    def motion_calc(self, dt):
        if self.speedup == self.ID:
            self.vel[0] += 3 * self.acc[0] * dt / self.damping  # v = u + at
            self.vel[1] += 3 * self.acc[1] * dt / self.damping

        elif self.freeze != 'False' and self.ID == self.freeze:
            self.vel[0] = 0
            self.vel[1] = 0

        else:
            self.vel[0] += self.acc[0] * dt / self.damping  # v = u + at
            self.vel[1] += self.acc[1] * dt / self.damping

        self.vel[0] = self.vel[0] * Ball.friction
        self.vel[1] = self.vel[1] * Ball.friction

        if self.invert == self.ID:
            self.pos[0] -= self.vel[0] * dt
            self.pos[1] -= self.vel[1] * dt
        else:
            self.pos[0] += self.vel[0] * dt
            self.pos[1] += self.vel[1] * dt

    def frame_collision(self):
        if self.get_centre()[0] - self.rect.center[0] < 82:  # left hitbox
            self.pos[0] = 82
            self.vel[0] = -self.vel[0] * Ball.restitution
            if abs(self.vel[0]) > 1000:
                ParticleSystem.active_systems.append(
                    ParticleSystem(particle_no=random.randint(1, 3), colour=self.colour, lifetime=0.5, distance=10,
                                   size=3, coords=[self.pos[0], self.pos[1] + self.rect.center[1]]))
        if self.get_centre()[0] + self.rect.center[0] > 1200:  # right hitbox
            self.pos[0] = 1156
            self.vel[0] = -self.vel[0] * Ball.restitution
            if abs(self.vel[0]) > 1000:
                ParticleSystem.active_systems.append(
                    ParticleSystem(particle_no=random.randint(1, 3), colour=self.colour, lifetime=0.5, distance=10,
                                   size=3, coords=[self.pos[0] + self.rect.right, self.pos[1] + self.rect.center[1]]))
        if self.get_centre()[1] - self.rect.center[1] < 72:  # up hitbox
            self.pos[1] = 72
            self.vel[1] = -self.vel[1] * Ball.restitution
            if abs(self.vel[1]) > 1000:
                ParticleSystem.active_systems.append(
                    ParticleSystem(particle_no=random.randint(1, 3), colour=self.colour, lifetime=0.5, distance=10,
                                   size=3, coords=[self.pos[0] + self.rect.center[0], self.pos[1]]))
        if self.get_centre()[1] + self.rect.center[1] > 645:  # down hitbox
            self.pos[1] = 601
            self.vel[1] = -self.vel[1] * Ball.restitution
            if abs(self.vel[1]) > 1000:
                ParticleSystem.active_systems.append(
                    ParticleSystem(particle_no=random.randint(1, 3), colour=self.colour, lifetime=0.5, distance=10,
                                   size=3, coords=[self.pos[0] + self.rect.center[0], self.pos[1] + self.rect.bottom]))

    def block_collision(self):
        for block in Level.active_level.blocks:
            # left hitbox
            if (self.get_centre()[0] + self.halfsize > block.rect.left - 1) and \
                    (self.get_centre()[0] - self.halfsize < block.rect.left + 20) and \
                    (self.get_centre()[1] + self.halfsize > block.rect.top + 15) and \
                    (self.get_centre()[1] - self.halfsize < block.rect.bottom - 15):
                self.pos[0] = block.rect.left - self.size + 2
                self.vel[0] = -self.vel[0] * Ball.restitution
                if abs(self.vel[0]) > 1000:
                    ParticleSystem.active_systems.append(
                        ParticleSystem(particle_no=random.randint(1, 3), colour=self.colour, lifetime=0.5, distance=10,
                                       size=3,
                                       coords=[self.pos[0] + self.rect.right, self.pos[1] + self.rect.center[1]]))
            # right hitbox
            if (self.get_centre()[0] + self.halfsize > block.rect.right - 20) and \
                    (self.get_centre()[0] - self.halfsize < block.rect.right) and \
                    (self.get_centre()[1] + self.halfsize > block.rect.top + 15) and \
                    (self.get_centre()[1] - self.halfsize < block.rect.bottom - 20):
                self.pos[0] = block.rect.right - 2
                self.vel[0] = -self.vel[0] * Ball.restitution
                if abs(self.vel[0]) > 1000:
                    ParticleSystem.active_systems.append(
                        ParticleSystem(particle_no=random.randint(1, 3), colour=self.colour, lifetime=0.5, distance=10,
                                       size=3, coords=[self.pos[0], self.pos[1] + self.rect.center[1]]))
            # up hitbox
            if (self.get_centre()[0] + self.halfsize > block.rect.left + 10) and \
                    (self.get_centre()[0] - self.halfsize < block.rect.right - 5) and \
                    (self.get_centre()[1] + self.halfsize > block.rect.top) and \
                    (self.get_centre()[1] - self.halfsize < block.rect.top + 20):
                self.pos[1] = block.rect.top - self.size + 2
                self.vel[1] = -self.vel[1] * Ball.restitution
                if abs(self.vel[1]) > 1000:
                    ParticleSystem.active_systems.append(
                        ParticleSystem(particle_no=random.randint(1, 3), colour=self.colour, lifetime=0.5, distance=10,
                                       size=3,
                                       coords=[self.pos[0] + self.rect.center[0], self.pos[1] + self.rect.bottom]))
            # down hitbox
            if (self.get_centre()[0] + self.halfsize > block.rect.left + 10) and \
                    (self.get_centre()[0] - self.halfsize < block.rect.right - 5) and \
                    (self.get_centre()[1] + self.halfsize > block.rect.bottom - 20) and \
                    (self.get_centre()[1] - self.halfsize < block.rect.bottom):
                self.pos[1] = block.rect.bottom - 2
                self.vel[1] = -self.vel[1] * Ball.restitution
                if abs(self.vel[1]) > 1000:
                    ParticleSystem.active_systems.append(
                        ParticleSystem(particle_no=random.randint(1, 3), colour=self.colour, lifetime=0.5, distance=10,
                                       size=3, coords=[self.pos[0] + self.rect.center[0], self.pos[1]]))

    def hole_collision(self):
        for hole in Level.active_level.holes:
            np_self = np.asarray(self.get_centre())
            np_hole = np.asarray([hole.pos[0] + hole.rect.center[0], hole.pos[1] + hole.rect.center[1]])
            line = np_self - np_hole
            distance = np.linalg.norm(line)
            if distance < 30:  # ball centre goes into hole
                direction = [np_hole[0] - np_self[0], np_hole[1] - np_self[1]]
                if self.invert == self.ID:
                    self.vel = [-direction[0] * 200, -direction[1] * 200]
                else:
                    self.vel = [direction[0] * 200, direction[1] * 200]
                self.scaler -= 0.01
                self.scaler = round(self.scaler, 2)
                self.image = pygame.transform.smoothscale(ball_images[self.ID].copy(), (
                self.size * self.scaler, self.size * self.scaler))  # makes ball smaller slowly
                if self.scaler > 0.9:
                    self.brightness = max(0, self.brightness - 15)
                    if type(hole) == Goal:
                        self.image.fill((255, 255, 255, self.brightness), None, pygame.BLEND_RGBA_MULT)
                        self.image.fill((255 - self.brightness, 255 - self.brightness, 255 - self.brightness, 255),
                                        None, pygame.BLEND_RGB_ADD)
                    else:
                        self.image.fill((self.brightness, self.brightness, self.brightness, 255), None,
                                        pygame.BLEND_RGBA_MULT)
                else:
                    self.image.fill((255, 255, 255, 0), None, pygame.BLEND_RGBA_MULT)  # hide ball during timeout
                if self.scaler < 0.8:
                    if type(hole) == Goal:
                        ParticleSystem.active_systems.append(
                            ParticleSystem(particle_no=50, colour=self.colour, lifetime=2, distance=400,
                                           coords=[hole.pos[0] + hole.rect.center[0],
                                                   hole.pos[1] + hole.rect.center[1]]))
                if self.scaler < 0.7:
                    if type(hole) == Goal:
                        Ball.scores[self.ID] += 40 - (len(Ball.won) * 10)  # scores are 40, 30, 20, 10 in that order
                        Ball.won.append(self.ID)  # New ball has won
                        balls[self.ID] = None  # No other way in python to delete an instance
                        if len(Ball.won) == 4:
                            update_level()
                    else:
                        Ball.scores[self.ID] = max(0, Ball.scores[self.ID] - 5)  # prevents negative scores
                        self.__init__(self.ID)  # respawn ball if fallen into the other holes.

    def powerup_collision(self):

        for powerup in active_powerups.powerup:
            np_selfpow = np.asarray(self.get_centre())
            np_pow = np.asarray(
                [powerup.pos[0] + powerup.rect.center[0], powerup.pos[1] + powerup.rect.center[1]])
            powline = np_selfpow - np_pow
            distance = np.linalg.norm(powline)
            if distance < 30:  # ball close to powerup
                if powerup.type == 'speedup':
                    self.speedup = self.ID
                elif powerup.type == 'freeze':
                    savefrID = self.ID
                    for ball in balls:
                        if ball != None:
                            if savefrID != ball.ID:
                                ball.freeze = ball.ID
                elif powerup.type == 'invert':
                    saveinvID = self.ID
                    for ball in balls:
                        if ball!= None:
                            if saveinvID != ball.ID:
                                ball.invert = ball.ID
                powerup.dead = 1
                return str(powerup.type)
            else:
                return 'NO'


    def poweruptimeout(self):
        for ball in balls:
            if ball != None:

                if self.poweruptimer == 0:
                    self.speedup = 'False'
                    self.freeze = 'False'
                    self.invert = 'False'
                elif self.poweruptimer >= 0:
                    self.poweruptimer = max(0, self.poweruptimer - 1)

    def ball_kill(self):
        for ball in balls:
            if ball != None:
                if ball.ID != self.ID:
                    np_self = np.asarray(self.get_centre())
                    np_ball = np.asarray(ball.get_centre())
                    line_of_impact = np_self - np_ball
                    distance = np.linalg.norm(line_of_impact)
                    if distance < 50:
                        if np.linalg.norm(ball.vel) > np.linalg.norm(self.vel):
                            self.pos = [random.randint(
                                100, 1150), random.randint(100, 570)]
                            self.vel = [0, 0]
                            self.acc = [0, 0]
                            ball.kills += 1
                            self.deaths += 1
                            if self.lives > 0:
                                self.lives -= 1

                        elif np.linalg.norm(self.vel) > np.linalg.norm(ball.vel):
                            ball.pos = [random.randint(
                                100, 1150), random.randint(100, 570)]
                            ball.vel = [0, 0]
                            ball.acc = [0, 0]
                            self.kills += 1
                            ball.deaths += 1
                            if ball.lives > 0:
                                ball.lives -= 1

def hex_to_dec(hex):
    d = int(hex, 16)
    if d < 2147483648:  # h80000000
        return d
    else:
        return d - 4294967296  # hFFFFFFFF+1


def update_level(choice=None):  # Done once to determine that level is changing and to which level
    global t, new_level, new_powerupplacements
    if choice == None:
        if Level.active_level == level1:
            new_level = level2
            new_powerupplacements = level2_powerup
        elif Level.active_level == level2:
            new_level = level3
            new_powerupplacements = level3_powerup
        elif Level.active_level == level3:
            new_level = level4
            new_powerupplacements = level4_powerup
        elif Level.active_level == level4:
            new_level = level5
            new_powerupplacements = level5_powerup
        elif Level.active_level == level5:
            pass  ######################
    else:
        new_level = choice
    t = 0
    Level.changing = True

def level_change():  # Keeps happening until it sets the variable to false
    global new_level, new_powerupplacements
    if t < 0.5:
        pass
    elif t < 1:
        ParticleSystem.active_systems.append(
            ParticleSystem(particle_no=500, colour="transition", lifetime=1, distance=8000, coords=[-200, 360],
                           type="stream", distr="unif", angle=0, width=500, size=30))
    elif t < 2:
        Level.active_level = new_level
        Powerup.active_powerups = new_powerupplacements
        for powerup in active_powerups.powerup:
            powerup.__init__(random.choice(Powerup.active_powerups), random.choice(powerupchoices))

        Ball.won = []
    elif t < 2.2:
        if balls[0] == None: balls[0] = Ball(0)  # gradually creates new balls again
    elif t < 2.4:
        if balls[1] == None: balls[1] = Ball(1)
    elif t < 2.6:
        if balls[2] == None: balls[2] = Ball(2)
    elif t < 2.8:
        if balls[3] == None: balls[3] = Ball(3)
    else:
        Level.changing = False


def which_level(level_in):  # turns level name into number
    if (level_in == level1):
        return 1
    elif level_in == level2:
        return 2
    elif level_in == level3:
        return 3
    elif level_in == level4:
        return 4
    elif level_in == level5:
        return 5


class Level:
    changing = False
    active_level = None

    def __init__(self, block_coords, hole_coords, colour, bg_colour, edge_colour, goal_colour):
        self.colour = colour
        self.bg_colour = bg_colour
        self.edge_colour = edge_colour
        self.blocks = []
        for i in range(len(block_coords)):
            self.blocks.append(Block(block_coords[i]))
        self.holes = []
        self.holes.append(Goal(hole_coords[0], goal_colour))
        for i in range(1, len(hole_coords)):
            self.holes.append(Hole(hole_coords[i], goal_colour))

    def draw_frame(self):
        # parallax
        pygame.draw.rect(screen, Level.active_level.edge_colour, pygame.Rect(10, 0, 83, 720))
        pygame.draw.rect(screen, Level.active_level.edge_colour, pygame.Rect(1190, 0, 80, 720))
        pygame.draw.rect(screen, Level.active_level.edge_colour, pygame.Rect(0, 10, 1280, 74))
        pygame.draw.rect(screen, Level.active_level.edge_colour, pygame.Rect(0, 635, 1280, 80))
        # frame
        pygame.draw.rect(screen, Level.active_level.colour, pygame.Rect(0, 0, 83, 720))
        pygame.draw.rect(screen, Level.active_level.colour, pygame.Rect(1200, 0, 80, 720))
        pygame.draw.rect(screen, Level.active_level.colour, pygame.Rect(0, 0, 1280, 74))
        pygame.draw.rect(screen, Level.active_level.colour, pygame.Rect(0, 644, 1280, 80))

class Dodgeball:
    def __init__(self, block_coords, colour, bg_colour, edge_colour):
        self.colour = colour
        self.bg_colour = bg_colour
        self.edge_colour = edge_colour
        self.blocks = []
        for i in range(len(block_coords)):
            self.blocks.append(Block(block_coords[i]))

    def draw_frame(self):
        # parallax
        pygame.draw.rect(screen, Level.active_level.edge_colour,
                         pygame.Rect(10, 0, 83, 720))
        pygame.draw.rect(screen, Level.active_level.edge_colour,
                         pygame.Rect(1190, 0, 80, 720))
        pygame.draw.rect(screen, Level.active_level.edge_colour,
                         pygame.Rect(0, 10, 1280, 74))
        pygame.draw.rect(screen, Level.active_level.edge_colour,
                         pygame.Rect(0, 635, 1280, 80))
        # frame
        pygame.draw.rect(screen, Level.active_level.colour,
                         pygame.Rect(0, 0, 83, 720))
        pygame.draw.rect(screen, Level.active_level.colour,
                         pygame.Rect(1200, 0, 80, 720))
        pygame.draw.rect(screen, Level.active_level.colour,
                         pygame.Rect(0, 0, 1280, 74))
        pygame.draw.rect(screen, Level.active_level.colour,
                         pygame.Rect(0, 644, 1280, 80))


class Block:
    def __init__(self, coords):
        self.rect = pygame.Rect(coords[0], coords[1], coords[2], coords[3])
        self.pos = [coords[0], coords[1]]


class Hole:
    def __init__(self, coords, colour):
        self.image = hole_image
        self.rect = self.image.get_rect()
        self.pos = [coords[0], coords[1]]


class Goal(Hole):
    def __init__(self, coords, colour):
        self.white = goal_white_image
        self.image = goal_glow_image.copy()
        self.image.fill(colour, None, pygame.BLEND_RGBA_MULT)
        self.rect = self.image.get_rect()
        self.pos = [coords[0], coords[1]]


class ParticleSystem():
    active_systems = []

    def __init__(self, particle_no, colour, lifetime, distance, coords, type="burst", distr="gauss", angle=None, size=5,
                 width=60):
        self.particles = []
        for i in range(particle_no):
            self.particles.append(Particle(colour, lifetime, distance, coords, type, distr, angle, size, width))


class Particle():
    def __init__(self, colour, lifetime, distance, coords, type, distr, angle, size, width):
        self.randomlifetime = random.uniform(lifetime * 0.8, lifetime * 1.2)
        self.size = size
        self.magnitude = random.randint(25, 100) * distance
        self.angle = random.uniform(0,
                                    2 * math.pi) if angle == None else angle  # differentiate between burst and stream
        if type == "stream":
            if distr == "gauss":
                self.pos = [coords[0], random.gauss(coords[1], width)]
            elif distr == "unif":
                self.pos = [coords[0], random.uniform(coords[1] - width, coords[1] + width)]
        else:
            self.pos = [coords[0], coords[1]]
        if colour == "title":
            self.colour = (255, max(0, 245 - abs(360 - self.pos[1]) * 0.8),
                           max(0, 190 - abs(360 - self.pos[1]) * 1.7))  # title gradient
        elif colour == "transition":
            random_grey = random.randint(200, 255)
            self.colour = (random_grey, random_grey, random_grey)
        else:
            self.colour = colour
        self.vel = [self.magnitude * np.cos(self.angle), self.magnitude * np.sin(self.angle)]
        self.veer = [random.randint(-500, 500), random.randint(-500, 500)]  # random turn

    def motion(self, dt):
        self.veer = [self.veer[0] * 0.93, self.veer[1] * 0.93]  # attenuate veer
        self.vel = [self.vel[0] - self.veer[0], self.vel[1] - self.veer[1]]  # apply veer
        self.vel = [self.vel[0] * 0.9, self.vel[1] * 0.9]  # attenuate speed
        self.pos[0] += self.vel[0] * dt
        self.pos[1] += self.vel[1] * dt

    def lifetime(self, particles):
        self.randomlifetime -= 0.05
        if self.randomlifetime < 0:
            particles.remove(self)  # dead


def draw_parallax(object):
    scale_factorX = (640 - object.rect.center[0]) / 100
    scale_factorY = (360 - object.rect.center[1]) / 100
    scaled = [object.pos[0] + scale_factorX,
              object.pos[1] + scale_factorY,
              object.rect.right - object.pos[0] + scale_factorX,
              object.rect.bottom - object.pos[1] + scale_factorY]
    pygame.draw.rect(screen, Level.active_level.edge_colour, pygame.Rect(scaled[0], scaled[1], scaled[2], scaled[3]))

class Powerup:
    active_powerups = None

    def __init__(self, coords, name):
        if name == 'freeze':
            self.image = freeze_image
        elif name == 'speedup':
            self.image = speedup_image
        elif name == 'invert':
            self.image = invert_image

        self.rect = self.image.get_rect()
        self.pos = [coords[0], coords[1]]
        self.brightness = 200
        self.type = name
        self.dead = 0
        self.respawntime = 500

    def respawn(self):
        randomrespawntime = random.randint(500, 5000)
        if self.respawntime == 0 and self.dead == 1:
            self.respawntime = randomrespawntime
            self.__init__(random.choice(Powerup.active_powerups), random.choice(powerupchoices))
        elif self.respawntime >= 0 and self.dead == 1:
            self.respawntime = max(0, self.respawntime - 1)



class SpawnPowerup:
    def __init__(self, coords, type):

        self.powerup = []
        self.powerup.append(Powerup(coords, type))


powerupchoices = ['speedup', 'freeze', 'invert']
level1_blocks = [(300, 50, 60, 320),
                 (750, 300, 60, 380)]
level1_holes = [(1020, 450),  # first hole is always the goal
                (500, 100),
                (600, 500),
                (1000, 200)]
level1_powerup = [(630, 300), (1080, 250), (350, 550)]
level1_colour = (190, 25, 90)  # Magenta
level1_bg_colour = (120, 15, 70)
level1_edge_colour = (100, 10, 60)
level1_goal_colour = (255, 110, 160, 255)  # RGBA
level1 = Level(level1_blocks, level1_holes, level1_colour, level1_bg_colour,
               level1_edge_colour, level1_goal_colour)
level1powerups = [level1_powerup, random.choice(powerupchoices)]

level2_blocks = [(400, 50, 60, 300),
                 (600, 300, 60, 380),
                 (1100, 200, 300, 60)]
level2_holes = [(1020, 450),  # first hole is always the goal
                (100, 250),
                (200, 500),
                (800, 300),
                (1000, 400),
                (1100, 350)]
level2_powerup = [(100, 500), (1000, 700)]
level2_colour = (129, 77, 189)  # Light Purple
level2_bg_colour = (81, 8, 163)  # Dark purple
level2_edge_colour = (60, 2, 127)
level2_goal_colour = (250, 200, 255, 255)  # RGBA
level2 = Level(level2_blocks, level2_holes, level2_colour, level2_bg_colour,
               level2_edge_colour, level2_goal_colour)
level2powerups = [random.choice(level2_powerup), random.choice(powerupchoices)]

level3_blocks = [(300, 50, 60, 420),
                 (600, 300, 60, 380),
                 (800, 50, 60, 320)]
level3_holes = [(1020, 100),  # first hole is always the goal
                (120, 550),
                (450, 450),
                (650, 200),
                (900, 100),
                (1100, 450),
                (450, 250)]
level3_powerup = [(660, 550), (1050, 520), (390, 110)]
level3_colour = (41, 204, 73)  # Light green
level3_bg_colour = (44, 153, 66)  # Dark green
level3_edge_colour = (27, 112, 44)
level3_goal_colour = (200, 255, 200, 255)  # RGBA
level3 = Level(level3_blocks, level3_holes, level3_colour, level3_bg_colour,
               level3_edge_colour, level3_goal_colour)
level3powerups = [level3_powerup, random.choice(powerupchoices)]

level4_blocks = [(80, 580, 350, 80),
                 (300, 50, 60, 350),
                 (600, 220, 60, 480)]
level4_holes = [(1020, 450),  # first hole is always the goal
                (250, 475),
                (475, 500),
                (700, 200),
                (975, 200),
                (1075, 200),
                (1100, 400),
                (950, 550)]
level4_powerup = [(800, 120), (1080, 300), (400, 500)]
level4_colour = (222, 139, 91)  # Light orange
level4_bg_colour = (191, 87, 27)  # Dark orange
level4_edge_colour = (172, 75, 19)
level4_goal_colour = (255, 230, 200, 255)  # RGBA
level4 = Level(level4_blocks, level4_holes, level4_colour, level4_bg_colour,
               level4_edge_colour, level4_goal_colour)
level4powerups = [level4_powerup, random.choice(powerupchoices)]

level5_blocks = [(300, 50, 60, 120),
                 (200, 300, 60, 400),
                 (500, 50, 60, 320),
                 (500, 550, 60, 100),
                 (800, 550, 60, 100),
                 (900, 300, 340, 60)]
level5_holes = [(1020, 450),  # first hole is always the goal
                (400, 200),
                (350, 350),
                (450, 400),
                (350, 550),
                (650, 550),
                (675, 150),
                (975, 150),
                (730, 440)]
level5_powerup = [(560, 270), (900, 190), (110, 380)]
level5_colour = (89, 164, 222)  # Light blue
level5_bg_colour = (13, 110, 184)  # Dark blue
level5_edge_colour = (13, 77, 181)
level5_goal_colour = (200, 230, 255, 255)  # RGBA
level5 = Level(level5_blocks, level5_holes, level5_colour, level5_bg_colour,
               level5_edge_colour, level5_goal_colour)
level5powerups = [level5_powerup, random.choice(powerupchoices)]

dodgeball_blocks = [(250, 550, 40, 40), (1050, 400, 30, 30),
                    (725, 130, 35, 35), (650, 450, 27, 27), (400, 260, 30, 30)]

dodgeball_colour = (100, 150, 200)
dodgeball_bg_colour = (83, 91, 131)
dodgeball_edge_colour = (13, 77, 181)
dodgeball = Dodgeball(dodgeball_blocks, dodgeball_colour,
                      dodgeball_bg_colour, dodgeball_edge_colour)

Level.active_level = level1
Powerup.active_powerups = level1_powerup
active_powerups = SpawnPowerup(random.choice(Powerup.active_powerups), random.choice(powerupchoices))


def manual_movement(ball_ID, key1, key2, key3, key4):
    keys = pygame.key.get_pressed()
    if keys[key1]:
        if balls[ball_ID] == None and ball_ID not in Ball.won: balls[ball_ID] = Ball(
            ball_ID)  # Spawn ball if doesn't exist
        if balls[ball_ID] != None: balls[ball_ID].acc[1] = hex_to_dec(
            "CCCCCCCC")  # Fake HEX movement of ball (if exists) for manual override
    if keys[key2]:
        if balls[ball_ID] == None and ball_ID not in Ball.won: balls[ball_ID] = Ball(ball_ID)
        if balls[ball_ID] != None: balls[ball_ID].acc[1] = hex_to_dec("33333333")
    if keys[key3]:
        if balls[ball_ID] == None and ball_ID not in Ball.won: balls[ball_ID] = Ball(ball_ID)
        if balls[ball_ID] != None: balls[ball_ID].acc[0] = hex_to_dec("33333333")
    if keys[key4]:
        if balls[ball_ID] == None and ball_ID not in Ball.won: balls[ball_ID] = Ball(ball_ID)
        if balls[ball_ID] != None: balls[ball_ID].acc[0] = hex_to_dec("CCCCCCCC")


titlefont = pygame.font.SysFont('interextrabeta', 200)
title = titlefont.render("Title", True, (255, 255, 255))
title_rect = title.get_rect()
title_rect.center = (640, 360)
levelfont = pygame.font.SysFont('interextrabeta', 50)
score_font = pygame.font.SysFont('interextrabeta', 50)

t = 0
dt = 0.001
clock = pygame.time.Clock()
t0 = time.time()
running = True


def GUI_loop():
    global running, t, t0
    clock.tick(60)  # keeps framerate at 60fps at most
    t += time.time() - t0  # keeps track of seconds elapsed since level start
    t0 = time.time()

    screen.fill(Level.active_level.bg_colour)

    for i, block in enumerate(Level.active_level.blocks):  # draws parallax
        draw_parallax(block)

    Level.active_level.draw_frame()

    for block in Level.active_level.blocks:  # draws blocks
        pygame.draw.rect(screen, Level.active_level.colour, block.rect)

    screen.blit(vignette, (0, 0))

    if Level.active_level != dodgeball:
        for hole in Level.active_level.holes:
            screen.blit(hole.image, (hole.pos[0], hole.pos[1]))
        goal_centre = [Level.active_level.holes[0].pos[0] +
                       60, Level.active_level.holes[0].pos[1] + 60]
        screen.blit(Level.active_level.holes[0].white,
                    (goal_centre[0], goal_centre[1]))

        for powerup in active_powerups.powerup:
            if powerup.dead == 1:
                powerup.respawn()
            screen.blit(powerup.image, (powerup.pos[0], powerup.pos[1]))

    keys = pygame.key.get_pressed()
    manual_movement(0, pygame.K_w, pygame.K_s, pygame.K_d, pygame.K_a)
    manual_movement(1, pygame.K_UP, pygame.K_DOWN, pygame.K_RIGHT, pygame.K_LEFT)
    manual_movement(2, pygame.K_i, pygame.K_k, pygame.K_l, pygame.K_j)
    manual_movement(3, pygame.K_g, pygame.K_b, pygame.K_n, pygame.K_v)



    for ball in balls:
        if ball != None and Level.active_level != dodgeball:
            ball.frame_collision()
            ball.block_collision()
            ball.hole_collision()

            if ball.powerup_collision() != 'NO':
                if ball.powerup_collision() == 'speedup':
                    powerup.pos = [0, 0]
                    powerup.image = transparent

                if ball.powerup_collision() == 'invert':
                    powerup.pos = [0, 0]
                    powerup.image = transparent

                if ball.powerup_collision() == 'freeze':
                    powerup.pos = [0, 0]
                    powerup.image = transparent

            if ball.freeze != 'False' or ball.speedup != 'False' or ball.invert != 'False':
                ball.poweruptimeout()

            screen.blit(ball.image, (ball.pos[0], ball.pos[1]))
            if ball.respawn_timer == 0:
                if t > 2:  # Determines when to give players control
                    ball.motion_calc(dt)
            else:
                ball.respawn_animation()

        elif ball != None and Level.active_level == dodgeball:
            ball.motion_calc(dt)
            ball.frame_collision()
            ball.block_collision()
            ball.ball_kill()
            if ball.lives > 0:
                screen.blit(ball.image, (ball.pos[0], ball.pos[1]))

    for ball in balls:
        if ball != None:
            ball.acc = [0, 0]  # set acceleration to 0 if no key pressed. After FPGA and manual override

    if Level.active_level == level1 and not Level.changing:
        if t > 0.5 and t < 2.5:  # Title stream
            y = random.randint(340, 380) + np.sin(15 * t) * 40
            ParticleSystem.active_systems.append(
                ParticleSystem(particle_no=200, colour="title", lifetime=1, distance=8000, coords=[-200, y],
                               type="stream", distr="gauss", angle=0, size=20))

    for system in ParticleSystem.active_systems:  # Draws all particle systems
        for particle in system.particles:
            particle.motion(dt)
            particle.lifetime(system.particles)
            if len(system.particles) == 0:
                ParticleSystem.active_systems.remove(system)  # delete system if empty
            pygame.draw.rect(screen, particle.colour,
                             (particle.pos[0], particle.pos[1], particle.size, particle.size))  # draw any particles

    if Level.active_level == level1 and not Level.changing:
        if t > 0.5 and t < 2.5:  # Title
            screen.blit(title, title_rect)

    if t > 2.5:
        what_level = which_level(Level.active_level)  # Displays "Level X"
        level_num = levelfont.render(f"Level {what_level}", True, (255, 255, 255))
        screen.blit(level_num, (560, 10))
        ball0_text = score_font.render(str(Ball.scores[0]), True, (230, 230, 230))
        screen.blit(ball0_text, (320, 650))
        ball1_text = score_font.render(str(Ball.scores[1]), True, (240, 240, 90))
        screen.blit(ball1_text, (520, 650))
        ball2_text = score_font.render(str(Ball.scores[2]), True, (120, 240, 120))
        screen.blit(ball2_text, (720, 650))
        ball3_text = score_font.render(str(Ball.scores[3]), True, (120, 120, 240))
        screen.blit(ball3_text, (920, 650))

    if Level.changing:
        level_change()  # keeps doing this until it sets the variable to false

    pygame.display.update()

    for event in pygame.event.get():  # close button
        if event.type == pygame.QUIT:
            running = False


server_name = '3.85.233.169'
server_port = 12000
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.settimeout(0.01)  # 10ms timeout for receives, after which silent error is thrown
connection = False
send_msg = "0,33333333:33333333,"
send_msg_prev = "0,33333333:33333333,"


def network():
    global recv_msg, send_msg, send_msg_prev, connection
    if connection == False:
        try:
            try:
                server_socket.connect((server_name, server_port))
            except Exception as e:
                print(e)
                pass
            server_socket.send("I'm the game".encode())  # Identifies which client is game
            print("Connected")
            connection = True
        except:
            pass
    else:  # connected
        received = False
        try:
            recv_msg = server_socket.recv(1024).decode()
            print(f"received {send_msg}")
            received = True
        except:
            pass
        if received:
            sender = recv_msg.split(',')[0]
            if sender == "s":
                pass  # server messages
            else:  # FPGA messages
                try:
                    acc0 = recv_msg.split(',')[1].split(":")[0]
                    balls[int(sender)].acc[0] = hex_to_dec(acc0)
                    acc1 = recv_msg.split(',')[1].split(":")[1]
                    balls[int(sender)].acc[1] = hex_to_dec(acc1)
                    print(balls[int(sender)].acc)
                except:
                    pass

        if send_msg != send_msg_prev:  # Check whether to send
            try:
                server_socket.send(send_msg.encode())
                print(f"sent {send_msg}")
            except:
                pass
        send_msg_prev = send_msg


if __name__ == "__main__":
    i = 0
    while running:  # switches between game and networking
        if i % 5 == 0:  # Make networking infrequent to reduce lag
            network()
        i += 1
        GUI_loop()
