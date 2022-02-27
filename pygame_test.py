import pygame, random, math
import numpy as np

pygame.init()

screen = pygame.display.set_mode((1280,720))
pygame.display.set_caption("Tilt Labyrinth")#################

bg = pygame.image.load("assets/bg.png")
frame_shadow = pygame.image.load("assets/frame_shadow.png")
frame = pygame.image.load("assets/frame.png")

ball_images = [pygame.image.load("assets/ball.png"), pygame.image.load("assets/ball_y.png"),
				pygame.image.load("assets/ball_g.png"), pygame.image.load("assets/ball_b.png")]

ball_initial_pos = [[150, 100], [110, 140], [190, 140], [150, 180]]  #[X, Y]

balls = [None, None, None, None]

friction = 0.95
restitution = 0.7
dt = 0.001

class Ball:
	def __init__ (self, ID):
		self.ID = ID
		self.acc = [0, 0]
		self.vel = [0, 0]
		self.pos = ball_initial_pos[ID]
		self.damping = 500
		self.image = ball_images[ID]
		self.rect = self.image.get_rect()
		self.size = 40
		self.halfsize = 20

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
			self.pos[0] = 1157
			self.vel[0] = -self.vel[0]*restitution
		if self.get_centre()[1] - self.rect.center[1] < 74:		#up hitbox
			self.pos[1] = 74
			self.vel[1] = -self.vel[1]*restitution
		if self.get_centre()[1] + self.rect.center[1] > 645:	#down hitbox
			self.pos[1] = 602
			self.vel[1] = -self.vel[1]*restitution

	def block_collision (self):
		for block in active_level.blocks:
			#left hitbox
			if (self.get_centre()[0] + self.halfsize > block.pos[0]) and\
			   (self.get_centre()[0] - self.halfsize < block.pos[0] + 20) and\
			   (self.get_centre()[1] + self.halfsize > block.pos[1] + 15) and\
			   (self.get_centre()[1] - self.halfsize < block.pos[1] + block.rect.bottom - 15):# and\
			   #(self.get_centre()[0] < block.pos[0])):	#so it doesn't interfere with bottom hitbox
				self.pos[0] = block.pos[0] - self.size - 1
				self.vel[0] = -self.vel[0]*restitution
			#right hitbox
			if (self.get_centre()[0] + self.halfsize > block.pos[0] + block.rect.right - 20) and\
			   (self.get_centre()[0] - self.halfsize < block.pos[0] + block.rect.right) and\
			   (self.get_centre()[1] + self.halfsize > block.pos[1] + 15) and\
			   (self.get_centre()[1] - self.halfsize < block.pos[1] + block.rect.bottom - 20):# and\
			   #(self.get_centre()[0] > block.pos[0] + block.rect.right)):	#so it doesn't interfere with bottom hitbox	
				self.pos[0] = block.pos[0] + block.rect.right - 3
				self.vel[0] = -self.vel[0]*restitution
			#up hitbox
			if (self.get_centre()[0] + self.halfsize > block.pos[0] + 10) and\
			   (self.get_centre()[0] - self.halfsize < block.pos[0] + block.rect.right - 5) and\
			   (self.get_centre()[1] + self.halfsize > block.pos[1]) and\
			   (self.get_centre()[1] - self.halfsize < block.pos[1] + 20):	
				self.pos[1] = block.pos[1] - self.size - 1
				self.vel[1] = -self.vel[1]*restitution
			#down hitbox
			if (self.get_centre()[0] + self.halfsize > block.pos[0] + 10) and\
			   (self.get_centre()[0] - self.halfsize < block.pos[0] + block.rect.right - 5) and\
			   (self.get_centre()[1] + self.halfsize > block.pos[1] + block.rect.bottom - 20) and\
			   (self.get_centre()[1] - self.halfsize < block.pos[1] + block.rect.bottom):	
				self.pos[1] = block.pos[1] + block.rect.bottom - 3
				self.vel[1] = -self.vel[1]*restitution

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
	def __init__ (self, level_block_data):
		images = [tup[0] for i,tup in enumerate(level_block_data)]
		coords = [tup[1] for i,tup in enumerate(level_block_data)]
		rotate = [tup[2] for i,tup in enumerate(level_block_data)]
		self.blocks = []
		for i in range(len(coords)):
			self.blocks.append(Block(images[i], coords[i], rotate[i]))


class Block:
	def __init__ (self, image, coords, rotate):
		self.image = pygame.transform.rotate(image, rotate)
		self.pos = coords
		self.rect = self.image.get_rect()

active_balls = 0
for i in range(4):
	balls[i] = Ball(i)
	active_balls += 1

Long = pygame.image.load("assets/long.png")
Med = pygame.image.load("assets/med.png")
Short = pygame.image.load("assets/short.png")

#block_data is (image, [coords], rotate)
level1_block_data = [(Long, [220, 200], 0),
					 (Med, [400, 280], 90), 
					 (Short, [1000,250], 0), 
					 (Med, [700,200], 0),
					 (Med, [900,400], 0)]
level1 = Level(level1_block_data)
active_level = level1

running = True

while running:
	screen.blit(bg, (0, 0))
	screen.blit(frame_shadow, (0, 0))

	for ball in balls:
		if ball != None:
			ball.acc = [0,0]

	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			running = False

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

	for block in active_level.blocks:
		screen.blit(block.image, (block.pos[0], block.pos[1]))

	for ball in balls:
		if ball != None:
			ball.motion_calc(dt)
			ball.frame_collision()
			ball.block_collision()
			#ball.ball_collision()
			screen.blit(ball.image, (ball.pos[0], ball.pos[1]))
	
	screen.blit(frame, (0, 0))

	pygame.display.update()