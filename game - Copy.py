import pygame, pygame.gfxdraw
import math, time, random
import numpy as np

pygame.init()

screen = pygame.display.set_mode((1280,720))
pygame.display.set_caption(" ")#################

vignette = pygame.image.load("assets/vignette.png")
hole_image = pygame.image.load("assets/hole.png")
goal_glow_image = pygame.image.load("assets/goal_glow.png").convert_alpha()
goal_white_image = pygame.image.load("assets/goal_white.png").convert_alpha()
ball_images = [pygame.image.load("assets/ball.png").convert_alpha(), pygame.image.load("assets/ball_y.png").convert_alpha(),
				pygame.image.load("assets/ball_g.png").convert_alpha(), pygame.image.load("assets/ball_b.png").convert_alpha()]
ball_colours = [(230, 230, 230), (255, 255, 170), (170, 255, 170), (170, 220, 255)]
ball_scores = [0,0,0,0]
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
		self.colour = ball_colours[ID]
		self.image = ball_images[ID].copy()
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
			if abs(self.vel[0]) > 1000:
				active_particle_systems.append(ParticleSystem(particle_no=random.randint(1,3), colour=self.colour, lifetime=0.5, radius=10, size=3, coords=[self.pos[0], self.pos[1] + self.rect.center[1]]))
		if self.get_centre()[0] + self.rect.center[0] > 1200:	#right hitbox
			self.pos[0] = 1156
			self.vel[0] = -self.vel[0]*restitution
			if abs(self.vel[0]) > 1000:
				active_particle_systems.append(ParticleSystem(particle_no=random.randint(1,3), colour=self.colour, lifetime=0.5, radius=10, size=3, coords=[self.pos[0] + self.rect.right, self.pos[1] + self.rect.center[1]]))
		if self.get_centre()[1] - self.rect.center[1] < 72:		#up hitbox
			self.pos[1] = 72
			self.vel[1] = -self.vel[1]*restitution
			if abs(self.vel[1]) > 1000:
				active_particle_systems.append(ParticleSystem(particle_no=random.randint(1,3), colour=self.colour, lifetime=0.5, radius=10, size=3, coords=[self.pos[0] +  self.rect.center[0], self.pos[1]]))
		if self.get_centre()[1] + self.rect.center[1] > 645:	#down hitbox
			self.pos[1] = 601
			self.vel[1] = -self.vel[1]*restitution
			if abs(self.vel[1]) > 1000:
				active_particle_systems.append(ParticleSystem(particle_no=random.randint(1,3), colour=self.colour, lifetime=0.5, radius=10, size=3, coords=[self.pos[0] +  self.rect.center[0], self.pos[1] + self.rect.bottom]))

	def block_collision (self):
		for block in active_level.blocks:
			#left hitbox
			if (self.get_centre()[0] + self.halfsize > block.rect.left - 1) and\
			   (self.get_centre()[0] - self.halfsize < block.rect.left + 20) and\
			   (self.get_centre()[1] + self.halfsize > block.rect.top + 15) and\
			   (self.get_centre()[1] - self.halfsize < block.rect.bottom - 15):
				self.pos[0] = block.rect.left - self.size - 3
				self.vel[0] = -self.vel[0]*restitution
				if abs(self.vel[0]) > 1000:
					active_particle_systems.append(ParticleSystem(particle_no=random.randint(1,3), colour=self.colour, lifetime=0.5, radius=10, size=3, coords=[self.pos[0] + self.rect.right, self.pos[1] + self.rect.center[1]]))
			#right hitbox
			if (self.get_centre()[0] + self.halfsize > block.rect.right - 20) and\
			   (self.get_centre()[0] - self.halfsize < block.rect.right) and\
			   (self.get_centre()[1] + self.halfsize > block.rect.top + 15) and\
			   (self.get_centre()[1] - self.halfsize < block.rect.bottom - 20):
				self.pos[0] = block.rect.right - 2
				self.vel[0] = -self.vel[0]*restitution
				if abs(self.vel[0]) > 1000:
					active_particle_systems.append(ParticleSystem(particle_no=random.randint(1,3), colour=self.colour, lifetime=0.5, radius=10, size=3, coords=[self.pos[0], self.pos[1] + self.rect.center[1]]))
			#up hitbox
			if (self.get_centre()[0] + self.halfsize > block.rect.left + 10) and\
			   (self.get_centre()[0] - self.halfsize < block.rect.right - 5) and\
			   (self.get_centre()[1] + self.halfsize > block.rect.top) and\
			   (self.get_centre()[1] - self.halfsize < block.rect.top + 20):
				self.pos[1] = block.rect.top - self.size - 2
				self.vel[1] = -self.vel[1]*restitution
				if abs(self.vel[1]) > 1000:
					active_particle_systems.append(ParticleSystem(particle_no=random.randint(1,3), colour=self.colour, lifetime=0.5, radius=10, size=3, coords=[self.pos[0] +  self.rect.center[0], self.pos[1] + self.rect.bottom]))
			#down hitbox
			if (self.get_centre()[0] + self.halfsize > block.rect.left + 10) and\
			   (self.get_centre()[0] - self.halfsize < block.rect.right - 5) and\
			   (self.get_centre()[1] + self.halfsize > block.rect.bottom - 20) and\
			   (self.get_centre()[1] - self.halfsize < block.rect.bottom):
				self.pos[1] = block.rect.bottom - 2
				self.vel[1] = -self.vel[1]*restitution
				if abs(self.vel[1]) > 1000:
					active_particle_systems.append(ParticleSystem(particle_no=random.randint(1,3), colour=self.colour, lifetime=0.5, radius=10, size=3, coords=[self.pos[0] +  self.rect.center[0], self.pos[1]]))

	def hole_collision (self):
		global active_level
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
				if self.scaler > 0.9:
					self.brightness -= 15
					if type(hole) == Goal:
						self.image.fill((255, 255, 255, self.brightness), None, pygame.BLEND_RGBA_MULT)
						self.image.fill((255-self.brightness, 255-self.brightness, 255-self.brightness, 255), None, pygame.BLEND_RGB_ADD)
					else:
						self.image.fill((self.brightness, self.brightness, self.brightness, 255), None, pygame.BLEND_RGBA_MULT)
				else:
					self.image.fill((255, 255, 255, 0), None, pygame.BLEND_RGBA_MULT) #hide ball during timeout
				if self.scaler < 0.8:
					if type(hole) == Goal:
						active_particle_systems.append(ParticleSystem(particle_no=50, colour=self.colour, lifetime=2, radius=400, coords=[hole.pos[0]+hole.rect.center[0], hole.pos[1]+hole.rect.center[1]]))
				if self.scaler < 0.7:
					if type(hole) == Goal:
						ball_scores[self.ID] +=10
						print (self.ID, ball_scores[self.ID])
						if active_level != level5:
							self.__init__(self.ID) #respawn ball
						active_level = update_level(active_level)
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
		pygame.draw.rect(screen, active_level.edge_colour, pygame.Rect(10, 0, 83, 720))
		pygame.draw.rect(screen, active_level.edge_colour, pygame.Rect(1190, 0, 80, 720))
		pygame.draw.rect(screen, active_level.edge_colour, pygame.Rect(0, 10, 1280, 74))
		pygame.draw.rect(screen, active_level.edge_colour, pygame.Rect(0, 635, 1280, 80))
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

class ParticleSystem ():
	def __init__(self, particle_no, colour, lifetime, radius, coords, type="burst", angle=0, size=5):
		self.particles = []
		for i in range(particle_no):
			self.particles.append(Particle(colour, lifetime, radius, coords, angle, size))

class Particle ():
	def __init__(self, colour, lifetime, radius, coords, angle, size):
		self.randomlifetime = random.uniform(lifetime*0.8, lifetime*1.2)
		self.colour = colour
		self.size = size
		self.pos = [coords[0], coords[1]]
		self.magnitude = random.randint(25, 100) * radius
		self.angle = random.uniform(0, 2*math.pi)
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

def draw_parallax (object):
	scale_factorX = (640 - object.rect.center[0]) / 100
	scale_factorY = (360 - object.rect.center[1]) / 100
	scaled = [object.pos[0] + scale_factorX,
			  object.pos[1] + scale_factorY,
			  object.rect.right - object.pos[0] + scale_factorX,
			  object.rect.bottom - object.pos[1] + scale_factorY]
	pygame.draw.rect(screen, active_level.edge_colour, pygame.Rect(scaled[0], scaled[1], scaled[2], scaled[3]))

level1_blocks = [(300, 50, 60, 320),
				(750, 300, 60, 380)]
level1_holes = [(1020, 450), #first hole is always the goal
				(500, 100),
                (600, 500),
                (1000, 200)]
level1_colour = (190,25,90) #Magenta
level1_bg_colour = (120,15,70)
level1_edge_colour = (100,10,60)
level1_goal_colour = (255, 110, 160, 255) #RGBA
level1 = Level(level1_blocks, level1_holes, level1_colour, level1_bg_colour, level1_edge_colour, level1_goal_colour)

level2_blocks = [(400, 50, 60, 300),
				(600, 300, 60, 380),
				(1100, 200, 300, 60)]
level2_holes = [(1020, 450), #first hole is always the goal
				(100, 250),
                (200, 500),
                (800, 300),
                (1000, 400),
                (1100, 350)]
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
level3_colour = (41, 204, 73) #Light green
level3_bg_colour = (44, 153, 66) #Dark green
level3_edge_colour = (27, 112, 44)
level3_goal_colour = (200, 255, 200, 255) #RGBA
level3 = Level(level3_blocks, level3_holes, level3_colour, level3_bg_colour, level3_edge_colour, level3_goal_colour)

level4_blocks = [(80, 580, 350, 80),
				(300, 50, 60, 350),
				(600, 220, 60, 480)]
level4_holes = [(1020, 450), #first hole is always the goal
				(250, 475),
                (475, 500),
                (700, 200),
                (975, 200),
                (1075, 200),
                (1100, 400),
                (950, 550)]
level4_colour = (222, 139, 91) #Light orange
level4_bg_colour = (191, 87, 27) #Dark orange
level4_edge_colour = (172, 75, 19)
level4_goal_colour = (255, 230, 200, 255) #RGBA
level4 = Level(level4_blocks, level4_holes, level4_colour, level4_bg_colour, level4_edge_colour, level4_goal_colour)

level5_blocks = [(300, 50, 60, 120),
				(200, 300, 60, 400),
				(500, 50, 60, 320),
                (500, 550, 60, 100),
                (800, 550, 60, 100),
                (900, 300, 340, 60)]
level5_holes = [(1020, 450), #first hole is always the goal
				(400, 200),
                (350, 350),
                (450, 400),
                (350, 550),
                (650, 550),
                (675, 150),
                (975, 150)]
level5_colour = (89, 164, 222) #Light blue
level5_bg_colour = (13, 110, 184 ) #Dark blue
level5_edge_colour = (13, 77, 181)
level5_goal_colour = (200, 230, 255, 255) #RGBA
level5 = Level(level5_blocks, level5_holes, level5_colour, level5_bg_colour, level5_edge_colour, level5_goal_colour)

active_level = level1

def update_level(curr_level):
	if curr_level == level1:
		return  level2
	elif curr_level == level2:
		return level3
	elif curr_level == level3:
		return level4
	elif curr_level == level4:
		return level5 
	elif curr_level == level5:
		pygame.quit()


active_balls = 0
for i in range(4):
	balls[i] = Ball(i)
	active_balls += 1

active_particle_systems = []
def which_level (level_in):
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

print(pygame.font.get_fonts())
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
	
	screen.blit(vignette, (0, 0))

	for hole in active_level.holes:
		screen.blit(hole.image, (hole.pos[0], hole.pos[1]))
	goal_centre = [active_level.holes[0].pos[0] + 60, active_level.holes[0].pos[1] + 60]
	screen.blit(active_level.holes[0].white, (goal_centre[0], goal_centre[1]))

	for ball in balls:
		if ball != None:
			ball.acc = [0,0]

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

	for system in active_particle_systems:
		for particle in system.particles:
			particle.motion(dt)
			particle.lifetime(system.particles)
			if len(system.particles) == 0:
				active_particle_systems.remove(system)
			pygame.draw.rect(screen, particle.colour, (particle.pos[0], particle.pos[1], particle.size, particle.size))
	
	font = pygame.font.Font(None, 80)
	what_level = which_level(active_level)
	text1 = font.render("Level ", True, (0, 0, 0))
	screen.blit(text1, (500,15))

	pygame.display.update()
