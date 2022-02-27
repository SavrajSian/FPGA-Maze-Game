import pygame, random, math, time
import numpy as np

pygame.init()
score = 0
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

def show_score(): #may be unfinished
    score_font = pygame.font.Font(None, 30)
    score_surface = score_font.render("SCORE: " + str(score), True, (255, 0, 0))
    score_rect = score_surface.get_rect()


def hex_to_dec (hex):
	d = int(hex, 16)
	if d < 2147483648: #h80000000
		return d
	else:
		return d - 4294967296 #hFFFFFFFF+1

class Block:
	def __init__ (self, image, coords, rotate):
		self.image = pygame.transform.rotate(image, rotate)
		self.pos = coords
		self.rect = self.image.get_rect()


class Level:
	def __init__ (self, level_block_data):
		images = [tup[0] for i,tup in enumerate(level_block_data)]
		coords = [tup[1] for i,tup in enumerate(level_block_data)]
		rotate = [tup[2] for i,tup in enumerate(level_block_data)]
		self.blocks = []
		for i in range(len(coords)):
			self.blocks.append(Block(images[i], coords[i], rotate[i]))


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

col1 = (218, 165, 32)
x_circle2 = 1100
y_circle2 = 400
running = True

while running:
	screen.fill([255,255,255])
	screen.blit(frame, (0, 0))
	
	screen.blit(bg, (0, 0))
	screen.blit(frame_shadow, (0, 0))
	circle2 = pygame.draw.circle(screen, (col1), (int(x_circle2), int(y_circle2)), 40) # temp circle just for functionality. 
	
	if (circle2).colliderect(balls[0]):
		score += 10; # 10 points for winning. -> to display to fpga.

	if (circle2).colliderect(balls[1]):
		score += 10; # 10 points for winning. -> to display to fpga.
	
	font = pygame.font.Font(None, 40)
	text1 = font.render("Score 1: " + str(score), True, (0, 0, 0))
	screen.blit(text1, (1000,700))
	#pygame.display.flip()
	font = pygame.font.Font(None, 40)
	text2 = font.render("Score 2: " + str(score), True, (0, 0, 0))
	screen.blit(text2, (100,700))
	pygame.display.flip()
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
	
	

	pygame.display.update()