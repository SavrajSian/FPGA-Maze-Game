import pygame
import numpy as np

pygame.init()

screen = pygame.display.set_mode((1280,720))
pygame.display.set_caption("Tilt Labyrinth")

bg = pygame.image.load("assets/bg.png")
frame_shadow = pygame.image.load("assets/frame_shadow.png")
frame = pygame.image.load("assets/frame.png")
ball = pygame.image.load("assets/ball.png")

ball_acc = [0, 0]
ball_vel = [0, 0]
ball_pos = [120, 150]

damping = 200
friction = 0.95

def hex_to_dec (hex):
	d = int(hex, 16)
	if d < 2147483648: #80000000
		return d
	else:
		return d - 4294967296

def motion_calc (dt):
	ball_vel[0] += ball_acc[0]*dt/damping
	ball_vel[1] += ball_acc[1]*dt/damping
	ball_vel[0] = ball_vel[0]*friction
	ball_vel[1] = ball_vel[1]*friction
	ball_pos[0] += ball_vel[0]*dt
	ball_pos[1] += ball_vel[1]*dt
	print(ball_acc, ball_vel, ball_pos)


prev_get_ticks = pygame.time.get_ticks()

running = True

while running:
	screen.blit(bg, (0, 0))
	screen.blit(frame_shadow, (0, 0))

	ball_acc = [0,0]

	dt = (pygame.time.get_ticks() - prev_get_ticks) / 1000
	prev_get_ticks = pygame.time.get_ticks()

	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			running = False
	
	keys = pygame.key.get_pressed()
	if keys[pygame.K_w]:
		ball_acc[0] = hex_to_dec("CCCCCCCC")
	if keys[pygame.K_s]:
		ball_acc[0] = hex_to_dec("33333333")
	if keys[pygame.K_w] and keys[pygame.K_s]:
		ball_acc[0] = 0
	if keys[pygame.K_d]:
		ball_acc[1] = hex_to_dec("33333333")
	if keys[pygame.K_a]:
		ball_acc[1] = hex_to_dec("CCCCCCCC")
	if keys[pygame.K_d] and keys[pygame.K_a]:
		ball_acc[1] = 0

	dt = pygame.time.Clock().tick(30)
	print(dt)
	motion_calc(dt*100)
	screen.blit(ball, (ball_pos[1], ball_pos[0]))
	screen.blit(frame, (0, 0))


	pygame.display.update()