import pygame, random, math
import numpy as np

pygame.init()

screen = pygame.display.set_mode((1280,720))
pygame.display.set_caption(" ")#################

vignette = pygame.image.load("assets/vignette.png")
hole_image = pygame.image.load("assets/hole.png")
goal_image = pygame.image.load("assets/goal.png").convert_alpha()
ball_images = [pygame.image.load("assets/ball.png").convert_alpha(), pygame.image.load("assets/ball_y.png").convert_alpha(),
				pygame.image.load("assets/ball_g.png").convert_alpha(), pygame.image.load("assets/ball_b.png").convert_alpha()]

ball_initial_pos = [[150, 100], [110, 140], [190, 140], [150, 180]]  #[X, Y]

balls = [None, None, None, None]

friction = 0.95
restitution = 0.6
dt = 0.001
clock = pygame.time.Clock()

class Ball:
	def __init__ (self, ID):
		self.ID = ID
		self.acc = [0, 0]
		self.vel = [0, 0]
		self.pos = ball_initial_pos[ID].copy()
		self.damping = 1000
		self.image = ball_images[ID]
		self.rect = self.image.get_rect()
		self.size = 40
		self.halfsize = 20
		self.scaler = 1
		self.brightness = 255

	def get_centre (self):
		return [self.pos[0] + self.rect.center[0], self.pos[1] + self.rect.center[1]] #centre on global coords

	def motion_calc (self, dt):
		ball.vel[0] += self.acc[0]*dt/self.damping	#v = u + at
		ball.vel[1] += self.acc[1]*dt/self.damping

		ball.vel[0] = self.vel[0]*friction
		ball.vel[1] = self.vel[1]*friction

		ball.pos[0] += self.vel[0]*dt
		ball.pos[1] += self.vel[1]*dt

	def frame_collision (self):
		if self.get_centre()[0] - self.rect.center[0] < 82:		#left hitbox
			self.pos[0] = 82
			self.vel[0] = -self.vel[0]*restitution
		if self.get_centre()[0] + self.rect.center[0] > 1200:	#right hitbox
			self.pos[0] = 1156
			self.vel[0] = -self.vel[0]*restitution
		if self.get_centre()[1] - self.rect.center[1] < 74:		#up hitbox
			self.pos[1] = 74
			self.vel[1] = -self.vel[1]*restitution
		if self.get_centre()[1] + self.rect.center[1] > 645:	#down hitbox
			self.pos[1] = 601
			self.vel[1] = -self.vel[1]*restitution

	def block_collision (self):
		for block in active_level.blocks:
			#left hitbox
			if (self.get_centre()[0] + self.halfsize > block.rect.left) and\
			   (self.get_centre()[0] - self.halfsize < block.rect.left + 20) and\
			   (self.get_centre()[1] + self.halfsize > block.rect.top + 15) and\
			   (self.get_centre()[1] - self.halfsize < block.rect.bottom - 15):
				self.pos[0] = block.rect.left - self.size - 2
				self.vel[0] = -self.vel[0]*restitution
			#right hitbox
			if (self.get_centre()[0] + self.halfsize > block.rect.right - 20) and\
			   (self.get_centre()[0] - self.halfsize < block.rect.right) and\
			   (self.get_centre()[1] + self.halfsize > block.rect.top + 15) and\
			   (self.get_centre()[1] - self.halfsize < block.rect.bottom - 20):
				self.pos[0] = block.rect.right - 2
				self.vel[0] = -self.vel[0]*restitution
			#up hitbox
			if (self.get_centre()[0] + self.halfsize > block.rect.left + 10) and\
			   (self.get_centre()[0] - self.halfsize < block.rect.right - 5) and\
			   (self.get_centre()[1] + self.halfsize > block.rect.top) and\
			   (self.get_centre()[1] - self.halfsize < block.rect.top + 20):
				self.pos[1] = block.rect.top - self.size - 2
				self.vel[1] = -self.vel[1]*restitution
			#down hitbox
			if (self.get_centre()[0] + self.halfsize > block.rect.left + 10) and\
			   (self.get_centre()[0] - self.halfsize < block.rect.right - 5) and\
			   (self.get_centre()[1] + self.halfsize > block.rect.bottom - 20) and\
			   (self.get_centre()[1] - self.halfsize < block.rect.bottom):
				self.pos[1] = block.rect.bottom - 2
				self.vel[1] = -self.vel[1]*restitution

	def hole_collision (self):
		for hole in active_level.holes:
				np_self = np.asarray(self.get_centre())
				np_hole = np.asarray([hole.pos[0] + hole.rect.center[0], hole.pos[1] + hole.rect.center[1]])
				line = np_self - np_hole
				distance = np.linalg.norm(line)
				if distance < 30:	#ball centre goes into hole
					direction = [np_hole[0] - np_self[0], np_hole[1] - np_self[1]]
					self.vel = [direction[0]*200, direction[1]*200]
					self.scaler -= 0.01
					self.image = pygame.transform.smoothscale(ball_images[self.ID], (self.size*self.scaler, self.size*self.scaler)) #makes ball smaller slowly
					self.brightness -= 15
					if self.scaler > 0.9:
						self.image.fill((self.brightness, self.brightness, self.brightness, 255), None, pygame.BLEND_RGBA_MULT)
					else:
						self.image.fill((255, 255, 255, 0), None, pygame.BLEND_RGBA_MULT) #hide ball during timeout
					if self.scaler < 0.7:
						self.__init__(self.ID) #respawn ball

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


def hex_to_dec (hex):
	d = int(hex, 16)
	if d < 2147483648: #h80000000
		return d
	else:
		return d - 4294967296 #hFFFFFFFF+1

class Level:
	def __init__ (self, block_coords, hole_coords, colour, bg_colour, shadow_colour):
		self.colour = colour
		self.bg_colour = bg_colour
		self.shadow_colour = shadow_colour
		self.blocks = []
		for i in range(len(block_coords)):
			self.blocks.append(Block(block_coords[i]))
		self.holes = []
		self.holes.append(Goal(hole_coords[0]))
		for i in range(1, len(hole_coords)):
			self.holes.append(Hole(hole_coords[i]))

	def draw_frame (self):
		#parallax
		pygame.draw.rect(screen, active_level.shadow_colour, pygame.Rect(10, 0, 83, 720))
		pygame.draw.rect(screen, active_level.shadow_colour, pygame.Rect(1190, 0, 80, 720))
		pygame.draw.rect(screen, active_level.shadow_colour, pygame.Rect(0, 10, 1280, 74))
		pygame.draw.rect(screen, active_level.shadow_colour, pygame.Rect(0, 635, 1280, 80))
		#frame
		pygame.draw.rect(screen, active_level.colour, pygame.Rect(0, 0, 83, 720))
		pygame.draw.rect(screen, active_level.colour, pygame.Rect(1200, 0, 80, 720))
		pygame.draw.rect(screen, active_level.colour, pygame.Rect(0, 0, 1280, 74))
		pygame.draw.rect(screen, active_level.colour, pygame.Rect(0, 644, 1280, 80))


class Block:
	def __init__ (self, coords):
		self.rect = pygame.Rect(coords[0], coords[1], coords[2], coords[3])
		self.pos = [coords[0], coords[1]]

class Hole:
	def __init__ (self, coords):
		self.image = hole_image
		self.rect = self.image.get_rect()
		self.pos = [coords[0], coords[1]]

class Goal (Hole):
	def __init__ (self, coords):
		self.image = goal_image
		self.rect = self.image.get_rect()
		self.pos = [coords[0], coords[1]]

def draw_parallax (object):
	scale_factorX = (640 - object.rect.center[0]) / 100
	scale_factorY = (360 - object.rect.center[1]) / 100
	scaled = [object.pos[0] + scale_factorX,
			  object.pos[1] + scale_factorY,
			  object.rect.right - object.pos[0] + scale_factorX,
			  object.rect.bottom - object.pos[1] + scale_factorY]
	pygame.draw.rect(screen, active_level.shadow_colour, pygame.Rect(scaled[0], scaled[1], scaled[2], scaled[3]))

active_balls = 0
for i in range(4):
	balls[i] = Ball(i)
	active_balls += 1

level1_blocks = [(280, 70, 80, 500),
				 (600, 200, 80, 500),
				 (1000, 120, 80, 80)]
level1_holes = [(1050, 300), #first hole is always the goal
				(800, 500)]
level1_colour = (190,25,90) #Magenta
level1_bg_colour = (120,15,70)
level1_shadow_colour = (100,10,60)
level1 = Level(level1_blocks, level1_holes, level1_colour, level1_bg_colour, level1_shadow_colour)
active_level = level1

running = True

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

	for hole in active_level.holes:
		screen.blit(hole.image, (hole.pos[0], hole.pos[1]))


	for ball in balls:
		if ball != None:
			ball.acc = [0,0]

	screen.blit(vignette, (0, 0))

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
		if ball != None:
			ball.motion_calc(dt)
			ball.frame_collision()
			ball.block_collision()
			ball.hole_collision()
			screen.blit(ball.image, (ball.pos[0], ball.pos[1]))

	pygame.display.update()