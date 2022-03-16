
	def ball_collision (self):
		for ball in balls:
			if ball != None:
				if ball.ID != self.ID:
					np_self = np.asarray(self.get_centre())
					np_ball = np.asarray(ball.get_centre())
					line_of_impact = np_self - np_ball
					distance = np.linalg.norm(line_of_impact) #vector magnitude
					if distance < 42:	#2 radii
						# p_self = pygame.math.Vector2(self.get_centre()[0], self.get_centre()[1]) #Temporary Pygame vectors used for the reflect function
						# p_ball = pygame.math.Vector2(ball.get_centre()[0], ball.get_centre()[1])
						# normal_vector = p_ball - p_self
						# v_self = pygame.math.Vector2(self.vel[0], self.vel[1]) #Temporary Pygame vectors used for the reflect function
						# v_ball = pygame.math.Vector2(ball.vel[0], ball.vel[1])
						# refl_v_self = pygame.math.Vector2(v_self[0], v_self[1]).reflect(normal_vector)
						# self.vel[0], self.vel[1] = refl_v_self.x, refl_v_self.y
						# self.vel[0], ball.vel[1] = -refl_v_self.x, -refl_v_self.y
						# refl_v_ball = pygame.math.Vector2(v_ball[0], v_ball[1]).reflect(-normal_vector)
						# ball.vel[0], ball.vel[1] = refl_v_ball.x, refl_v_ball.y

						cos_alpha = np.dot(line_of_impact, np.array([1, 0]))/	\
									(np.linalg.norm(line_of_impact)*np.linalg.norm(np.array([1, 0]))) #cosine similarity between line and +1 vector
						alpha = np.arccos(np.clip(cos_alpha, -1, 1)) #vector angle
						if np_self[1] > np_ball[1]:
							alpha = -alpha		#0→-π
						ball_impact_vel = np.linalg.norm(np.asarray(ball.vel)) #Swap velocities on relevant component (new axis)
						self_vel = np.linalg.norm(np.asarray(self.vel)) #preserved momentum on irrelevant axis
						if self.vel != [0.0, 0.0]:
							cos_theta_a = np.dot(self.vel, np.array([1, 0]))/	\
										(np.linalg.norm(self.vel)*np.linalg.norm(np.array([1, 0]))) #cosine similarity between self velocity and +1 vector
						else: cos_theta_a = 0
						theta_a = np.arccos(np.clip(cos_theta_a, -1, 1)) #vector angle
						if self.vel[1] > 0:
							theta_a = -theta_a		#0→-π
						psi = alpha - theta_a 	#angle between relevant impact component and velocity (measures self obliqueness)
						if ball.vel != [0.0, 0.0]:
							cos_theta_b = np.dot(ball.vel, np.array([1, 0]))/	\
										(np.linalg.norm(ball.vel)*np.linalg.norm(np.array([1, 0]))) #cosine similarity between ball velocity and +1 vector
						else: cos_theta_b = 0
						theta_b = np.arccos(np.clip(cos_theta_b, -1, 1)) #vector angle
						if ball.vel[1] > 0:
							theta_b = -theta_b		#0→-π
						phi = alpha - theta_b 	#angle between relevant impact component and velocity (measures ball obliqueness)
						impact_velocity_rel = ball_impact_vel*np.cos(phi)	#projection of velocity onto axis
						velocity_irrel = self_vel*np.sin(psi)
						final_vel = np.linalg.norm([velocity_irrel, impact_velocity_rel])
						#print(np.arccos(np.clip(np.dot(np.asarray([velocity_irrel, impact_velocity_rel]), np.array([1, 0]))/(np.linalg.norm(np.asarray([velocity_irrel, impact_velocity_rel]))*np.linalg.norm(np.array([1, 0]))), -1, 1)))###########
						self.pos[0] = self.pos[0] + (41-distance)*np.cos(alpha) if self.pos[0] < ball.pos[0] else self.pos[0] - (41-distance)*np.cos(alpha) #position yourself outside other ball
						self.pos[1] = self.pos[1] + (41-distance)*np.sin(alpha) if self.pos[1] < ball.pos[1] else self.pos[1] - (41-distance)*np.sin(alpha)
						self.vel[0] = final_vel*np.cos(alpha) if self.pos[0] < ball.pos[0] else final_vel*np.cos(-alpha) #return velocity to global x, y components
						self.vel[1] = final_vel*np.sin(alpha) if self.pos[1] < ball.pos[1] else final_vel*np.sin(-alpha)
