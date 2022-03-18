import pygame, pygame.gfxdraw
import math, time, random
import numpy as np
import socket

pygame.init()

screen = pygame.display.set_mode((1280,720))
pygame.display.set_caption("The Maze Game")

vignette = pygame.image.load("assets/vignette.png")
hole_image = pygame.image.load("assets/hole.png")
goal_glow_image = pygame.image.load("assets/goal_glow.png").convert_alpha()
goal_white_image = pygame.image.load("assets/goal_white.png").convert_alpha()
speedup_image = pygame.image.load("assets/boost_powerup.png")
invert_image = pygame.image.load("assets/invert_powerup.png")
freeze_image = pygame.image.load("assets/freeze_powerup.png")
ghost_image = pygame.image.load("assets/ghost_powerup.png")
transparent = pygame.image.load(("assets/transparent.png"))
ball_images = [pygame.image.load("assets/ball.png").convert_alpha(), pygame.image.load("assets/ball_y.png").convert_alpha(),
				pygame.image.load("assets/ball_g.png").convert_alpha(), pygame.image.load("assets/ball_b.png").convert_alpha()]
ball_colours = [(230, 230, 230), (255, 255, 170), (170, 255, 170), (170, 220, 255)]

ball_initial_pos = [[150, 100], [110, 140], [190, 140], [150, 180]]  #[X, Y]

balls = [None, None, None, None]
connected_balls = [None, None, None, None]
ball_sensitivities = [5000, 5000, 5000, 5000]

class Ball:

	friction = 0.95 #gradual slowing
	restitution = 0.6 #bounce
	scores = [0, 0, 0, 0]
	kills = [0, 0, 0, 0]
	lives = [10, 10, 10, 10]
	won = [] #list to determine how many balls have won, and when to change level

	def __init__ (self, ID):
		self.ID = ID
		self.acc = [0, 0]
		self.vel = [0, 0]
		self.pos = ball_initial_pos[ID].copy() if Level.active_level != dodgeball else [random.randint(100, 1150), random.randint(100, 570)]
		self.sensitivity = ball_sensitivities[ID]
		self.colour = ball_colours[ID]
		self.image = ball_images[ID].copy()
		self.rect = self.image.get_rect()
		self.size = 45
		self.halfsize = 20
		self.scaler = 1.0
		self.brightness = 255
		self.respawn_timer = 20 #ms
		self.speedup = False
		self.invert_others = False
		self.ghost = False
		self.freeze_others = False
		self.poweruptimer = 200

	def respawn_animation (self):
		if self.respawn_timer == 20:
			self.pos[0] -= 10 #fixes ball drawn from top left
			self.pos[1] -= 10
			self.scaler = 1.9
		elif self.respawn_timer > 10:
			self.pos[0] += 2
			self.pos[1] += 2
			self.scaler -= 0.1
		elif self.respawn_timer > 5:
			if self.respawn_timer == 10:
				ParticleSystem.active_systems.append(ParticleSystem(particle_no=20, colour=self.colour, lifetime=0.5, distance=200, size=3, coords=[self.pos[0] + self.rect.center[0], self.pos[1] + self.rect.center[1]]))
			self.pos[0] -= 1
			self.pos[1] -= 1
			self.scaler += 0.1
		else:
			self.pos[0] += 1
			self.pos[1] += 1
			self.scaler -= 0.1
			if self.respawn_timer == 1:
				ParticleSystem.active_systems.append(ParticleSystem(particle_no=10, colour=self.colour, lifetime=0.5, distance=100, size=3, coords=[self.pos[0] + self.rect.center[0], self.pos[1] + self.rect.center[1]]))
		self.scaler = round(self.scaler, 2)
		self.respawn_timer = max(0, self.respawn_timer - 1)
		self.image = pygame.transform.smoothscale(ball_images[self.ID].copy(), (self.size*self.scaler, self.size*self.scaler))


	def get_centre (self):
		return [self.pos[0] + self.rect.center[0], self.pos[1] + self.rect.center[1]] #centre on global coords

	def motion_calc (self, dt):
		freeze = False
		invert = False
		for ball in balls:
			if ball != None and ball != self:
				if ball.freeze_others:
					freeze = True
				if ball.invert_others:
					invert = True

		if self.speedup:
			self.vel[0] += 2*self.acc[0]*dt*self.sensitivity  # v = u + at
			self.vel[1] += 2*self.acc[1]*dt*self.sensitivity

		elif freeze:
			self.vel[0] = 0
			self.vel[1] = 0
		else:
			self.vel[0] += self.acc[0]*dt*self.sensitivity	#v = u + at
			self.vel[1] += self.acc[1]*dt*self.sensitivity

		self.vel[0] = self.vel[0]*Ball.friction
		self.vel[1] = self.vel[1]*Ball.friction

		if invert:
			self.pos[0] -= self.vel[0] * dt
			self.pos[1] -= self.vel[1] * dt
		else:
			self.pos[0] += self.vel[0] * dt
			self.pos[1] += self.vel[1] * dt

	def frame_collision (self):
		if self.get_centre()[0] - self.rect.center[0] < 82:		#left hitbox
			self.pos[0] = 82
			self.vel[0] = -self.vel[0]*Ball.restitution
			if abs(self.vel[0]) > 1000:
				ParticleSystem.active_systems.append(ParticleSystem(particle_no=random.randint(1,3), colour=self.colour, lifetime=0.5, distance=10, size=3, coords=[self.pos[0], self.pos[1] + self.rect.center[1]]))
		if self.get_centre()[0] + self.rect.center[0] > 1200:	#right hitbox
			self.pos[0] = 1156
			self.vel[0] = -self.vel[0]*Ball.restitution
			if abs(self.vel[0]) > 1000:
				ParticleSystem.active_systems.append(ParticleSystem(particle_no=random.randint(1,3), colour=self.colour, lifetime=0.5, distance=10, size=3, coords=[self.pos[0] + self.rect.right, self.pos[1] + self.rect.center[1]]))
		if self.get_centre()[1] - self.rect.center[1] < 72:		#up hitbox
			self.pos[1] = 72
			self.vel[1] = -self.vel[1]*Ball.restitution
			if abs(self.vel[1]) > 1000:
				ParticleSystem.active_systems.append(ParticleSystem(particle_no=random.randint(1,3), colour=self.colour, lifetime=0.5, distance=10, size=3, coords=[self.pos[0] +  self.rect.center[0], self.pos[1]]))
		if self.get_centre()[1] + self.rect.center[1] > 645:	#down hitbox
			self.pos[1] = 601
			self.vel[1] = -self.vel[1]*Ball.restitution
			if abs(self.vel[1]) > 1000:
				ParticleSystem.active_systems.append(ParticleSystem(particle_no=random.randint(1,3), colour=self.colour, lifetime=0.5, distance=10, size=3, coords=[self.pos[0] +  self.rect.center[0], self.pos[1] + self.rect.bottom]))

	def block_collision (self):
		for block in Level.active_level.blocks:
			#left hitbox
			if (self.get_centre()[0] + self.halfsize > block.rect.left - 1) and\
			   (self.get_centre()[0] - self.halfsize < block.rect.left + 20) and\
			   (self.get_centre()[1] + self.halfsize > block.rect.top + 15) and\
			   (self.get_centre()[1] - self.halfsize < block.rect.bottom - 15):
				self.pos[0] = block.rect.left - self.size + 2
				self.vel[0] = -self.vel[0]*Ball.restitution
				if abs(self.vel[0]) > 1000:
					ParticleSystem.active_systems.append(ParticleSystem(particle_no=random.randint(1,3), colour=self.colour, lifetime=0.5, distance=10, size=3, coords=[self.pos[0] + self.rect.right, self.pos[1] + self.rect.center[1]]))
			#right hitbox
			if (self.get_centre()[0] + self.halfsize > block.rect.right - 20) and\
			   (self.get_centre()[0] - self.halfsize < block.rect.right) and\
			   (self.get_centre()[1] + self.halfsize > block.rect.top + 15) and\
			   (self.get_centre()[1] - self.halfsize < block.rect.bottom - 20):
				self.pos[0] = block.rect.right - 2
				self.vel[0] = -self.vel[0]*Ball.restitution
				if abs(self.vel[0]) > 1000:
					ParticleSystem.active_systems.append(ParticleSystem(particle_no=random.randint(1,3), colour=self.colour, lifetime=0.5, distance=10, size=3, coords=[self.pos[0], self.pos[1] + self.rect.center[1]]))
			#up hitbox
			if (self.get_centre()[0] + self.halfsize > block.rect.left + 10) and\
			   (self.get_centre()[0] - self.halfsize < block.rect.right - 5) and\
			   (self.get_centre()[1] + self.halfsize > block.rect.top) and\
			   (self.get_centre()[1] - self.halfsize < block.rect.top + 20):
				self.pos[1] = block.rect.top - self.size + 3
				self.vel[1] = -self.vel[1]*Ball.restitution
				if abs(self.vel[1]) > 1000:
					ParticleSystem.active_systems.append(ParticleSystem(particle_no=random.randint(1,3), colour=self.colour, lifetime=0.5, distance=10, size=3, coords=[self.pos[0] +  self.rect.center[0], self.pos[1] + self.rect.bottom]))
			#down hitbox
			if (self.get_centre()[0] + self.halfsize > block.rect.left + 10) and\
			   (self.get_centre()[0] - self.halfsize < block.rect.right - 5) and\
			   (self.get_centre()[1] + self.halfsize > block.rect.bottom - 20) and\
			   (self.get_centre()[1] - self.halfsize < block.rect.bottom):
				self.pos[1] = block.rect.bottom - 2
				self.vel[1] = -self.vel[1]*Ball.restitution
				if abs(self.vel[1]) > 1000:
					ParticleSystem.active_systems.append(ParticleSystem(particle_no=random.randint(1,3), colour=self.colour, lifetime=0.5, distance=10, size=3, coords=[self.pos[0] +  self.rect.center[0], self.pos[1]]))

	def hole_collision (self):
		for hole in Level.active_level.holes:
				np_self = np.asarray(self.get_centre())
				np_hole = np.asarray([hole.pos[0] + hole.rect.center[0], hole.pos[1] + hole.rect.center[1]])
				line = np_self - np_hole
				distance = np.linalg.norm(line)
				if distance < 30:	#ball centre goes into hole
					direction = [np_hole[0] - np_self[0], np_hole[1] - np_self[1]]
					self.vel = [direction[0]*200, direction[1]*200]
					self.scaler -= 0.01
					self.scaler = round(self.scaler, 2)
					self.image = pygame.transform.smoothscale(ball_images[self.ID].copy(), (self.size*self.scaler, self.size*self.scaler)) #makes ball smaller slowly
					if self.scaler > 0.9:
						self.brightness = max(0, self.brightness - 15)
						if type(hole) == Goal:
							self.image.fill((255, 255, 255, self.brightness), None, pygame.BLEND_RGBA_MULT)
							self.image.fill((255-self.brightness, 255-self.brightness, 255-self.brightness, 255), None, pygame.BLEND_RGB_ADD)
						else:
							self.image.fill((self.brightness, self.brightness, self.brightness, 255), None, pygame.BLEND_RGBA_MULT)
					else:
						self.image.fill((255, 255, 255, 0), None, pygame.BLEND_RGBA_MULT) #hide ball during timeout
					if self.scaler < 0.8:
						if type(hole) == Goal:
							ParticleSystem.active_systems.append(ParticleSystem(particle_no=50, colour=self.colour, lifetime=2, distance=400, coords=[hole.pos[0]+hole.rect.center[0], hole.pos[1]+hole.rect.center[1]]))
					if self.scaler < 0.7:
						if type(hole) == Goal:
							Ball.scores[self.ID] += 40 - (len(Ball.won) * 10) #scores are 40, 30, 20, 10 in that order
							Ball.won.append(self.ID) #New ball has won
							balls[self.ID] = None #No other way in python to delete an instance
							num_balls = [ball for ball in connected_balls if ball != None]
							if len(Ball.won) == len(num_balls):
								update_level()
						else:
							Ball.scores[self.ID]  = max(0, Ball.scores[self.ID] - 5) #prevents negative scores
							self.__init__(self.ID) #respawn ball if fallen into the other holes.

	def powerup_collision(self):
		np_selfpow = np.asarray(self.get_centre())
		np_pow = np.asarray([active_powerup.pos[0] + active_powerup.rect.center[0], active_powerup.pos[1] + active_powerup.rect.center[1]])
		powline = np_selfpow - np_pow
		distance = np.linalg.norm(powline)
		if distance < 60:  # ball close to powerup
			ParticleSystem.active_systems.append(ParticleSystem(particle_no=20, colour=(255,220,255), lifetime=0.2, distance=200, size=5, coords=[active_powerup.pos[0] + active_powerup.rect.center[0], active_powerup.pos[1] + active_powerup.rect.center[1]]))
			if active_powerup.type == 'speedup':
				self.speedup = True
				self.image.fill((55, 55, 55), None, pygame.BLEND_RGB_ADD)
			elif active_powerup.type == 'freeze':
				self.freeze_others = True
				for ball in balls:
					if ball != None:
						if not ball.freeze_others:
							ball.image.fill((0, 40, 55), None, pygame.BLEND_RGB_ADD)
							ParticleSystem.active_systems.append(ParticleSystem(particle_no=20, colour=(200,240,255), lifetime=2, distance=10, size=5, coords=[ball.pos[0] + ball.rect.center[0], ball.pos[1] + ball.rect.center[1]]))
			elif active_powerup.type == 'invert':
				self.invert_others = True
				for ball in balls:
					if ball!= None:
						if not ball.invert_others:
							ball.image.fill((200, 200, 200, 255), None, pygame.BLEND_RGBA_MULT)
							ParticleSystem.active_systems.append(ParticleSystem(particle_no=20, colour=(50,0,50), lifetime=1, distance=50, size=5, coords=[ball.pos[0] + ball.rect.center[0], ball.pos[1] + ball.rect.center[1]]))
			elif active_powerup.type == 'ghost':
				self.ghost = True
				self.image.fill((255, 255, 255, 100), None, pygame.BLEND_RGBA_MULT)
			active_powerup.dead = 1
			return str(active_powerup.type)
		else:
			return 'NO'


	def poweruptimeout(self):
		if self.poweruptimer == 0:
			self.speedup = False
			self.ghost = False
			self.freeze_others = False
			self.invert_others = False
			for ball in balls:
				if ball != None:
					ball.image = ball_images[ball.ID].copy()
			self.poweruptimer = 200
		elif self.poweruptimer > 0:
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
						if np.linalg.norm(ball.vel) > np.linalg.norm(self.vel): #ball kills self
							ParticleSystem.active_systems.append(ParticleSystem(particle_no=50, colour=self.colour, lifetime=2, distance=200, coords=[self.pos[0]+self.rect.center[0], self.pos[1]+self.rect.center[1]]))
							if Ball.lives[self.ID] > 1: #don't respawn the last time
								self.__init__(self.ID)
							self.vel = [0, 0]
							self.acc = [0, 0]
							Ball.kills[ball.ID] += 1
							Ball.lives[self.ID] = max(0, Ball.lives[self.ID] - 1)

						elif np.linalg.norm(self.vel) > np.linalg.norm(ball.vel): #self kills ball
							ParticleSystem.active_systems.append(ParticleSystem(particle_no=50, colour=ball.colour, lifetime=2, distance=200, coords=[ball.pos[0]+ball.rect.center[0], ball.pos[1]+ball.rect.center[1]]))
							if Ball.lives[ball.ID] > 1: #don't respawn the last time
								ball.__init__(ball.ID)
							ball.vel = [0, 0]
							ball.acc = [0, 0]
							Ball.kills[self.ID] += 1
							Ball.lives[ball.ID] = max(0, Ball.lives[ball.ID] - 1)


def hex_to_dec (hex):
	d = int(hex, 16)
	if d < 2147483648: #h80000000
		return d
	else:
		return d - 4294967296 #hFFFFFFFF+1

def update_level(choice=None): #Done once to determine that level is changing and to which level
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
			pass######################
	else:
		new_level = choice
		if choice == level1: new_powerupplacements = level1_powerup
		elif choice == level2: new_powerupplacements = level2_powerup
		elif choice == level3: new_powerupplacements = level3_powerup
		elif choice == level4: new_powerupplacements = level4_powerup
		elif choice == level5: new_powerupplacements = level5_powerup
	t = 0
	Level.changing = True

def level_change (): #Keeps happening until it sets the variable to false
	global new_level, balls, new_powerupplacements
	if t < 0.5:
		pass
	elif t < 1:
		ParticleSystem.active_systems.append(ParticleSystem(particle_no=500, colour="transition", lifetime=1, distance=8000, coords=[-200, 360], type="stream", distr="unif", angle=0, width=500, size=30))
	elif t < 1.4:
		Level.active_level = new_level
		Ball.won = []
		balls = [None, None, None, None]
		if new_level != dodgeball and Powerup.active_powerups != new_powerupplacements:
			Powerup.active_powerups = new_powerupplacements
			active_powerup.__init__(random.choice(Powerup.active_powerups), random.choice(Powerup.powerupchoices))
	elif t < 2:
		if balls[0] == None and connected_balls[0] != None: balls[0] = Ball(0) #gradually creates new balls again
	elif t < 2.2:
		if balls[1] == None and connected_balls[1] != None: balls[1] = Ball(1)
	elif t < 2.4:
		if balls[2] == None and connected_balls[2] != None: balls[2] = Ball(2)
	elif t < 2.6:
		if balls[3] == None and connected_balls[3] != None: balls[3] = Ball(3)
	else:
		Level.changing = False


def which_level (level_in): #turns level name into number
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

def draw_parallax (object):
	scale_factorX = (640 - object.rect.center[0]) / 100
	scale_factorY = (360 - object.rect.center[1]) / 100
	scaled = [object.pos[0] + scale_factorX,
			  object.pos[1] + scale_factorY,
			  object.rect.right - object.pos[0] + scale_factorX,
			  object.rect.bottom - object.pos[1] + scale_factorY]
	pygame.draw.rect(screen, Level.active_level.edge_colour, pygame.Rect(scaled[0], scaled[1], scaled[2], scaled[3]))


class Level:

	changing = False
	active_level = None

	def __init__ (self, block_coords, hole_coords, colour, bg_colour, edge_colour, goal_colour):
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

	def draw_frame (self):
		#parallax
		pygame.draw.rect(screen, Level.active_level.edge_colour, pygame.Rect(10, 0, 83, 720))
		pygame.draw.rect(screen, Level.active_level.edge_colour, pygame.Rect(1190, 0, 80, 720))
		pygame.draw.rect(screen, Level.active_level.edge_colour, pygame.Rect(0, 10, 1280, 74))
		pygame.draw.rect(screen, Level.active_level.edge_colour, pygame.Rect(0, 635, 1280, 80))
		#frame
		pygame.draw.rect(screen, Level.active_level.colour, pygame.Rect(0, 0, 83, 720))
		pygame.draw.rect(screen, Level.active_level.colour, pygame.Rect(1200, 0, 80, 720))
		pygame.draw.rect(screen, Level.active_level.colour, pygame.Rect(0, 0, 1280, 74))
		pygame.draw.rect(screen, Level.active_level.colour, pygame.Rect(0, 644, 1280, 80))


class Block:
	def __init__ (self, coords):
		self.rect = pygame.Rect(coords[0], coords[1], coords[2], coords[3])
		self.pos = [coords[0], coords[1]]

class Hole:
	def __init__ (self, coords, colour):
		self.image = hole_image
		self.rect = self.image.get_rect()
		self.pos = [coords[0], coords[1]]

class Goal (Hole):
	def __init__ (self, coords, colour):
		self.white = goal_white_image
		self.image = goal_glow_image.copy()
		self.image.fill(colour, None, pygame.BLEND_RGBA_MULT)
		self.rect = self.image.get_rect()
		self.pos = [coords[0], coords[1]]

class Dodgeball (Level):
	def __init__(self, block_coords, hole_coords, colour, bg_colour, edge_colour):
		self.colour = colour
		self.bg_colour = bg_colour
		self.edge_colour = edge_colour
		self.blocks = []
		self.holes = []
		for i in range(len(block_coords)):
			self.blocks.append(Block(block_coords[i]))

class Powerup:
	active_powerups = None
	powerupchoices = ['speedup', 'freeze', 'invert', 'ghost']

	def __init__(self, coords, name):
		if name == 'freeze':
			self.image = freeze_image
		elif name == 'speedup':
			self.image = speedup_image
		elif name == 'invert':
			self.image = invert_image
		elif name == 'ghost':
			self.image = ghost_image

		self.rect = self.image.get_rect()
		self.pos = [coords[0], coords[1]]
		self.brightness = 200
		self.type = name
		self.dead = 0
		self.respawntime = random.randint(100, 400)

	def respawn(self):
		randomrespawntime = random.randint(100, 400)
		if self.respawntime == 0 and self.dead == 1:
			self.respawntime = randomrespawntime
			self.__init__(random.choice(Powerup.active_powerups), random.choice(Powerup.powerupchoices))
		elif self.respawntime > 0 and self.dead == 1:
			self.respawntime = max(0, self.respawntime - 1)

class ParticleSystem ():

	active_systems = []

	def __init__(self, particle_no, colour, lifetime, distance, coords, type="burst", distr="gauss", angle=None, size=5, width=60):
		self.particles = []
		for i in range(particle_no):
			self.particles.append(Particle(colour, lifetime, distance, coords, type, distr, angle, size, width))

class Particle ():
	def __init__(self, colour, lifetime, distance, coords, type, distr, angle, size, width):
		self.randomlifetime = random.uniform(lifetime*0.8, lifetime*1.2)
		self.size = size
		self.magnitude = random.randint(25, 100) * distance
		self.angle = random.uniform(0, 2*math.pi) if angle == None else angle #differentiate between burst and stream
		if type == "stream":
			if distr == "gauss":
				self.pos = [coords[0], random.gauss(coords[1], width)]
			elif distr == "unif":
				self.pos = [coords[0], random.uniform(coords[1]-width, coords[1]+width)]
		else: 
			self.pos = [coords[0], coords[1]]
		if colour == "title":
			self.colour = (255, max(0, 200-abs(360-self.pos[1])*0.6), max(0, 210-abs(360-self.pos[1])*1.7)) #title gradient
		elif colour == "transition":
			random_grey = random.randint(200, 255)
			self.colour = (random_grey, random_grey, random_grey)
		else: 
			self.colour = colour 
		self.vel = [self.magnitude*np.cos(self.angle), self.magnitude*np.sin(self.angle)]
		self.veer = [random.randint(-500, 500), random.randint(-500, 500)] #random turn

	def motion (self, dt):
		self.veer = [self.veer[0]*0.93, self.veer[1]*0.93] #attenuate veer
		self.vel = [self.vel[0]-self.veer[0], self.vel[1]-self.veer[1]] #apply veer
		self.vel = [self.vel[0]*0.9, self.vel[1]*0.9] #attenuate speed
		self.pos[0] += self.vel[0]*dt
		self.pos[1] += self.vel[1]*dt

	def lifetime (self, particles):
		self.randomlifetime -= 0.05
		if self.randomlifetime < 0:
			particles.remove(self) #dead


level1_blocks = [(300, 50, 60, 320),
				(750, 300, 60, 380)]
level1_holes = [(1020, 450), #first hole is always the goal
				(500, 150),
				(400, 400),
				(620, 520),
				(1000, 350),
				(980, 200)]
level1_powerup = [(630, 300), (1080, 250), (350, 550)]
level1powerups = [level1_powerup, random.choice(Powerup.powerupchoices)]
level1_colour = (190,25,90) #Magenta
level1_bg_colour = (120,15,70)
level1_edge_colour = (100,10,60)
level1_goal_colour = (255, 110, 160, 255) #RGBA
level1 = Level(level1_blocks, level1_holes, level1_colour, level1_bg_colour, level1_edge_colour, level1_goal_colour)

level2_blocks = [(400, 50, 60, 300),
				(700, 300, 60, 380),
				(1000, 200, 300, 60)]
level2_holes = [(1020, 450), #first hole is always the goal
				(120, 300),
				(200, 500),
				(800, 300),
				(1000, 400),
				(1100, 350)]
level2_powerup = [(500, 400), (1000, 300), (1100, 110)]
level2powerups = [random.choice(level2_powerup), random.choice(Powerup.powerupchoices)]
level2_colour = (129, 77, 189) #Light Purple
level2_bg_colour = (81, 8, 163) #Dark purple
level2_edge_colour = (60, 2, 127)
level2_goal_colour = (250, 200, 255, 255) #RGBA
level2 = Level(level2_blocks, level2_holes, level2_colour, level2_bg_colour, level2_edge_colour, level2_goal_colour)

level3_blocks = [(300, 50, 60, 420),
				(600, 300, 60, 380),
				(800, 50, 60, 320)]
level3_holes = [(1020, 100), #first hole is always the goal
				(120, 550),
				(450, 450),
				(650, 200),
				(900, 100),
				(1100, 450),
				(450, 250)]
level3_powerup = [(700, 550), (1000, 520), (390, 110)]
level3powerups = [level3_powerup, random.choice(Powerup.powerupchoices)]
level3_colour = (41, 204, 73) #Light green
level3_bg_colour = (44, 153, 66) #Dark green
level3_edge_colour = (27, 112, 44)
level3_goal_colour = (200, 255, 200, 255) #RGBA
level3 = Level(level3_blocks, level3_holes, level3_colour, level3_bg_colour, level3_edge_colour, level3_goal_colour)

level4_blocks = [(500, 350, 500, 60),
				(300, 50, 60, 350),
				(600, 270, 60, 480)]
level4_holes = [(650, 450), #first hole is always the goal
				(250, 475),
				(475, 500),
				(700, 200),
				(975, 200),
				(470, 160),
				(1100, 400),
				(950, 550)]
level4_powerup = [(800, 120), (1080, 300), (350, 500)]
level4powerups = [level4_powerup, random.choice(Powerup.powerupchoices)]
level4_colour = (222, 139, 91) #Light orange
level4_bg_colour = (191, 87, 27) #Dark orange
level4_edge_colour = (172, 75, 19)
level4_goal_colour = (255, 230, 200, 255) #RGBA
level4 = Level(level4_blocks, level4_holes, level4_colour, level4_bg_colour, level4_edge_colour, level4_goal_colour)

level5_blocks = [(300, 50, 60, 120),
				(200, 300, 60, 400),
				(500, 50, 60, 320),
				(500, 550, 60, 100),
				(800, 300, 60, 500),
				(1000, 300, 340, 60)]
level5_holes = [(1020, 450), #first hole is always the goal
				(400, 200),
				(350, 350),
				(450, 400),
				(350, 550),
				(650, 550),
				(675, 150),
				(900, 400)]
level5_powerup = [(600, 270), (1050, 160), (110, 500)]
level5powerups = [level5_powerup, random.choice(Powerup.powerupchoices)]
level5_colour = (89, 164, 222) #Light blue
level5_bg_colour = (13, 110, 184 ) #Dark blue
level5_edge_colour = (13, 77, 181)
level5_goal_colour = (200, 230, 255, 255) #RGBA
level5 = Level(level5_blocks, level5_holes, level5_colour, level5_bg_colour, level5_edge_colour, level5_goal_colour)

dodgeball_blocks = [(250, 550, 50, 50), (1050, 400, 50, 50),
					(725, 130, 50, 50), (650, 450, 55, 55), (400, 260, 40, 40)]
dodgeball_holes = []
dodgeball_colour = (190, 210, 230)
dodgeball_bg_colour = (100, 100, 130)
dodgeball_edge_colour = (140, 160, 200)
dodgeball = Dodgeball(dodgeball_blocks, dodgeball_holes, dodgeball_colour,
					  dodgeball_bg_colour, dodgeball_edge_colour)

Level.active_level = level1

Powerup.active_powerups = level1_powerup
active_powerup = Powerup(random.choice(Powerup.active_powerups), random.choice(Powerup.powerupchoices))

def manual_movement (ball_ID, key1, key2, key3, key4):
	keys = pygame.key.get_pressed()
	if keys[key1]:
		if balls[ball_ID] == None and ball_ID not in Ball.won:
			balls[ball_ID] = Ball(ball_ID) #Spawn ball if doesn't exist
			connected_balls[ball_ID] = balls[ball_ID].ID #Connect ball if doesn't exist
		if balls[ball_ID] != None: balls[ball_ID].acc[1] = hex_to_dec("FFFFFF5C") #Fake HEX movement of ball (if exists) for manual override
	if keys[key2]:
		if balls[ball_ID] == None and ball_ID not in Ball.won:
			balls[ball_ID] = Ball(ball_ID) #Spawn ball if doesn't exist
			connected_balls[ball_ID] = balls[ball_ID].ID #Connect ball if doesn't exist
		if balls[ball_ID] != None: balls[ball_ID].acc[1] = hex_to_dec("A3")
	if keys[key3]:
		if balls[ball_ID] == None and ball_ID not in Ball.won:
			balls[ball_ID] = Ball(ball_ID) #Spawn ball if doesn't exist
			connected_balls[ball_ID] = balls[ball_ID].ID #Connect ball if doesn't exist
		if balls[ball_ID] != None: balls[ball_ID].acc[0] = hex_to_dec("A3")
	if keys[key4]:
		if balls[ball_ID] == None and ball_ID not in Ball.won:
			balls[ball_ID] = Ball(ball_ID) #Spawn ball if doesn't exist
			connected_balls[ball_ID] = balls[ball_ID].ID #Connect ball if doesn't exist
		if balls[ball_ID] != None: balls[ball_ID].acc[0] = hex_to_dec("FFFFFF5C")

titlefont = pygame.font.SysFont('interextrabeta', 100)
title = titlefont.render("The Maze Race", True, (255, 255, 255))
title_rect = title.get_rect()
title_rect.center = (640, 360)
levelfont = pygame.font.SysFont('interextrabeta', 50, italic=True)
score_font = pygame.font.SysFont('interextrabeta', 50)

t = 0
dt = 0.001
clock = pygame.time.Clock()
t0 = time.time()
running = True

def GUI_loop ():
	global running, t, t0
	clock.tick(60)	#keeps framerate at 60fps at most
	t += time.time() - t0	#keeps track of seconds elapsed since level start
	t0 = time.time()

	screen.fill(Level.active_level.bg_colour)


	for i, block in enumerate(Level.active_level.blocks): #draws parallax
		draw_parallax(block)

	Level.active_level.draw_frame()

	for block in Level.active_level.blocks: #draws blocks
		pygame.draw.rect(screen, Level.active_level.colour, block.rect)
	
	screen.blit(vignette, (0, 0))

	for hole in Level.active_level.holes: #draws holes
		screen.blit(hole.image, (hole.pos[0], hole.pos[1]))
	try:
		goal_centre = [Level.active_level.holes[0].pos[0] + 60, Level.active_level.holes[0].pos[1] + 60]
		screen.blit(Level.active_level.holes[0].white, (goal_centre[0], goal_centre[1]))
	except: pass

	if active_powerup.dead == 1:
		active_powerup.respawn()
	screen.blit(active_powerup.image, (active_powerup.pos[0], active_powerup.pos[1]))

	keys = pygame.key.get_pressed()
	manual_movement(0, pygame.K_w, pygame.K_s, pygame.K_d, pygame.K_a)
	manual_movement(1, pygame.K_UP, pygame.K_DOWN, pygame.K_RIGHT, pygame.K_LEFT)
	manual_movement(2, pygame.K_i, pygame.K_k, pygame.K_l, pygame.K_j)
	manual_movement(3, pygame.K_g, pygame.K_b, pygame.K_n, pygame.K_v)

	if keys[pygame.K_1]: #Manual level change
		update_level(level1)
	if keys[pygame.K_2]:
		update_level(level2)
	if keys[pygame.K_3]:
		update_level(level3)
	if keys[pygame.K_4]:
		update_level(level4)
	if keys[pygame.K_5]:
		update_level(level5)
	if keys[pygame.K_6]:
		update_level(dodgeball)
	

	for ball in balls:
		if ball != None:
			ball.frame_collision()
			if not ball.ghost:
				ball.block_collision()
			ball.hole_collision()

			if ball.powerup_collision() != 'NO':
				active_powerup.pos = [0, 0]
				active_powerup.image = transparent
			if ball.freeze_others or ball.speedup or ball.invert_others or ball.ghost:
				ball.poweruptimeout()

			if ball.respawn_timer == 0:
				if t > 2:	#Determines when to give players control
					ball.motion_calc(dt)
			else:
				ball.respawn_animation()
			screen.blit(ball.image, (ball.pos[0], ball.pos[1])) #draw ball

			if Level.active_level == dodgeball:
				ball.ball_kill()
				if Ball.lives[ball.ID] == 0:
					balls[ball.ID] = None

	if infrequent % 5  == 4:
		for ball in balls:
			if ball != None:
				ball.acc = [0,0]	#set acceleration to 0 if no key pressed. After FPGA and manual override

	if Level.active_level == level1 and not Level.changing:
		if t > 0.5 and t < 2.2: #Title stream
			y = random.randint(340, 380)+np.sin(15*t)*40
			ParticleSystem.active_systems.append(ParticleSystem(particle_no=250, colour="title", lifetime=1, distance=8000, coords=[-200, y], type="stream", distr="gauss", angle=0, size=20))

	for system in ParticleSystem.active_systems: #Draws all particle systems
		for particle in system.particles:
			particle.motion(dt)
			particle.lifetime(system.particles)
			if len(system.particles) == 0:
				ParticleSystem.active_systems.remove(system) #delete system if empty
			pygame.draw.rect(screen, particle.colour, (particle.pos[0], particle.pos[1], particle.size, particle.size)) #draw any particles

	if Level.active_level == level1 and not Level.changing:
		if t > 0.5 and t < 2.2: #Title
			screen.blit(title, title_rect)

	if (Level.active_level == level1 and t > 2.5) or Level.active_level != level1 and t > 1.6:
		if Level.active_level == dodgeball:
			level_name = levelfont.render("Dodgeball", True, (255, 255, 255))
			screen.blit(level_name, (520,10))
			ball0_text = score_font.render(str(Ball.lives[0]), True, (230, 230, 230))
			screen.blit(ball0_text, (320,650))
			ball1_text = score_font.render(str(Ball.lives[1]), True, (240, 240, 90))
			screen.blit(ball1_text, (520,650))
			ball2_text = score_font.render(str(Ball.lives[2]), True, (120, 240, 120))
			screen.blit(ball2_text, (720,650))
			ball3_text = score_font.render(str(Ball.lives[3]), True, (90, 90, 240))
			screen.blit(ball3_text, (920,650))
		else:
			what_level = which_level(Level.active_level) #Displays "Level X"
			level_num = levelfont.render(f"Level {what_level}", True, (255, 255, 255))
			screen.blit(level_num, (560,10))
			ball0_text = score_font.render(str(Ball.scores[0]), True, (230, 230, 230))
			screen.blit(ball0_text, (320,650))
			ball1_text = score_font.render(str(Ball.scores[1]), True, (240, 240, 90))
			screen.blit(ball1_text, (520,650))
			ball2_text = score_font.render(str(Ball.scores[2]), True, (120, 240, 120))
			screen.blit(ball2_text, (720,650))
			ball3_text = score_font.render(str(Ball.scores[3]), True, (90, 90, 240))
			screen.blit(ball3_text, (920,650))

	if Level.changing:
		level_change() #keeps doing this until it sets the variable to false

	pygame.display.update()

	for event in pygame.event.get():	#close button
		if event.type == pygame.QUIT:
			running = False


server_name = '3.85.233.169' #"192.168.56.1"
server_port = 12000
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.settimeout(0.01) #10ms timeout for receives, after which silent error is thrown
connection = False
send_msg = "None"
send_msg_prev = "None"

def network ():
	global recv_msg, send_msg, send_msg_prev, connection
	if connection == False:
		try:
			try: server_socket.connect((server_name, server_port))
			except:
				pass
			server_socket.send("~I'm the game".encode()) #Identifies which client is game
			print("Connected")
			connection = True
		except:
			pass
	else: #connected
		received = False
		try:
			recv_msg = server_socket.recv(1024).decode()
			if recv_msg != "":
				if ":" not in recv_msg:
					print(f"received {recv_msg}")
				received = True
		except:
			pass
		if received:
			msgs = recv_msg.split('~')[1:]
			for msg in msgs:		#Handles multiple messages in same TCP receive
				if " connected" in msg: #New FPGA connected
					ball_ID = int(msg.split(" connected")[0][-1])
					balls[ball_ID] = Ball(ball_ID) #Spawn ball
					connected_balls[ball_ID] = balls[ball_ID].ID #Connect ball
				elif " disconnected" in msg:
					ball_ID = int(msg.split(" disconnected")[0][-1])
					connected_balls[ball_ID] = None
					balls[ball_ID] = None
				else:
					sender = msg.split(',')[0]
					if sender == "s":
						pass #server messages
					else: #FPGA messages
						try:
							acc0 = msg.split(',')[1].split(":")[0]
							balls[int(sender)].acc[0] = -hex_to_dec(acc0)
							acc1 = msg.split(',')[1].split(":")[1]
							balls[int(sender)].acc[1] = hex_to_dec(acc1)
						except:
							pass
						if "buttonpress" in msg:
							if Level.active_level != dodgeball:
								update_level(dodgeball)
							else:
								update_level(level1)
						elif "switch" in msg:
							try:
								val = hex_to_dec(recv_msg.split('=')[1].split(',')[0])
								ball_sensitivities[int(sender)] = 5000 + val*10
								balls[int(sender)].sensitivity = ball_sensitivities[int(sender)]
								print(f"ball {int(sender)} sensitivity change to {balls[int(sender)].sensitivity}")
							except:
								pass
		
		if send_msg != send_msg_prev: #Check whether to send
			try:
				#server_socket.send(send_msg.encode()) ######################
				print(f"sent {send_msg}")
			except:
				pass
		send_msg_prev = send_msg

if __name__ == "__main__":
	infrequent = 0
	while running: #switches between game and networking
		if infrequent%5 == 0: #Make networking infrequent to reduce lag
			network()
		infrequent += 1
		GUI_loop()
