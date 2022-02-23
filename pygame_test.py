import pygame, random
import numpy as np

pygame.init()

screen = pygame.display.set_mode((1280,720))
pygame.display.set_caption("Tilt Labyrinth")

bg = pygame.image.load("assets/bg.png")
frame_shadow = pygame.image.load("assets/frame_shadow.png")
frame = pygame.image.load("assets/frame.png")

ball_sprites = [pygame.image.load("assets/ball.png"), pygame.image.load("assets/ball_y.png"),
				pygame.image.load("assets/ball_g.png"), pygame.image.load("assets/ball_b.png")]

balls = [None, None, None, None]

friction = 0.95
dt = 0.001

class Ball:
	def __init__ (self):
		self.acc = [0, 0]
		self.vel = [0, 0]
		self.pos = [random.randint(110, 130), random.randint(140, 160)]
		self.damping = 500
		self.sprite = ball_sprites[active_balls]

	def motion_calc (self, dt):
		ball.vel[0] += self.acc[0]*dt/self.damping	#v = u + at
		ball.vel[1] += self.acc[1]*dt/self.damping

		ball.vel[0] = self.vel[0]*friction
		ball.vel[1] = self.vel[1]*friction

		ball.pos[0] += self.vel[0]*dt
		ball.pos[1] += self.vel[1]*dt

def hex_to_dec (hex):
	d = int(hex, 16)
	if d < 2147483648: #h80000000
		return d
	else:
		return d - 4294967296 #hFFFFFFFF+1

active_balls = 0
balls[0] = Ball()
active_balls = 1
balls[1] = Ball()
active_balls = 2

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
		balls[0].acc[0] = hex_to_dec("CCCCCCCC")
	if keys[pygame.K_s]:
		balls[0].acc[0] = hex_to_dec("33333333")
	if keys[pygame.K_d]:
		balls[0].acc[1] = hex_to_dec("33333333")
	if keys[pygame.K_a]:
		balls[0].acc[1] = hex_to_dec("CCCCCCCC")

	if keys[pygame.K_UP]:
		balls[1].acc[0] = hex_to_dec("CCCCCCCC")
	if keys[pygame.K_DOWN]:
		balls[1].acc[0] = hex_to_dec("33333333")
	if keys[pygame.K_RIGHT]:
		balls[1].acc[1] = hex_to_dec("33333333")
	if keys[pygame.K_LEFT]:
		balls[1].acc[1] = hex_to_dec("CCCCCCCC")

	for ball in balls:
		if ball != None:
			ball.motion_calc(dt)
			screen.blit(ball.sprite, (ball.pos[1], ball.pos[0]))
	
	screen.blit(frame, (0, 0))


	pygame.display.update()