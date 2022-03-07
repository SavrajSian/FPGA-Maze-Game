import pygame
import pygame.gfxdraw
import math
import time
import random
import numpy as np
from random import choice


pygame.init()

screen = pygame.display.set_mode((1280, 720))
pygame.display.set_caption(" ")

vignette = pygame.image.load("assets/vignette.png")
hole_image = pygame.image.load("assets/hole.png")
goal_glow_image = pygame.image.load("assets/goal_glow.png").convert_alpha()
goal_white_image = pygame.image.load("assets/goal_white.png").convert_alpha()
ball_images = [pygame.image.load("assets/ball.png").convert_alpha(), pygame.image.load("assets/ball_y.png").convert_alpha(),
               pygame.image.load("assets/ball_g.png").convert_alpha(), pygame.image.load("assets/ball_b.png").convert_alpha()]
speedup_image = pygame.image.load("assets/speedup.png")
invert_image = pygame.image.load("assets/invert.png")
freeze_image = pygame.image.load("assets/freeze.png")

ball_colours = [(230, 230, 230), (255, 255, 170),
                (170, 255, 170), (170, 220, 255)]

ball_initial_pos = [[150, 100], [110, 140], [190, 140], [150, 180]]  # [X, Y]
dodgeball_initial_pos = [[100, 100], [1130, 100], [100, 570], [1130, 570]]
balls = [None, None, None, None]

friction = 0.95
restitution = 0.6
dt = 0.001
clock = pygame.time.Clock()
gofast = 'NO'
invertcontrol = 'NO'
freezeball = 'NO'
starttimesp = 0
starttimeinv = 0
starttimefr = 0


class Ball:
    def __init__(self, ID):
        self.ID = ID
        self.acc = [0, 0]
        self.vel = [0, 0]
        if active_level == dodgeball:
            self.pos = dodgeball_initial_pos[ID].copy()
        else:
            self.pos = ball_initial_pos[ID].copy()
        self.damping = 1000
        self.colour = ball_colours[ID]
        self.image = ball_images[ID].copy()
        self.rect = self.image.get_rect()
        self.size = 40
        self.halfsize = 20
        self.scaler = 1
        self.brightness = 255
        self.kills = 0
        self.deaths = 0

    def get_centre(self):
        # centre on global coords
        return [self.pos[0] + self.rect.center[0], self.pos[1] + self.rect.center[1]]

    def motion_calc(self, dt):
        if gofast != 'NO' and self.ID == gofast:
            ball.vel[0] += 3*self.acc[0]*dt/self.damping  # v = u + at
            ball.vel[1] += 3*self.acc[1]*dt/self.damping

        elif freezeball != 'NO' and self.ID != freezeball:
            ball.vel[0] = 0
            ball.vel[1] = 0

        else:
            ball.vel[0] += self.acc[0]*dt/self.damping  # v = u + at
            ball.vel[1] += self.acc[1]*dt/self.damping

        ball.vel[0] = self.vel[0]*friction
        ball.vel[1] = self.vel[1]*friction

        if invertcontrol != 'NO' and self.ID != invertcontrol:
            ball.pos[0] -= self.vel[0]*dt
            ball.pos[1] -= self.vel[1]*dt
        else:
            ball.pos[0] += self.vel[0]*dt
            ball.pos[1] += self.vel[1]*dt

    def frame_collision(self):
        if self.get_centre()[0] - self.rect.center[0] < 82:  # left hitbox
            self.pos[0] = 82
            self.vel[0] = -self.vel[0]*restitution
            if abs(self.vel[0]) > 1000:
                active_particle_systems.append(ParticleSystem(particle_no=random.randint(
                    1, 3), colour=self.colour, lifetime=0.5, radius=10, size=3, coords=[self.pos[0], self.pos[1] + self.rect.center[1]]))
        if self.get_centre()[0] + self.rect.center[0] > 1200:  # right hitbox
            self.pos[0] = 1156
            self.vel[0] = -self.vel[0]*restitution
            if abs(self.vel[0]) > 1000:
                active_particle_systems.append(ParticleSystem(particle_no=random.randint(
                    1, 3), colour=self.colour, lifetime=0.5, radius=10, size=3, coords=[self.pos[0] + self.rect.right, self.pos[1] + self.rect.center[1]]))
        if self.get_centre()[1] - self.rect.center[1] < 72:  # up hitbox
            self.pos[1] = 72
            self.vel[1] = -self.vel[1]*restitution
            if abs(self.vel[1]) > 1000:
                active_particle_systems.append(ParticleSystem(particle_no=random.randint(
                    1, 3), colour=self.colour, lifetime=0.5, radius=10, size=3, coords=[self.pos[0] + self.rect.center[0], self.pos[1]]))
        if self.get_centre()[1] + self.rect.center[1] > 645:  # down hitbox
            self.pos[1] = 601
            self.vel[1] = -self.vel[1]*restitution
            if abs(self.vel[1]) > 1000:
                active_particle_systems.append(ParticleSystem(particle_no=random.randint(1, 3), colour=self.colour, lifetime=0.5, radius=10, size=3, coords=[
                                               self.pos[0] + self.rect.center[0], self.pos[1] + self.rect.bottom]))

    def block_collision(self):
        for block in active_level.blocks:
            # left hitbox
            if (self.get_centre()[0] + self.halfsize > block.rect.left - 1) and\
               (self.get_centre()[0] - self.halfsize < block.rect.left + 20) and\
               (self.get_centre()[1] + self.halfsize > block.rect.top + 15) and\
               (self.get_centre()[1] - self.halfsize < block.rect.bottom - 15):
                self.pos[0] = block.rect.left - self.size - 3
                self.vel[0] = -self.vel[0]*restitution
                if abs(self.vel[0]) > 1000:
                    active_particle_systems.append(ParticleSystem(particle_no=random.randint(
                        1, 3), colour=self.colour, lifetime=0.5, radius=10, size=3, coords=[self.pos[0] + self.rect.right, self.pos[1] + self.rect.center[1]]))
            # right hitbox
            if (self.get_centre()[0] + self.halfsize > block.rect.right - 20) and\
               (self.get_centre()[0] - self.halfsize < block.rect.right) and\
               (self.get_centre()[1] + self.halfsize > block.rect.top + 15) and\
               (self.get_centre()[1] - self.halfsize < block.rect.bottom - 20):
                self.pos[0] = block.rect.right - 2
                self.vel[0] = -self.vel[0]*restitution
                if abs(self.vel[0]) > 1000:
                    active_particle_systems.append(ParticleSystem(particle_no=random.randint(
                        1, 3), colour=self.colour, lifetime=0.5, radius=10, size=3, coords=[self.pos[0], self.pos[1] + self.rect.center[1]]))
            # up hitbox
            if (self.get_centre()[0] + self.halfsize > block.rect.left + 10) and\
               (self.get_centre()[0] - self.halfsize < block.rect.right - 5) and\
               (self.get_centre()[1] + self.halfsize > block.rect.top) and\
               (self.get_centre()[1] - self.halfsize < block.rect.top + 20):
                self.pos[1] = block.rect.top - self.size - 2
                self.vel[1] = -self.vel[1]*restitution
                if abs(self.vel[1]) > 1000:
                    active_particle_systems.append(ParticleSystem(particle_no=random.randint(1, 3), colour=self.colour, lifetime=0.5, radius=10, size=3, coords=[
                                                   self.pos[0] + self.rect.center[0], self.pos[1] + self.rect.bottom]))
            # down hitbox
            if (self.get_centre()[0] + self.halfsize > block.rect.left + 10) and\
               (self.get_centre()[0] - self.halfsize < block.rect.right - 5) and\
               (self.get_centre()[1] + self.halfsize > block.rect.bottom - 20) and\
               (self.get_centre()[1] - self.halfsize < block.rect.bottom):
                self.pos[1] = block.rect.bottom - 2
                self.vel[1] = -self.vel[1]*restitution
                if abs(self.vel[1]) > 1000:
                    active_particle_systems.append(ParticleSystem(particle_no=random.randint(
                        1, 3), colour=self.colour, lifetime=0.5, radius=10, size=3, coords=[self.pos[0] + self.rect.center[0], self.pos[1]]))

    def hole_collision(self):
        for hole in active_level.holes:
            np_self = np.asarray(self.get_centre())
            np_hole = np.asarray(
                [hole.pos[0] + hole.rect.center[0], hole.pos[1] + hole.rect.center[1]])
            line = np_self - np_hole
            distance = np.linalg.norm(line)
            if distance < 30:  # ball centre goes into hole
                direction = [np_hole[0] - np_self[0], np_hole[1] - np_self[1]]
                if invertcontrol != 'NO' and self.ID != invertcontrol:
                    self.vel = [-direction[0] * 200, -direction[1] * 200]
                else:
                    self.vel = [direction[0] * 200, direction[1] * 200]
                self.scaler -= 0.01
                self.image = pygame.transform.smoothscale(ball_images[self.ID], (
                    self.size*self.scaler, self.size*self.scaler))  # makes ball smaller slowly
                if self.scaler > 0.9:
                    self.brightness -= 15
                    if type(hole) == Goal:
                        self.image.fill(
                            (255, 255, 255, self.brightness), None, pygame.BLEND_RGBA_MULT)
                        self.image.fill((255-self.brightness, 255-self.brightness,
                                        255-self.brightness, 255), None, pygame.BLEND_RGB_ADD)
                    else:
                        self.image.fill(
                            (self.brightness, self.brightness, self.brightness, 255), None, pygame.BLEND_RGBA_MULT)
                else:
                    # hide ball during timeout
                    self.image.fill((255, 255, 255, 0), None,
                                    pygame.BLEND_RGBA_MULT)
                if self.scaler < 0.8:
                    if type(hole) == Goal:
                        active_particle_systems.append(ParticleSystem(particle_no=50, colour=self.colour, lifetime=2, radius=400, coords=[
                                                       hole.pos[0]+hole.rect.center[0], hole.pos[1]+hole.rect.center[1]]))
                if self.scaler < 0.7:
                    self.__init__(self.ID)  # respawn ball

    def speedup_collision(self):

        for speedup in active_level.speedup:
            np_selfsp = np.asarray(self.get_centre())
            np_speedup = np.asarray(
                [speedup.pos[0] + speedup.rect.center[0], speedup.pos[1] + speedup.rect.center[1]])
            line = np_selfsp - np_speedup
            distance = np.linalg.norm(line)
            if distance < 30:  # ball close to rocket
                return self.ID
            else:
                return 'NO'

    def invert_collision(self):

        for invert in active_level.invert:
            np_selfinv = np.asarray(self.get_centre())
            np_invert = np.asarray(
                [invert.pos[0] + invert.rect.center[0], invert.pos[1] + invert.rect.center[1]])
            invline = np_selfinv - np_invert
            distance = np.linalg.norm(invline)
            if distance < 30:  # ball close to invert
                return self.ID
            else:
                return 'NO'

    def freeze_collision(self):

        for freeze in active_level.freeze:
            np_selffr = np.asarray(self.get_centre())
            np_freeze = np.asarray(
                [freeze.pos[0] + freeze.rect.center[0], freeze.pos[1] + freeze.rect.center[1]])
            frline = np_selffr - np_freeze
            distance = np.linalg.norm(frline)
            if distance < 30:  # ball close to freeze
                return self.ID
            else:
                return 'NO'

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
                            self.pos = [random.randint(100, 1150), random.randint(100, 570)]
                            self.vel = [0, 0]
                            self.acc = [0, 0]
                            ball.kills += 1
                            self.deaths += 1

                        elif np.linalg.norm(self.vel) > np.linalg.norm(ball.vel):
                            ball.pos = [random.randint(100, 1150), random.randint(100, 570)]
                            ball.vel = [0, 0]
                            ball.acc = [0, 0]
                            self.kills += 1
                            ball.deaths += 1

    # def ball_collision (self):
    # 	for ball in balls:
    # 		if ball != None:
    # 			if ball.ID != self.ID:
    # 				np_self = np.asarray(self.get_centre())
    # 				np_ball = np.asarray(ball.get_centre())
    # 				line_of_impact = np_self - np_ball
    # 				distance = np.linalg.norm(line_of_impact) #vector magnitude
    # 				if distance < 42:	#2 radii
    # 					cos_alpha = np.dot(line_of_impact, np.array([1, 0]))/	\
    # 								(np.linalg.norm(line_of_impact)*np.linalg.norm(np.array([1, 0]))) #cosine similarity between line and +1 vector
    # 					alpha = np.arccos(np.clip(cos_alpha, -1, 1)) #vector angle
    # 					if np_self[1] > np_ball[1]:
    # 						alpha = -alpha		#0→-π
    # 					ball_impact_vel = np.linalg.norm(np.asarray(ball.vel)) #Swap velocities on relevant component (new axis)
    # 					self_vel = np.linalg.norm(np.asarray(self.vel)) #preserved momentum on irrelevant axis
    # 					if ball.vel != [0.0, 0.0]:
    # 						cos_theta = np.dot(ball_impact_vel, np.array([1, 0]))/	\
    # 									(np.linalg.norm(ball_impact_vel)*np.linalg.norm(np.array([1, 0]))) #cosine similarity between velocity and +1 vector
    # 					else: cos_theta = 0
    # 					theta = np.arccos(np.clip(cos_theta, -1, 1)) #vector angle
    # 					if ball.vel[1] > 0:
    # 						theta = -theta		#0→-π
    # 					phi = alpha - theta 	#angle between relevant impact component and velocity
    # 					impact_velocity_rel = ball_impact_vel*np.cos(phi)	#projection of velocity onto axis
    # 					velocity_irrel = self_vel*np.cos(phi + math.pi/2)
    # 					final_vel = impact_velocity_rel + velocity_irrel
    # 					self.vel = [-final_vel*np.cos(alpha), -final_vel*np.sin(alpha)]		#return to global x, y components


def hex_to_dec(hex):
    d = int(hex, 16)
    if d < 2147483648:  # h80000000
        return d
    else:
        return d - 4294967296  # hFFFFFFFF+1


class Level:
    def __init__(self, block_coords, hole_coords, colour, bg_colour, edge_colour, goal_colour, speedup_coords, invert_coords, freeze_coords):
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
        self.speedup = []
        self.speedup.append(Speedup(speedup_coords))
        self.invert = []
        self.invert.append(Invert(invert_coords))
        self.freeze = []
        self.freeze.append(Freeze(freeze_coords))

    def draw_frame(self):
        # parallax
        pygame.draw.rect(screen, active_level.edge_colour,
                         pygame.Rect(10, 0, 83, 720))
        pygame.draw.rect(screen, active_level.edge_colour,
                         pygame.Rect(1190, 0, 80, 720))
        pygame.draw.rect(screen, active_level.edge_colour,
                         pygame.Rect(0, 10, 1280, 74))
        pygame.draw.rect(screen, active_level.edge_colour,
                         pygame.Rect(0, 635, 1280, 80))
        # frame
        pygame.draw.rect(screen, active_level.colour,
                         pygame.Rect(0, 0, 83, 720))
        pygame.draw.rect(screen, active_level.colour,
                         pygame.Rect(1200, 0, 80, 720))
        pygame.draw.rect(screen, active_level.colour,
                         pygame.Rect(0, 0, 1280, 74))
        pygame.draw.rect(screen, active_level.colour,
                         pygame.Rect(0, 644, 1280, 80))


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
        pygame.draw.rect(screen, active_level.edge_colour,
                         pygame.Rect(10, 0, 83, 720))
        pygame.draw.rect(screen, active_level.edge_colour,
                         pygame.Rect(1190, 0, 80, 720))
        pygame.draw.rect(screen, active_level.edge_colour,
                         pygame.Rect(0, 10, 1280, 74))
        pygame.draw.rect(screen, active_level.edge_colour,
                         pygame.Rect(0, 635, 1280, 80))
        # frame
        pygame.draw.rect(screen, active_level.colour,
                         pygame.Rect(0, 0, 83, 720))
        pygame.draw.rect(screen, active_level.colour,
                         pygame.Rect(1200, 0, 80, 720))
        pygame.draw.rect(screen, active_level.colour,
                         pygame.Rect(0, 0, 1280, 74))
        pygame.draw.rect(screen, active_level.colour,
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


class Goal (Hole):
    def __init__(self, coords, colour):
        self.white = goal_white_image
        self.image = goal_glow_image.copy()
        self.image.fill(colour, None, pygame.BLEND_RGBA_MULT)
        self.rect = self.image.get_rect()
        self.pos = [coords[0], coords[1]]


class ParticleSystem ():
    def __init__(self, particle_no, colour, lifetime, radius, coords, type="burst", angle=0, size=5):
        self.particles = []
        for i in range(particle_no):
            self.particles.append(
                Particle(colour, lifetime, radius, coords, angle, size))


class Particle ():
    def __init__(self, colour, lifetime, radius, coords, angle, size):
        self.randomlifetime = random.uniform(lifetime*0.8, lifetime*1.2)
        self.colour = colour
        self.size = size
        self.pos = [coords[0], coords[1]]
        self.magnitude = random.randint(25, 100) * radius
        self.angle = random.uniform(0, 2*math.pi)
        self.vel = [self.magnitude *
                    np.cos(self.angle), self.magnitude*np.sin(self.angle)]
        self.veer = [random.randint(-500, 500),
                     random.randint(-500, 500)]  # random turn

    def motion(self, dt):
        self.veer = [self.veer[0]*0.93, self.veer[1]*0.93]  # attenuate veer
        self.vel = [self.vel[0]-self.veer[0],
                    self.vel[1]-self.veer[1]]  # apply veer
        self.vel = [self.vel[0]*0.9, self.vel[1]*0.9]  # attenuate speed
        self.pos[0] += self.vel[0]*dt
        self.pos[1] += self.vel[1]*dt

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
    pygame.draw.rect(screen, active_level.edge_colour, pygame.Rect(
        scaled[0], scaled[1], scaled[2], scaled[3]))


class Speedup:
    def __init__(self, coords):
        self.image = speedup_image
        self.rect = self.image.get_rect()
        self.pos = [coords[0], coords[1]]
        self.brightness = 200


class Invert:
    def __init__(self, coords):
        self.image = invert_image
        self.rect = self.image.get_rect()
        self.pos = [coords[0], coords[1]]
        self.brightness = 155


class Freeze:
    def __init__(self, coords):
        self.image = freeze_image
        self.rect = self.image.get_rect()
        self.pos = [coords[0], coords[1]]
        self.brightness = 200


level1_blocks = [(300, 50, 60, 320),
                 (750, 300, 60, 380)]
level1_holes = [(1020, 450),  # first hole is always the goal
                (500, 100),
                (600, 500),
                (1000, 200)]
level1_speedup = (630, 300)
level1_invert = (1080, 250)
level1_freeze = (350, 550)
level1_colour = (190, 25, 90)  # Magenta
level1_bg_colour = (120, 15, 70)
level1_edge_colour = (100, 10, 60)
level1_goal_colour = (255, 110, 160, 255)  # RGBA
level1 = Level(level1_blocks, level1_holes, level1_colour, level1_bg_colour,
               level1_edge_colour, level1_goal_colour, level1_speedup, level1_invert, level1_freeze)

level2_blocks = [(400, 50, 60, 300),
                 (600, 300, 60, 380),
                 (1100, 200, 300, 60)]
level2_holes = [(1020, 450),  # first hole is always the goal
                (100, 250),
                (200, 500),
                (800, 300),
                (1000, 400),
                (1100, 350)]
level2_speedup = (300, 550)
level2_invert = (1100, 120)
level2_freeze = (1000, 300)
level2_colour = (129, 77, 189)  # Light Purple
level2_bg_colour = (81, 8, 163)  # Dark purple
level2_edge_colour = (60, 2, 127)
level2_goal_colour = (250, 200, 255, 255)  # RGBA
level2 = Level(level2_blocks, level2_holes, level2_colour, level2_bg_colour,
               level2_edge_colour, level2_goal_colour, level2_speedup, level2_invert, level2_freeze)

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
level3_speedup = (660, 550)
level3_invert = (1050, 520)
level3_freeze = (390, 110)
level3_colour = (41, 204, 73)  # Light green
level3_bg_colour = (44, 153, 66)  # Dark green
level3_edge_colour = (27, 112, 44)
level3_goal_colour = (200, 255, 200, 255)  # RGBA
level3 = Level(level3_blocks, level3_holes, level3_colour, level3_bg_colour,
               level3_edge_colour, level3_goal_colour, level3_speedup, level3_invert, level3_freeze)

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
level4_speedup = (800, 120)
level4_invert = (1080, 300)
level4_freeze = (400, 500)
level4_colour = (222, 139, 91)  # Light orange
level4_bg_colour = (191, 87, 27)  # Dark orange
level4_edge_colour = (172, 75, 19)
level4_goal_colour = (255, 230, 200, 255)  # RGBA
level4 = Level(level4_blocks, level4_holes, level4_colour, level4_bg_colour,
               level4_edge_colour, level4_goal_colour, level4_speedup, level4_invert, level4_freeze)

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
level5_speedup = (560, 270)
level5_invert = (900, 190)
level5_freeze = (110, 380)
level5_colour = (89, 164, 222)  # Light blue
level5_bg_colour = (13, 110, 184)  # Dark blue
level5_edge_colour = (13, 77, 181)
level5_goal_colour = (200, 230, 255, 255)  # RGBA
level5 = Level(level5_blocks, level5_holes, level5_colour, level5_bg_colour,
               level5_edge_colour, level5_goal_colour, level5_speedup, level5_invert, level5_freeze)


dodgeball_blocks = [(250, 550, 40, 40), (1050, 400, 30, 30),
                    (725, 130, 35, 35), (650, 450, 27, 27), (400, 260, 30, 30)]
dodgeball_speedup = (0, 0)
dodgeball_invert = (0, 0)
dodgeball_freeze = (0, 0)
dodgeball_colour = (100, 150, 200)
dodgeball_bg_colour = (83, 91, 131)
dodgeball_edge_colour = (13, 77, 181)
dodgeball = Dodgeball(dodgeball_blocks, dodgeball_colour,
                      dodgeball_bg_colour, dodgeball_edge_colour)


active_level = dodgeball

active_balls = 0
for i in range(4):
    balls[i] = Ball(i)
    active_balls += 1

active_particle_systems = []

running = True

font = pygame.font.SysFont('Futura', 20, False, True)


while running:
    clock.tick(60)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill(active_level.bg_colour)

    for i, block in enumerate(active_level.blocks):
        draw_parallax(block)

    active_level.draw_frame()

    for block in active_level.blocks:
        pygame.draw.rect(screen, active_level.colour, block.rect)

    screen.blit(vignette, (0, 0))

    if active_level != dodgeball:
        for hole in active_level.holes:
            screen.blit(hole.image, (hole.pos[0], hole.pos[1]))
        goal_centre = [active_level.holes[0].pos[0] +
                       60, active_level.holes[0].pos[1] + 60]
        screen.blit(active_level.holes[0].white,
                    (goal_centre[0], goal_centre[1]))

        for speedup in active_level.speedup:
            screen.blit(speedup.image, (speedup.pos[0], speedup.pos[1]))

        for invert in active_level.invert:
            screen.blit(invert.image, (invert.pos[0], invert.pos[1]))

        for freeze in active_level.freeze:
            screen.blit(freeze.image, (freeze.pos[0], freeze.pos[1]))

    for ball in balls:
        if ball != None:
            ball.acc = [0, 0]

    keys = pygame.key.get_pressed()
    if keys[pygame.K_w]:
        balls[0].acc[1] = hex_to_dec("CCCCCCCC")
    if keys[pygame.K_s]:
        balls[0].acc[1] = hex_to_dec("33333333")
    if keys[pygame.K_d]:
        balls[0].acc[0] = hex_to_dec("33333333")
    if keys[pygame.K_a]:
        balls[0].acc[0] = hex_to_dec("CCCCCCCC")

    if keys[pygame.K_UP]:
        balls[1].acc[1] = hex_to_dec("CCCCCCCC")
    if keys[pygame.K_DOWN]:
        balls[1].acc[1] = hex_to_dec("33333333")
    if keys[pygame.K_RIGHT]:
        balls[1].acc[0] = hex_to_dec("33333333")
    if keys[pygame.K_LEFT]:
        balls[1].acc[0] = hex_to_dec("CCCCCCCC")

    if keys[pygame.K_i]:
        balls[2].acc[1] = hex_to_dec("CCCCCCCC")
    if keys[pygame.K_k]:
        balls[2].acc[1] = hex_to_dec("33333333")
    if keys[pygame.K_l]:
        balls[2].acc[0] = hex_to_dec("33333333")
    if keys[pygame.K_j]:
        balls[2].acc[0] = hex_to_dec("CCCCCCCC")

    if keys[pygame.K_KP5]:
        balls[3].acc[1] = hex_to_dec("CCCCCCCC")
    if keys[pygame.K_KP2]:
        balls[3].acc[1] = hex_to_dec("33333333")
    if keys[pygame.K_KP3]:
        balls[3].acc[0] = hex_to_dec("33333333")
    if keys[pygame.K_KP1]:
        balls[3].acc[0] = hex_to_dec("CCCCCCCC")

    for ball in balls:
        if ball != None and active_level != dodgeball:

            ball.motion_calc(dt)
            ball.frame_collision()
            ball.block_collision()
            ball.hole_collision()

            if ball.speedup_collision() != 'NO':
                gofast = ball.speedup_collision()
                speedup.brightness += 55
                screen.blit(speedup.image, (speedup.pos[0], speedup.pos[1]))
                speedup.pos = [0, 0]
                speedup.image = pygame.image.load("assets/transparent.png")
                starttimesp = time.time()
            if time.time() > starttimesp + 3:
                gofast = 'NO'

            if ball.invert_collision() != 'NO':
                invertcontrol = ball.invert_collision()
                invert.brightness += 100
                screen.blit(invert.image, (invert.pos[0], invert.pos[1]))
                invert.pos = [0, 0]
                invert.image = pygame.image.load("assets/transparent.png")
                starttimeinv = time.time()
            if time.time() > starttimeinv + 5:
                invertcontrol = 'NO'

            if ball.freeze_collision() != 'NO':
                freezeball = ball.freeze_collision()
                freeze.brightness += 55
                screen.blit(freeze.image, (freeze.pos[0], freeze.pos[1]))
                freeze.pos = [0, 0]
                freeze.image = pygame.image.load("assets/transparent.png")
                starttimefr = time.time()
            if time.time() > starttimefr + 3:
                freezeball = 'NO'
            screen.blit(ball.image, (ball.pos[0], ball.pos[1]))

        elif ball != None and active_level == dodgeball:
            ball.motion_calc(dt)
            ball.frame_collision()
            ball.block_collision()
            ball.ball_kill()
            screen.blit(ball.image, (ball.pos[0], ball.pos[1]))

    for system in active_particle_systems:
        for particle in system.particles:
            particle.motion(dt)
            particle.lifetime(system.particles)
            if len(system.particles) == 0:
                active_particle_systems.remove(system)
            pygame.draw.rect(
                screen, particle.colour, (particle.pos[0], particle.pos[1], particle.size, particle.size))

    for ball in balls:
         if ball != None and active_level == dodgeball:
            if ball.colour == (230, 230, 230):
                colour = "Silver Ball"
            elif ball.colour == (255, 255, 170):
                colour = "Gold Ball"
            elif ball.colour == (170, 255, 170):
                colour = "Green Ball"
            elif ball.colour == (170, 220, 255):
                colour = "Blue Ball"

            kills = font.render(colour + " kills: " + str(ball.kills), True, (255, 255, 255))
            deaths = font.render(colour + " deaths: " + str(ball.deaths), True, (255, 255, 255))
            screen.blit(kills, (ball.ID*200 + 250, 10))
            screen.blit(deaths, (ball.ID * 200 + 250, 40))

    pygame.display.update()
