"""
Ludum Dares 16
"""

import os
import math
from random import randrange, sample

import pygame		
from pygame.locals import *
from fenix.locals import *
from fenix.program import Program
from fenix.process import Process

from consts import *
from media import Media
import math
#from tilemap import Tilemap
from particles import Particles
from mrf.mathutil import Vector2d
#from mrf.tileutil import tile_ray_cast


## -------------------------------------
## -------- MAIN GAME PROCESS ----------
## -------------------------------------
class Game(Process):

	media = None
	text_fps = None

	player = None
	wormhole = None
	particles = None
	debris = None
	hud = {'hold' : None, 'hull' : None, 'message' : None, 'invenbutton' : None}
	stars = []

	cam_speed = (0.00, 0.00)

	debris_types = {}

	paused_processes = []
	paused = False

	start_game = False

	landmarks = {
		'spacestation' : {
			'name' : "Space Station Tobias",
			'x' : (FIELD_WIDTH/3) * 2 ,
			'y' : 1500,
			'graphic' : 'spacestation'
			},
		'spacestation2' : {
			'name' : "Space Station Buffalo",
			'x' : 100,
			'y' : 5000,
			'graphic' : 'spacestation'
			},
		'cruiser' : {
			'name' : "Walnut Class Cruser",
			'x' : FIELD_WIDTH - 500,
			'y' : 7500,
			'graphic' : 'cruiser'
			}
		}

	def begin(self):

		self.start_game = False

		# SET UP
		Program.set_mode((800,600), True)
		Program.set_title("Scavenger (Ludum Dare 16 entry by Fiona)")
		Program.set_fps(30)

		self.media = Media()

		self.debris_types = {
			'junk' : {
				'name' : 'Junk',
				'weight' : 50,
				'worth' : 0,
				'special' : False
			},

			# TIER 1 DEBRIS
			'tier1' : {
				'uncharged_startonium' : {
					'name' : 'Uncharged Startonium',
					'weight' : 100,
					'worth' : 50,
					'special' : False,
					'graphic' :	0
					},
				'depleted_powercell' : {
					'name' : 'Depleted Powercell',
					'weight' : 125,
					'worth' : 65,
					'special' : False,
					'graphic' :	1			
					},
				'empty_container' : {
					'name' : 'Empty Container',
					'weight' : 150,
					'worth' : 80,
					'special' : False,
					'graphic' :	2
					},
				'broken_solarpanel' : {
					'name' : 'Broken Solarpanel',
					'weight' : 90,
					'worth' : 40,
					'special' : False,
					'graphic' :	3
					}
				},
			# TIER 2 DEBRIS
			'tier2' : {
				'gold' : {
					'name' : 'Gold!',
					'weight' : 200,
					'worth' : 150,
					'special' : False,
					'graphic' :	0
					},
				'guns' : {
					'name' : 'Guns. Lots of guns.',
					'weight' : 220,
					'worth' : 175,
					'special' : False,
					'graphic' :	1			
					},
				'cat_food' : {
					'name' : 'Space Kitty Food',
					'weight' : 250,
					'worth' : 200,
					'special' : False,
					'graphic' :	2
					},
				'beowulf' : {
					'name' : 'Beowulf Cluster',
					'weight' : 300,
					'worth' : 250,
					'special' : False,
					'graphic' :	3
					}
				},

			# TIER 3 DEBRIS
			'tier3' : {
				'powercell' : {
					'name' : 'Powercell',
					'weight' : 275,
					'worth' : 250,
					'special' : False,
					'graphic' :	0
					},
				'blackbox' : {
					'name' : 'Black Box',
					'weight' : 350,
					'worth' : 270,
					'special' : False,
					'graphic' :	1			
					},
				'medical' : {
					'name' : 'Medical Supplies',
					'weight' : 375,
					'worth' : 300,
					'special' : False,
					'graphic' :	2
					},
				'stasis' : {
					'name' : 'Occupied Stasis Pod',
					'weight' : 400,
					'worth' : 350,
					'special' : False,
					'graphic' :	3
					}
				},

			# TIER 4 DEBRIS
			'tier4' : {
				'nuke' : {
					'name' : 'Nuclear Device',
					'weight' : 510,
					'worth' : 400,
					'special' : False,
					'graphic' :	0
					},
				'startonium' : {
					'name' : 'Startonium',
					'weight' : 600,
					'worth' : 650,
					'special' : False,
					'graphic' :	1
					},
				'jumpdrive' : {
					'name' : 'Jump Drive',
					'weight' : 550,
					'worth' : 600,
					'special' : False,
					'graphic' :	2		
					},				
				'escape' : {
					'name' : 'Empty Escape Pod',
					'weight' : 650,
					'worth' : 700,
					'special' : False,
					'graphic' :	3
					}
				},

			# TIER 5 DEBRIS
			'tier5' : {
				'alien' : {
					'name' : 'Alien Artifact',
					'weight' : 1000,
					'worth' : 1500,
					'special' : False,
					'graphic' :	0
					},
				'singularity' : {
					'name' : 'Contained Singularity',
					'weight' : 1250,
					'worth' : 2000,
					'special' : False,
					'graphic' :	1			
					},
				'timemachine' : {
					'name' : 'Flux Capacitor',
					'weight' : 1300,
					'worth' : 3500,
					'special' : False,
					'graphic' :	2
					},
				'element' : {
					'name' : 'Undiscovered Element',
					'weight' : 1500,
					'worth' : 5000,
					'special' : False,
					'graphic' :	3
					}
				}			
		}
		

		# MOUSE
		pygame.mouse.set_visible(False)

		# start game
		self.setup_starfield()
		self.particles = Particles(self, Program.screen)
		
		Program.start_scroll(0, None, None, lock = SC_BACKHOR|SC_BACKVER|SC_FOREHOR|SC_FOREVER)
		self.wormhole = Wormhole(self)
		self.camera = Camera(self)
		Program.scroll[0].camera = self.camera

		self.debris = Debris_field(self)

		pygame.mixer.music.load(os.path.join("sounds", "ambient.ogg"))
		pygame.mixer.music.set_volume(1.0)
		pygame.mixer.music.play(-1)					

		Title_screen(self)
		
		while True:

			if Program.key(K_ESCAPE):
				Program.exit()
			
			yield


	def start(self):
		self.hud['hold'] = HUD_hold(self)
		self.hud['hull'] = HUD_hull(self)
		self.hud['message'] = HUD_message(self)
		self.hud['invenbutton'] = HUD_invenbutton(self)
		self.player = Player_ship(self)
		Program.mouse.graph = self.media.player_gfx['crosshair']
		self.start_game = True
		
		
	def setup_starfield(self):

		for a in xrange(STAR_AMOUNT):
			self.stars.append({
				'x' : float(randrange(0, 800)),
				'y' : float(randrange(0, 600)),
				'speed' : float(randrange(1, 6))
				})

			if self.stars[-1]['speed'] == 5:
				self.stars[-1]['colour'] = randrange(1, 10)
			else:
				b = (int(self.stars[-1]['speed']) * 200) / 4
				self.stars[-1]['colour'] = (b,b,b)


	def draw(self):

		for star in self.stars:

			if not self.paused:

				if math.fabs(self.cam_speed[0]) > 0.0 and star['speed'] > 0:
					star['x'] -= self.cam_speed[0] / (6-star['speed'])
				if math.fabs(self.cam_speed[1]) > 0.0 and star['speed'] > 0:
					star['y'] -= self.cam_speed[1] / (6-star['speed'])

				change = False
			
				while star['x'] < 0:
					change = True
					star['x'] += 800

				while star['x'] > 800:
					change = True
					star['x'] -= 800

				while star['y'] < 0:
					change = True
					star['y'] += 600

				while star['y'] >  600:
					change = True
					star['y'] -= 600

				if change:
					star['x'] = float(star['x'])
					star['y'] = float(star['y'])
				
					star['speed'] = float(randrange(1, 6))
					
					if star['speed'] == 5:
						star['colour'] = randrange(1, 10)
					else:
						b = (int(star['speed']) * 200) / 4
						star['colour'] = (b,b,b)

			if star['speed'] == 5:
				Program.map_put(Program.screen, self.media.gfx_debris_particles[star['colour']], star['x'], star['y'])
			else:
				Program.map_put_pixel(Program.screen, int(star['x']), int(star['y']), star['colour'])


	def pause(self, pauser):
		self.paused_processes = Program.processes_in_status(0)
		self.paused_processes.remove(self)
		self.paused_processes.remove(Program.mouse)
		self.paused_processes.remove(pauser)
		self.paused_processes.remove(self.particles)

		Program.signal(self.paused_processes, S_FREEZE)
		pygame.mixer.music.set_volume(0.2)

		self.paused = True

	def unpause(self):
		Program.signal(self.paused_processes, S_WAKEUP)
		pygame.mixer.music.set_volume(1.0)
		self.paused_processes = []
		self.paused = False


class Title_screen(Process):

	wait = 0
	phase = 0
	
	def begin(self, game):

		self.x = 400
		self.y = 100
		self.z = Z_TUTORIAL_TEXT
		self.graph = game.media.gfx_title
		self.alpha = 0
		
		while True:

			if self.phase == 0:

				if self.wait > 30 and self.alpha < 200:
					self.alpha += 2
				self.wait += 1

				if game.camera.y > -300:
					game.cam_speed = (0.0, -2.0)
				else:
					game.start()
					self.phase = 1

			if self.phase == 1:
				if self.alpha > 0:
					self.alpha -= 2
				if self.alpha <= 0:
					self.graph = game.media.gfx_tutorial_messages[1]
					self.phase = 2
					self.x = 200
					self.y = 150
					self.wait = 0
					
			if self.phase == 2:
				if self.wait > 200:
					self.alpha -= 2
					self.x += 1

					if self.alpha <= 0:
						self.signal(S_KILL)

				elif self.wait > 20:
					self.alpha += 2
					self.x += 1
					
				self.wait += 1

				if self.wait == 100:
					Tutorial_message2(game)
					
			yield

class Tutorial_message2(Process):			
	def begin(self, game):
		self.graph = game.media.gfx_tutorial_messages[2]
		self.x = 600
		self.y = 190
		self.z = Z_TUTORIAL_TEXT
		self.wait = 0
		self.alpha = 0

		while True:

			if self.wait > 200:
				self.alpha -= 2
				self.x -= 1

				if self.alpha <= 0:
					self.signal(S_KILL)

			else:
				self.alpha += 2
				self.x -= 1
					
			self.wait += 1
			
			if self.wait == 100:
				Tutorial_message3(game)
			
			yield


class Tutorial_message3(Process):			
	def begin(self, game):
		self.graph = game.media.gfx_tutorial_messages[3]
		self.x = 200
		self.y = 230
		self.z = Z_TUTORIAL_TEXT
		self.wait = 0
		self.alpha = 0

		while True:

			if self.wait > 200:
				self.alpha -= 2
				self.x += 1

				if self.alpha <= 0:
					Tutorial_message4(game)
					self.signal(S_KILL)

			else:
				self.alpha += 2
				self.x += 1
					
			self.wait += 1
			
			yield


class Tutorial_message4(Process):			
	def begin(self, game):
		self.graph = game.media.gfx_tutorial_messages[4]
		self.x = 600
		self.y = 190
		self.z = Z_TUTORIAL_TEXT
		self.wait = 0
		self.alpha = 0

		while True:

			if self.wait > 500:
				if self.wait > 700:
					self.alpha -= 2
					self.x -= 1

					if self.wait == 800:
						Tutorial_message5(game)
					
					if self.alpha <= 0:
						self.signal(S_KILL)

				else:
					self.alpha += 2
					self.x -= 1
					
			self.wait += 1
			
			yield


class Tutorial_message5(Process):			
	def begin(self, game):
		self.graph = game.media.gfx_tutorial_messages[5]
		self.x = 200
		self.y = 220
		self.z = Z_TUTORIAL_TEXT
		self.wait = 0
		self.alpha = 0

		while True:

			if self.wait > 200:
				self.alpha -= 2
				self.x += 1

				if self.alpha <= 0:
					Tutorial_message6(game)
					self.signal(S_KILL)

			else:
				self.alpha += 2
				self.x += 1
					
			self.wait += 1
			
			yield			

class Tutorial_message6(Process):			
	def begin(self, game):
		self.graph = game.media.gfx_tutorial_messages[6]
		self.x = 600
		self.y = 250
		self.z = Z_TUTORIAL_TEXT
		self.wait = 0
		self.alpha = 0

		while True:

			if self.wait > 200:
				self.alpha -= 2
				self.x -= 1

				if self.alpha <= 0:
					self.signal(S_KILL)

			else:
				self.alpha += 2
				self.x -= 1
					
			self.wait += 1
			
			yield			
			

class Physical_process(Process):
	pos = Vector2d(0.0, 0.0)
 
	velocity = Vector2d(0.0, 0.0)
	velocity_friction = 0.95
 
	accel = 0.0
 
	angle_velocity = 0
	angle_friction = 0.9
	angle_accel = 1000

	def get_x(self):
		return int(self.pos.i)
	def set_x(self, val):
		self.pos[0] = val
	x = property(get_x, set_x)
	
	def get_y(self):
		return int(self.pos.j)
	def set_y(self, val):
		self.pos[1] = val
	y = property(get_y, set_y)
	
	def init_physics(self):
		self.pos = Vector2d(0.0, 0.0)
		self.velocity = Vector2d(0.0, 0.0)

	def update_physics(self):
		self.update_angle()
		self.update_velocity()
		self.update_position()
 
	def update_velocity(self):
		if math.fabs(self.accel) > 0:
			self.velocity += Vector2d(dir = math.radians(-(self.angle)/1000), mag = self.accel)
		self.velocity *= self.velocity_friction
 
	def update_position(self):
		self.pos += self.velocity
 
	def update_angle(self):
		self.angle_velocity *= self.angle_friction
		self.angle += self.angle_velocity

	def bump(self, vec):
		self.velocity += vec
		

class Camera(Process):

	def begin(self, game):
		
		self.x = FIELD_WIDTH / 2
		self.y = 400

		game.cam_speed = (0.0,0.0)
		
		while True:

			if game.start_game:
				game.cam_speed = ((game.player.x - self.x) * 0.10, (game.player.y - self.y) * 0.05)

			self.x += game.cam_speed[0]
			self.y += game.cam_speed[1]

			yield


## -------------------------------------
## ----- PLAYER RELATED PROCESS --------
## -------------------------------------
class Player_ship(Physical_process):

	credits = 0
	
	hold = 0
	max_hold = 500
	hold_contents = {}

	hull = 100
	max_hull = 100
	docking = False
	undock = True
	dying = False

	hold_level = 0
	hull_level = 0
	tractor_level = 0
	engine_level = 0
	
	def begin(self, game):

		self.init_physics()

		self.graph = game.media.player_gfx['ship']
		self.ctype = C_SCROLL
		self.x = float(FIELD_WIDTH / 2)
		self.y = -350
		self.angle = -90000
		self.z = Z_PLAYER
		self.size = 0
		laser_reload = 0
		tractor_reload = 0
		tractor_sound = 10

		Hub_arrow(game)
		
		start_fly = False
		
		while True:
					
			if not self.docking:

				if not self.undock and self.hull > 0:

					self.accel = 0
					
					# MOVEMENT
					if Program.key(K_UP) or Program.key(K_w) or Program.key(K_COMMA):
						if not start_fly:
							game.media.sounds['startfly'].play()
							game.media.sounds['flyloop'].play(-1)

							start_fly = True

						self.accel = 0.3 + (self.engine_level * 0.1)
					else:
						game.media.sounds['flyloop'].fadeout(500)
						start_fly = False
						
					if Program.key(K_DOWN) or Program.key(K_s) or Program.key(K_o):
						self.accel = -0.2  - (self.engine_level * 0.1)
					if Program.key(K_LEFT) or Program.key(K_a):
						self.angle_velocity += 400
					if Program.key(K_RIGHT) or Program.key(K_d) or Program.key(K_e):
						self.angle_velocity -= 400

					if Program.key(K_1):
						self.hull = 5
					if Program.key_released(K_2):
						Mine(game)
					if Program.key_released(K_3):
						Turret(game)
						
					# LAZORS
					laser_reload += 1
				
					if Program.key(K_SPACE) and laser_reload >= 10:
						Player_laser(
							game,
							self.pos + Vector2d(dir = math.radians((-(self.angle/1000)) + 90), mag = -10)
							)
						Player_laser(
							game,
							self.pos + Vector2d(dir = math.radians((-(self.angle/1000)) + 90) , mag = 10)
							)

						game.media.sounds['laser'].play()

						laser_reload = 0

					# TRACTOR
					tractor_reload += 1
			
					if Program.mouse.left and not game.hud['invenbutton'].point_collision((Program.mouse.x, Program.mouse.y)):
						tractor_sound += 1
						if tractor_reload >= 5:
							Player_tractor(game)
							tractor_reload = 0

						if tractor_sound >= 15:
							game.media.sounds['tractor'].play()							
							tractor_sound = 0

						for p in game.debris.pieces:
							if p.graph != None and self.get_dist(p) < (120 + (game.player.tractor_level*25)):

								mouse_to = Program.fget_angle(self.x, self.y, Program.mouse.x +  Program.scroll[0].x0, Program.mouse.y +  Program.scroll[0].y0)
								process_to = Program.fget_angle(self.x, self.y, p.x, p.y)

								if math.fabs(Program.angle_difference(mouse_to, process_to)) < 10000:
									p.bump(Vector2d(dir =  math.radians(-p.get_angle(self) / 1000), mag = 0.2))

									if self.get_dist(p) < 40 and p.__class__.__name__ == "Debris_piece":
										if game.player.hold + p.info['weight'] <= game.player.max_hold:											
											p.absorb()
										else:
											game.hud['message'].message = "It wont fit in the hold! Sell your stuff or upgrade."


				# PHYSICS
				self.update_physics()

				# PARTICLE TRAILS
				if self.accel > 0:
					game.particles.add_pixel_particles(count = 1, x = self.x, y= self.y, angle_from = int((self.angle - 180000) - 25000),
													   angle_to = int((self.angle - 180000) + 25000), speed_from = 3, speed_to = 6,
													   particle_col = (255,255,128), life = (4 + self.engine_level * 2))
					game.particles.add_graph_particles(count = 1, x = self.x, y= self.y, angle_from = int((self.angle - 180000) - 25000),
													   angle_to = int((self.angle - 180000) + 25000), speed_from = 3, speed_to = 6,
													   particle_map = game.media.gfx_particles_trail, life = (4 + self.engine_level * 2))

			# dying
			if self.hull <= 0:
				if self.dying == False:
					counter = randrange(20, 30)
					game.media.sounds['explosion'].play()
					Explosion(game, self.x, self.y)
					self.dying = True
					
				counter -= 1

				if counter > 0:
					game.particles.add_pixel_particles(count = 2, x = self.x, y = self.y, angle_from = 0,
															angle_to = 360000, speed_from = 3, speed_to = 6,
															particle_col = (255, 255, 70), life = 10)
					self.angle_velocity += 400
				else:
					self.graph = None
					self.accel = 0.0
					self.angle_velocity = 0

				if counter < -20:
					mask = Program.new_map(Program.screen.get_width(), Program.screen.get_height())
					Program.map_clear(mask, (0,0,0))

					while counter > -27:
						yield
						Program.map_put(Program.screen, mask, 0, 0)
						counter -= 1
					
					self.graph = game.media.player_gfx['ship']
					self.x = float(FIELD_WIDTH / 2)
					self.y = -350
					self.angle = -90000
					self.z = Z_PLAYER
					self.size = 0
					laser_reload = 0
					tractor_reload = 0

					if self.credits > 0:
						self.credits = self.credits / 2
	
					self.hold = 0
					self.hold_contents = {}

					self.hull = self.max_hull
					self.docking = False
					self.undock = True
					self.dying = False

					game.camera.x, game.camera.y = self.x, self.y
					
			# leaving wormhole
			if self.undock:

				if self.size == 0:
					game.media.sounds['wormhole'].play()

				self.angle = -90000
				self.accel = 1.0

				if self.size < 100:
					self.size += 10

				if self.size > 100:
					self.size = 100

				if self.y > -100:
					self.undock = False
					self.docking = False
					
			# Being sucked into wormhole
			elif self.docking:
				if self.size > 0:
					self.size -= 10

				if self.size <=  0:
					HUD_hub(game)

			yield


class Player_laser(Process):
	def begin(self, game, pos):
		self.ctype = C_SCROLL
		self.x = pos[0]
		self.y = pos[1]
		self.angle = self.father.angle
		self.z = Z_PLAYER
		self.graph = game.media.player_gfx['laser']
		self.life = 0
		self.game = game
		
		while True:
			self.advance(20)
			self.life += 1

			if self.life == 25:
				self.signal(S_KILL)

			collide = self.collision("Debris_piece", box = True)

			if collide:
				collide.bump(Vector2d(dir =  math.radians(-self.angle / 1000), mag = 1))
				self.game.particles.add_pixel_particles(count = 5, x = self.x, y= self.y, angle_from = 0,
														angle_to = 360000, speed_from = 1, speed_to = 5,
														particle_col = (50, 255, 50), life = 10)
				self.signal(S_KILL)
			else:
				collide = self.collision("Landmark")
				if collide:
					self.game.particles.add_pixel_particles(count = 5, x = self.x, y= self.y, angle_from = 0,
															angle_to = 360000, speed_from = 1, speed_to = 5,
															particle_col = (50, 255, 50), life = 10)
					self.signal(S_KILL)
				
			yield
			

class Player_tractor(Process):
	def begin(self, game):
		self.ctype = C_SCROLL
		self.x = self.father.x
		self.y = self.father.y
		self.angle = Program.fget_angle(self.x, self.y, Program.mouse.x +  Program.scroll[0].x0, Program.mouse.y +  Program.scroll[0].y0)
		self.z = Z_PLAYER
		self.graph = game.media.player_gfx['tractor']
		self.size = 0
		
		while True:

			if self.size < 150:
				self.size += 10
				
			if self.alpha > 0:
				self.alpha -= (10 - (game.player.tractor_level*2))
				
			self.advance(5)

			if self.alpha <= 0:
				self.signal(S_KILL)

			yield


class Hub_arrow(Process):

	def begin(self, game):
		self.ctype = C_SCROLL
		self.graph = game.media.player_gfx['hub_arrow']
		self.z = Z_PLAYER - 1
		self.alpha = 0

		while True:

			if Program.mouse.right:
				counter += 1
			else:
				counter = 0 

			if counter > 10:
				if self.alpha < 255:
					self.alpha += 25
				self.x, self.y = self.father.x, self.father.y
				self.angle = Program.fget_angle(self.x, self.y, game.wormhole.x, game.wormhole.y)
				
			else:
				if self.alpha > 0:
					self.x, self.y = self.father.x, self.father.y
					self.alpha -= 25
					self.angle = Program.fget_angle(self.x, self.y, game.wormhole.x, game.wormhole.y)

			yield

class Wormhole(Process):

	def begin(self, game):
		self.ctype = C_SCROLL
		self.x = float(FIELD_WIDTH / 2)
		self.y = -350
		self.graph = game.media.player_gfx['wormhole']
		self.z = Z_PLAYER + 1
		#self.alpha = 220
		
		while True:

			if not game.start_game:
				game.particles.add_pixel_particles(count = 1, x = self.x, y= self.y, angle_from = 0,
														angle_to = 360000, speed_from = 4, speed_to = 6,
														particle_col = (255, 255, 255), life = 50)
				yield
				continue
			
			if self.get_dist(game.player) < 700:
				game.particles.add_pixel_particles(count = 1, x = self.x, y= self.y, angle_from = 0,
														angle_to = 360000, speed_from = 4, speed_to = 6,
														particle_col = (255, 255, 255), life = 50)

			if self.get_dist(game.player) < 200:
				game.player.bump(Vector2d(dir =  math.radians(-game.player.get_angle(self) / 1000), mag = 0.5))

			if self.get_dist(game.player) < 10 and not game.player.docking and not game.player.undock:
				game.player.docking = True
				
			yield
			
## -------------------------------------
## --------------- HUD -----------------
## -------------------------------------
class HUD_hold(Process):

	def begin(self, game):

		self.graph = game.media.gfx_hud['hold']
		self.x = 800 - 16
		self.y = 300
		self.z = Z_HUD

		self.meter = HUD_hold_meter(game)
		
		while True:

			yield


class HUD_hold_meter(Process):

	prev_hold = 0
	
	def begin(self, game):
		self.x = self.father.x
		self.y = self.father.y -8
		self.graph = Program.new_map(27, 575)
		Program.map_clear(self.graph, (0, 0, 0))

		self.prev_hold = game.player.hold
		self.prev_max_hold = game.player.max_hold
		self.z = self.father.z + 1
		
		while True:

			if self.prev_max_hold != game.player.max_hold:
				self.prev_hold = 1
				
			self.prev_max_hold = game.player.max_hold
			
			if self.prev_hold != game.player.hold:

				if self.prev_hold < game.player.hold:
					self.prev_hold += 1
				if self.prev_hold > game.player.hold:				
					self.prev_hold -= 1
					
				Program.map_clear(self.graph, (0, 0, 0))
				height = int(575 * self.prev_hold / game.player.max_hold)
				self.graph.fill((0, 150, 190), rect = ((0, 575 - height), (27, height)))
				
			yield


class HUD_hull(Process):

	def begin(self, game):

		self.graph = game.media.gfx_hud['hull']
		self.x = 16
		self.y = 300
		self.z = Z_HUD

		self.meter = HUD_hull_meter(game)
		
		while True:

			yield


class HUD_hull_meter(Process):

	prev_hull = 0
	
	def begin(self, game):
		self.x = self.father.x
		self.y = self.father.y -8
		self.graph = Program.new_map(27, 575)
		Program.map_clear(self.graph, (160, 45, 45))
		self.prev_hull == game.player.hull
		self.z = self.father.z + 1
		
		while True:

			if self.prev_hull != game.player.hull:

				if self.prev_hull < game.player.hull:
					self.prev_hull += 1
				if self.prev_hull > game.player.hull:
					self.prev_hull -= 1
				
				Program.map_clear(self.graph, (0, 0, 0))
				height = int(575 * self.prev_hull / game.player.max_hull)
				self.graph.fill((160, 45, 45), rect = ((0, 575 - height), (27, height)))
				
			yield


class HUD_invenbutton(Process):

	def begin(self, game):
		self.x = 700
		self.y = 12
		self.graph = game.media.gfx_hud['invenbutton'][0]
		self.z = Z_HUD

		while True:

			if self.point_collision((Program.mouse.x, Program.mouse.y)):
				self.graph = game.media.gfx_hud['invenbutton'][1]
				if Program.mouse.left_up:
					game.media.sounds['beep'].play()
					HUD_inventory(game)
			else:
				self.graph = game.media.gfx_hud['invenbutton'][0]
				
			yield

			

class HUD_message(Process):

	message = ""
	
	def begin(self, game):
		self.graph = Program.new_map(800, 20)
		Program.map_clear(self.graph, (10,10,10))
		self.x = 400
		self.y = 600 - 10
		self.z = Z_HUD + 1
		self.text = Program.write(game.media.fonts['vera'], 40, self.y - 9, text = "")
		text_counter = 0
		prev_message = ""
		
		while True:

			if self.message != prev_message:
				self.text.text = self.message
				prev_message = self.message
				text_counter = 200

			if text_counter <= 0:
				text_counter = 0
				self.message = ""
				prev_message = ""
				self.text.text = ""
			else:
				text_counter -= 1
				
			yield
			

class HUD_inventory(Process):
	
	def begin(self, game):
		self.x = 400
		self.y = 300
		self.z = Z_HUD - 1
		#self.text = Program.write(game.media.fonts['vera'], 40, self.y - 9, text = "")

		# create graphics
		self.graph = Program.map_clone(game.media.gfx_hud['inventory'])
		self.mask = Program.new_map(Program.screen.get_width(), Program.screen.get_height())
		self.mask.fill((128, 128, 128))
		self.mask.set_alpha(128)
		self.graph.set_alpha(50)

		# add contents to main graphic
		text_height = 135
		self.texts = []

		game.pause(self)
		
		if len(game.player.hold_contents):
			for tier in game.player.hold_contents:

				for item_type in game.player.hold_contents[tier]:
					if item_type == "junk":
						name = "Junk"
						g = game.media.gfx_debris_inventory
					else:
						name = game.debris_types[tier][item_type]['name']
						g = game.media.gfx_valuable_debris[tier][game.debris_types[tier][item_type]['graphic']]

					Program.map_block_copy(self.graph, 25, text_height - 110, g,
										   origin_x = 10, origin_y = 10, width = 20, height = 20, flags = 0)
					pygame.draw.rect(self.graph, (200,200,200), ((25, text_height - 110),(20,20)), 1)

					tx = Program.write(game.media.fonts['vera'], 300, text_height, alignment = ALIGN_CENTER_LEFT, text = str(game.player.hold_contents[tier][item_type]) + " x " + name)
					tx.z = -512
					self.texts.append(tx)
					text_height += 25

		tx = Program.write(game.media.fonts['mini_vera'], 325, 440, alignment = ALIGN_CENTER_LEFT, text = str(game.player.credits))
		tx.colour = (50,50,50)
		self.texts.append(tx)
		
		yield
		
		while True:

			if self.graph.get_alpha() < 255:
				self.graph.set_alpha(self.graph.get_alpha() + 50)
				
			if Program.mouse.left_up:
				for i in self.texts:
					Program.delete_text(i)
					
				game.unpause()
				game.media.sounds['beep'].play()				
				self.signal(S_KILL)
				
			yield

	def draw(self):
		Program.map_put(Program.screen, self.mask, 0, 0)
		Program.map_put(Program.screen, self.graph, 250, 100)


class HUD_hub(Process):

	mask = None
	
	texts = {}
	objects = []

	def begin(self, game, pause = True):
		self.x = 400
		self.y = 300
		self.z = Z_HUD - 1

		# create graphics
		self.graph = Program.map_clone(game.media.gfx_hud['hub'])
		self.mask = Program.new_map(Program.screen.get_width(), Program.screen.get_height())
		self.mask.fill((128, 128, 128))
		self.mask.set_alpha(128)
		self.graph.set_alpha(50)

		if pause:
			game.pause(self)

		self.texts['credits'] = Program.write(game.media.fonts['mini_vera'], 535, 111, alignment = ALIGN_CENTER_RIGHT, text = str(game.player.credits))

		# hud buttons
		self.objects.append(HUD_launch_button(game, 490, 430, game.media.gfx_hud['hub_launch']))
		
		self.objects.append(HUD_repair_button(game, 310, 140, game.media.gfx_hud['hub_repair']))
		cost = ("- -" if self.workout_repair_price(game) == 0 else self.workout_repair_price(game))
		self.texts['repair'] =  Program.write(game.media.fonts['mini_vera'], 535, 135, alignment = ALIGN_CENTER_RIGHT, text = str(cost))
		
		self.objects.append(HUD_upgrade_hull_button(game, 336, 166, game.media.gfx_hud['hub_upgradehull']))
		cost = ("Max Level" if self.workout_hull_upgrade_price(game) == -1 else self.workout_hull_upgrade_price(game))
		self.texts['upgrade_hull'] =  Program.write(game.media.fonts['mini_vera'], 535, 161, alignment = ALIGN_CENTER_RIGHT, text = str(cost))

		self.objects.append(HUD_upgrade_hold_button(game, 336, 192, game.media.gfx_hud['hub_upgradehold']))
		cost = ("Max Level" if self.workout_hold_upgrade_price(game) == -1 else self.workout_hold_upgrade_price(game))
		self.texts['upgrade_hold'] =  Program.write(game.media.fonts['mini_vera'], 535, 187, alignment = ALIGN_CENTER_RIGHT, text = str(cost))

		self.objects.append(HUD_upgrade_tractor_button(game, 345, 218, game.media.gfx_hud['hub_upgradetractor']))
		cost = ("Max Level" if self.workout_tractor_upgrade_price(game) == -1 else self.workout_tractor_upgrade_price(game))
		self.texts['upgrade_tractor'] =  Program.write(game.media.fonts['mini_vera'], 535, 213, alignment = ALIGN_CENTER_RIGHT, text = str(cost))

		self.objects.append(HUD_upgrade_engine_button(game, 345, 244, game.media.gfx_hud['hub_upgradeengine']))
		cost = ("Max Level" if self.workout_engine_upgrade_price(game) == -1 else self.workout_engine_upgrade_price(game))
		self.texts['upgrade_engine'] =  Program.write(game.media.fonts['mini_vera'], 535, 239, alignment = ALIGN_CENTER_RIGHT, text = str(cost))

		self.objects.append(HUD_sell_stuff_button(game, 310, 430, game.media.gfx_hud['hub_sellstuff']))

		while True:

			if self.graph.get_alpha() < 255:
				self.graph.set_alpha(self.graph.get_alpha() + 50)

			self.texts['credits'].text = game.player.credits
			
			yield


	def draw(self):
		if self.mask:
			Program.map_put(Program.screen, self.mask, 0, 0)
			Program.map_put(Program.screen, self.graph, 250, 100)


	def kill(self):
		for i in self.texts:
			Program.delete_text(self.texts[i])

		for i in self.objects:
			i.signal(S_KILL)

		self.signal(S_KILL)


	def workout_repair_price(self, game):
		if game.player.hull >= game.player.max_hull:
			return 0

		return (game.player.max_hull - game.player.hull) * 4


	def workout_hull_upgrade_price(self, game):
		if game.player.hull_level == MAX_HULL_LEVEL:
			return -1

		return (game.player.hull_level+1) * 800


	def workout_hold_upgrade_price(self, game):
		if game.player.hold_level == MAX_HOLD_LEVEL:
			return -1

		return (game.player.hold_level+1) * 500


	def workout_tractor_upgrade_price(self, game):
		if game.player.tractor_level == MAX_TRACTOR_LEVEL:
			return -1

		return (game.player.tractor_level+1) * 750


	def workout_engine_upgrade_price(self, game):
		if game.player.engine_level == MAX_ENGINE_LEVEL:
			return -1

		return (game.player.engine_level+1) * 400


class HUD_button(Process):

	def begin(self, game, x, y, graph):
		self.x = x
		self.y = y
		self.graph = graph[0]
		self.z = Z_HUD - 2
		self.game = game
		while True:

			if self.point_collision((Program.mouse.x, Program.mouse.y)):
				self.graph = graph[1]
				if Program.mouse.left_up:
					game.media.sounds['beep'].play()					
					self.action()
			else:
				self.graph = graph[0]
				
			yield

class HUD_launch_button(HUD_button):
	def action(self):
		self.game.unpause()
		self.game.player.undock = True
		self.game.player.docking = False
		self.game.player.x = float(FIELD_WIDTH / 2)
		self.game.player.y = -350
		
		self.father.kill()
		

class HUD_repair_button(HUD_button):
	def action(self):
		cost = self.father.workout_repair_price(self.game)
		if cost == 0:
			return
		
		if cost < self.game.player.credits:
			self.game.player.hull = self.game.player.max_hull
			self.game.player.credits -= cost
			self.father.texts['repair'].text = str("- -" if self.father.workout_repair_price(self.game) == 0 else self.father.workout_repair_price(self.game))

	
class HUD_upgrade_hull_button(HUD_button):
	def action(self):
		cost = self.father.workout_hull_upgrade_price(self.game)
		if cost == -1:
			return

		if cost < self.game.player.credits:
			self.game.media.sounds['moneyout'].play()								
			self.game.player.hull_level += 1
			self.game.player.max_hull += 100
			self.game.player.hull = self.game.player.max_hull
			self.game.player.credits -= cost
			self.father.texts['upgrade_hull'].text = ("Max Level" if self.father.workout_hull_upgrade_price(self.game) == -1 else self.father.workout_hull_upgrade_price(self.game))
			self.father.texts['repair'].text = "- -"
		

class HUD_upgrade_hold_button(HUD_button):
	def action(self):
		cost = self.father.workout_hold_upgrade_price(self.game)
		if cost == -1:
			return

		if cost < self.game.player.credits:
			self.game.media.sounds['moneyout'].play()								
			self.game.player.hold_level += 1
			self.game.player.max_hold += 500
			self.game.player.credits -= cost
			self.father.texts['upgrade_hold'].text = ("Max Level" if self.father.workout_hold_upgrade_price(self.game) == -1 else self.father.workout_hold_upgrade_price(self.game))


class HUD_upgrade_tractor_button(HUD_button):
	def action(self):
		cost = self.father.workout_tractor_upgrade_price(self.game)
		if cost == -1:
			return

		if cost < self.game.player.credits:
			self.game.media.sounds['moneyout'].play()								
			self.game.player.tractor_level += 1
			self.game.player.credits -= cost
			self.father.texts['upgrade_tractor'].text = ("Max Level" if self.father.workout_tractor_upgrade_price(self.game) == -1 else self.father.workout_tractor_upgrade_price(self.game))


class HUD_upgrade_engine_button(HUD_button):
	def action(self):
		cost = self.father.workout_engine_upgrade_price(self.game)
		if cost == -1:
			return

		if cost < self.game.player.credits:
			self.game.media.sounds['moneyout'].play()								
			self.game.player.engine_level += 1
			self.game.player.credits -= cost
			self.father.texts['upgrade_engine'].text = ("Max Level" if self.father.workout_engine_upgrade_price(self.game) == -1 else self.father.workout_engine_upgrade_price(self.game))


class HUD_sell_stuff_button(HUD_button):
	def action(self):
		self.father.kill()
		HUD_sell(self.game)
		

class HUD_sell(Process):

	mask = None
	texts = []
	total_payment = 0
	
	def begin(self, game):
		self.x = 400
		self.y = 300
		self.z = Z_HUD - 1
		self.game = game
		
		# create graphics
		self.redraw(game)
		self.mask = Program.new_map(Program.screen.get_width(), Program.screen.get_height())
		self.mask.fill((128, 128, 128))
		self.mask.set_alpha(128)

		# add contents to main graphic
		self.objects = []

		self.objects.append(HUD_sell_cancel_button(game, 500, 439, game.media.gfx_hud['hub_sell_cancel']))
		self.objects.append(HUD_sell_sell_button(game, 290, 439, game.media.gfx_hud['hub_sell_sell']))

		yield
		
		while True:
			yield

	def draw(self):
		if self.mask:
			Program.map_put(Program.screen, self.mask, 0, 0)
			Program.map_put(Program.screen, self.graph, 250, 100)

	def redraw(self, game):
		self.graph = Program.map_clone(game.media.gfx_hud['hub_sell'])
		
		for i in self.texts:
			Program.delete_text(i)

		text_height = 135
		self.texts = []

		self.total_payment = 0
		
		if len(game.player.hold_contents):
			for tier in game.player.hold_contents:

				for item_type in game.player.hold_contents[tier]:
					if item_type == "junk":
						name = "Junk"
						cost = ""
						g = game.media.gfx_debris_inventory
					else:
						name = game.debris_types[tier][item_type]['name']
						cost = " (" + str(game.debris_types[tier][item_type]['worth'] * game.player.hold_contents[tier][item_type]) + ")"
						g = game.media.gfx_valuable_debris[tier][game.debris_types[tier][item_type]['graphic']]
						self.total_payment += game.debris_types[tier][item_type]['worth'] * game.player.hold_contents[tier][item_type]
						
					Program.map_block_copy(self.graph, 25, text_height - 110, g,
										   origin_x = 10, origin_y = 10, width = 20, height = 20, flags = 0)
					pygame.draw.rect(self.graph, (200,200,200), ((25, text_height - 110),(20,20)), 1)

					tx = Program.write(game.media.fonts['vera'], 300, text_height, alignment = ALIGN_CENTER_LEFT, text = str(game.player.hold_contents[tier][item_type]) + " x " + name + cost)
					tx.z = -512
					self.texts.append(tx)
					text_height += 25

			tx = Program.write(game.media.fonts['mini_vera'], 400, 438, alignment = ALIGN_CENTER, text = "Total :" + str(self.total_payment))
			tx.colour = (0,0,0)
			self.texts.append(tx)


class HUD_sell_cancel_button(HUD_button):
	def action(self):
		for i in self.father.texts:
			Program.delete_text(i)

		for i in self.father.objects:
			i.signal(S_KILL)

		self.father.signal(S_KILL)
		HUD_hub(self.game, pause = False)




class HUD_sell_sell_button(HUD_button):
	def action(self):
		if self.father.total_payment > 0:
			self.game.media.sounds['moneyout'].play()								
		self.game.player.hold_contents = {}
		self.game.player.hold = 0
		self.game.player.credits += self.father.total_payment
		self.father.redraw(self.game)
		
## -------------------------------------
## ----- DEBRIS RELATED PROCESS --------
## -------------------------------------
class Debris_field(Process):

	pieces = []
	
	def begin(self, game):

		# boring old pieces
		for a in xrange(FIELD_DENSITY):
			self.pieces.append(
				Debris_piece(game)
				)

		# Valuable pieces
		for debris_type in game.debris_types['tier1']:
			for x in xrange(3):
				self.pieces.append(
					Debris_piece(game, debris_type, 'tier1', 1000, 2500)
					)

		for debris_type in game.debris_types['tier2']:
			for x in xrange(3):
				self.pieces.append(
					Debris_piece(game, debris_type, 'tier2', 2500, 3000)
					)

		for debris_type in game.debris_types['tier3']:
			for x in xrange(3):
				self.pieces.append(
					Debris_piece(game, debris_type, 'tier3', 3000, 6000)
					)
				
		for debris_type in game.debris_types['tier4']:
			for x in xrange(4):
				self.pieces.append(
					Debris_piece(game, debris_type, 'tier4', 6000, 9000)
					)
				
		for debris_type in game.debris_types['tier5']:
			self.pieces.append(
				Debris_piece(game, debris_type, 'tier5', 9000, 10000)
				)

		for x in xrange(20):
			self.pieces.append(
				Mine(game, 6000, 9000)
				)

		for x in xrange(1, 5):
			self.pieces.append(
				Turret(game, (FIELD_WIDTH / 4) * x, 8900, 9100)
				)

		for lm in game.landmarks:
			self.pieces.append(
				Landmark(game, lm, game.landmarks[lm]['graphic'], game.landmarks[lm]['name'], game.landmarks[lm]['x'], game.landmarks[lm]['y'])
				)
			
		while True:

			yield


class Debris_piece(Physical_process):

	indicator = None
	indicator_count = 0
	name = ""
	absorbing = False
	debris_type = ""

	info = {}
	
	def begin(self, game, debris_type = "junk", tier = "", threshold_start = 0, threshold_end = FIELD_HEIGHT):
		self.init_physics()
		
		self.debris_type = debris_type
		self.x = randrange(0, FIELD_WIDTH)
		self.y = randrange(threshold_start, threshold_end)
		self.angle = randrange(0, 360000)
		self.tier = tier
		self.thresholds = (threshold_start, threshold_end)
		
		if debris_type == "junk":
			self.info = game.debris_types['junk']
		else:
			self.info = game.debris_types[tier][debris_type]
		
		self.name = self.info['name']

		if debris_type == 'junk':
			self.my_graph = sample(game.media.gfx_debris, 1)[0]
		else:
			self.my_graph = game.media.gfx_valuable_debris[tier][self.info['graphic']]

		self.ctype = C_SCROLL

		self.angle_velocity = randrange(-500, 500)
		
		sound_count = 6
		
		while True:

			if self.x > (game.camera.x - 500) and self.x < (game.camera.x + 500) \
				   and self.y > (game.camera.y - 400) and self.y < (game.camera.y + 400):
				self.graph = self.my_graph
			else:
				self.graph = None

			if game.start_game == False:
				yield
				continue

			if self.absorbing == False:

				sound_count += 1
				
				if self.graph and self.get_dist(game.player) < 40:
					if self.collision(game.player, box = True):

						p_get_angle = math.radians(-self.get_angle(game.player) / 1000)
						s_get_angle = math.radians(-game.player.get_angle(self) / 1000)

						mag = (1 if game.player.velocity.get_mag() < 1 else game.player.velocity.get_mag())

						game.player.bump(Vector2d(dir = p_get_angle, mag = (0.75 * mag)))
						self.bump(Vector2d(dir = s_get_angle, mag = (0.75 * mag)))
						game.player.hull -= 1

						if sound_count > 5:
							game.media.sounds['collision'].play()
							sound_count = 0
														
						game.player.pos += Vector2d(dir = p_get_angle, mag = (0.01  * mag))
						self.pos += Vector2d(dir = s_get_angle, mag = (0.01  * mag))

						game.particles.add_pixel_particles(count = 10, x = self.x, y= self.y, angle_from = 0,
														   angle_to = 360000, speed_from = 1, speed_to = 5,
														   particle_col = (128,128,128), life = 10)

				if self.graph:
					self.angle += self.angle_velocity

				if self.velocity.get_mag() > 0.1:
					self.velocity *= self.velocity_friction
					self.pos += self.velocity

				if self.graph != None and self.point_collision((Program.mouse.x + Program.scroll[0].x0, Program.mouse.y  + Program.scroll[0].y0), True):
					self.indicator_count += 1
					if self.indicator_count == 5 and self.indicator == None:
						self.indicator = Indicator(game, self.name)
				else:
					self.indicator_count = 0
					if self.indicator != None:
						self.indicator.signal(S_KILL)
						self.indicator = None

				if self.indicator != None:
					pygame.draw.rect(
						Program.screen,
						(125, 50, 125, 150),
						(
						(self.rect.left  - Program.scroll[0].x0, self.rect.top - Program.scroll[0].y0),
						(self.rect.width, self.rect.height)
						),
						1
					)
			

			else:

				if self.size == 100:
					game.media.sounds['pickup'].play()
					
				self.size -= 10
				self.alpha -= 25

				if self.size <= 0:
					
					game.player.hold += self.info['weight']

					if not self.tier in game.player.hold_contents:
						game.player.hold_contents[self.tier] = {}

					if self.debris_type in game.player.hold_contents[self.tier]:
						game.player.hold_contents[self.tier][self.debris_type] += 1
					else:
						game.player.hold_contents[self.tier][self.debris_type] = 1
						
					game.hud['message'].message = "Picked up " + self.name + "."

					if not self.info['special']:
						self.recreate_self(game)
					game.debris.pieces.remove(self)

					if self.indicator != None:
						self.indicator.signal(S_KILL)
					
					self.signal(S_KILL)
				
			yield


	def absorb(self):
		self.absorbing = True
		
	def recreate_self(self, game):		
		new_d = Debris_piece(game, self.debris_type, self.tier, self.thresholds[0], self.thresholds[1])
		found = True
		while found:
			new_d.x = randrange(0, FIELD_WIDTH)
			new_d.y = randrange(self.thresholds[0], self.thresholds[1])

			if new_d.x > game.camera.x - 500 and new_d.x < game.camera.x + 400 and \
			   new_d.y > game.camera.y - 400 and new_d.y < game.camera.y + 400:
				found = True
			else:
				found = False

		game.debris.pieces.append(new_d)


class Landmark(Physical_process):

	indicator = None
	
	def begin(self, game, lm, graphic, name, x, y):

		self.init_physics()
		self.x, self.y, self.name = x, y, name
		self.type = lm
		self.ctype = C_SCROLL

		self.angle_velocity = 50
		self.angle = randrange(0, 360000)

		self.my_graph = game.media.gfx_landmarks[graphic]
		self.z = Z_PLAYER + 1

		sound_count = 5
		
		while True:

			if self.x > (game.camera.x - 1000) and self.x < (game.camera.x + 1000) \
				   and self.y > (game.camera.y - 800) and self.y < (game.camera.y + 800):
				self.graph = self.my_graph
			else:
				self.graph = None

			if game.start_game == False:
				yield
				continue

			if self.graph and self.get_dist(game.player) < 500 and self.collision(game.player):

				p_get_angle = math.radians(-self.get_angle(game.player) / 1000)

				mag = (1 if game.player.velocity.get_mag() < 1 else game.player.velocity.get_mag())

				game.player.bump(Vector2d(dir = p_get_angle, mag = (0.75 * mag)))
				game.player.hull -= 2

				if sound_count > 5:
					game.media.sounds['collision'].play()
					sound_count = 0
														
				game.player.pos += Vector2d(dir = p_get_angle, mag = (0.01  * mag))

				game.particles.add_pixel_particles(count = 10, x = game.player.x, y= game.player.y, angle_from = 0,
												   angle_to = 360000, speed_from = 1, speed_to = 5,
												   particle_col = (128,128,128), life = 15)

			sound_count += 1
				

			if self.graph:
				self.angle += self.angle_velocity

			if self.graph != None and self.point_collision((Program.mouse.x + Program.scroll[0].x0, Program.mouse.y  + Program.scroll[0].y0), True):
				self.indicator_count += 1
				if self.indicator_count == 5 and self.indicator == None:
					self.indicator = Indicator(game, self.name)
			else:
				self.indicator_count = 0
				if self.indicator != None:
					self.indicator.signal(S_KILL)
					self.indicator = None

			if self.indicator != None:
				pygame.draw.rect(
					Program.screen,
					(125, 50, 125, 150),
					(
					(self.rect.left  - Program.scroll[0].x0, self.rect.top - Program.scroll[0].y0),
					(self.rect.width, self.rect.height)
					),
					1
				)
				
			yield
			

class Indicator(Process):

	def begin(self, game, name):

		self.z = Z_HUD
		
		text_g = game.media.fonts['system'].render(str(name), True, (255, 255, 255))
		
		self.graph = Program.new_map(text_g.get_width() + 20, text_g.get_height() + 6)
		Program.map_clear(self.graph, (125, 50, 125))

		Program.map_put(self.graph, game.media.player_gfx['indicator'][0], 0, 0)
		Program.map_put(self.graph, game.media.player_gfx['indicator'][1], text_g.get_width() + 16, 0)
		Program.map_put(self.graph, game.media.player_gfx['indicator'][2], 0, text_g.get_height() + 2)
		Program.map_put(self.graph, game.media.player_gfx['indicator'][3], text_g.get_width() + 16, text_g.get_height() + 2)

		Program.map_put(self.graph, text_g, 10, 3)

		self.alpha = 150

		self.size = 0
		
		while True:

			self.x = (self.father.x - Program.scroll[0].x0)
			self.y = (self.father.y - Program.scroll[0].y0) - 30

			if self.size < 100:
				self.size += 25
				
			yield



class Explosion(Process):

	def begin(self, game, x, y, follow = True):
		self.x, self.y = x, y
		iterations = randrange(15,30)
		curr = 0
	
		while True:

			if follow:
				self.x, self.y = self.father.x, self.father.y

			for a in xrange(randrange(2, 5)):
				Explosion_bit(game, self.x + randrange(-20, 20), self.y + randrange(-20, 20))

			curr += 1
			if curr == iterations:
				self.signal(S_KILL)
				
			yield

class Explosion_bit(Process):

	def begin(self, game, x, y):
		self.ctype = C_SCROLL
		self.z = Z_PLAYER - 1
		self.x, self.y = x, y
		self.graph = game.media.gfx_exp
		self.size = randrange(100, 200)

		while True:

			if self.size > 0:
				self.size -= 10
			else:
				self.signal(S_KILL)

			yield
				


class Mine(Physical_process):

	indicator = None
	
	def begin(self, game, threshold_start = 0, threshold_end = FIELD_HEIGHT):
		self.init_physics()

		self.x = randrange(0, FIELD_WIDTH)
		self.y = randrange(threshold_start, threshold_end)
		self.angle = randrange(0, 360000)
		self.thresholds = (threshold_start, threshold_end)
		
		self.name = "Mine"

		self.my_graph = game.media.gfx_mine

		self.ctype = C_SCROLL

		self.angle_velocity = randrange(-500, 500)
		
		while True:

			if not game.start_game:
				yield
				continue
			
			if self.x > (game.camera.x - 500) and self.x < (game.camera.x + 500) \
				   and self.y > (game.camera.y - 400) and self.y < (game.camera.y + 400):
				self.graph = self.my_graph
			else:
				self.graph = None

			if self.get_dist(game.player) < 80:
				Explosion(game, self.x+20, self.y+20, follow = False)
				Explosion(game, self.x-20, self.y-20, follow = False)
				Explosion(game, self.x+20, self.y-20, follow = False)
				Explosion(game, self.x-20, self.y+20, follow = False)
				p_get_angle = math.radians(-self.get_angle(game.player) / 1000)
				game.player.bump(Vector2d(dir = p_get_angle, mag = 30.0))
				game.player.hull -= 75
				game.media.sounds['explosion'].play()					

				for p in game.debris.pieces:
					if self.get_dist(p) < 200:
						p_get_angle = math.radians(-self.get_angle(p) / 1000)
						p.bump(Vector2d(dir = p_get_angle, mag = 20.0))

				if self.indicator != None:
					self.indicator.signal(S_KILL)
				
				self.recreate_self(game)
				self. signal(S_KILL)

			self.angle += self.angle_velocity

			if self.velocity.get_mag() > 0.1:
				self.velocity *= self.velocity_friction
				self.pos += self.velocity

			if self.graph != None and self.point_collision((Program.mouse.x + Program.scroll[0].x0, Program.mouse.y  + Program.scroll[0].y0), True):
				self.indicator_count += 1
				if self.indicator_count == 5 and self.indicator == None:
					self.indicator = Indicator(game, self.name)
			else:
				self.indicator_count = 0
				if self.indicator != None:
					self.indicator.signal(S_KILL)
					self.indicator = None

			if self.indicator != None:
				pygame.draw.rect(
					Program.screen,
					(125, 50, 125, 150),
					(
					(self.rect.left  - Program.scroll[0].x0, self.rect.top - Program.scroll[0].y0),
					(self.rect.width, self.rect.height)
					),
					1
				)			

			yield
			

	def recreate_self(self, game):		
		new_d = Mine(game, self.thresholds[0], self.thresholds[1])
		found = True
		while found:
			new_d.x = randrange(0, FIELD_WIDTH)
			new_d.y = randrange(self.thresholds[0], self.thresholds[1])

			if new_d.x > game.camera.x - 500 and new_d.x < game.camera.x + 400 and \
			   new_d.y > game.camera.y - 400 and new_d.y < game.camera.y + 400:
				found = True
			else:
				found = False

		game.debris.pieces.append(new_d)


class Turret(Physical_process):

	indicator = None
	
	def begin(self, game, x, threshold_start = 0, threshold_end = FIELD_HEIGHT):
		self.init_physics()

		self.x = x
		self.y = randrange(threshold_start, threshold_end)
		self.angle = randrange(0, 360000)
		self.thresholds = (threshold_start, threshold_end)
		
		self.name = "Turret"

		self.my_graph = game.media.gfx_turret

		self.ctype = C_SCROLL

		_reload = 0

		while True:

			if not game.start_game:
				yield
				continue

			if self.x > (game.camera.x - 500) and self.x < (game.camera.x + 500) \
				   and self.y > (game.camera.y - 400) and self.y < (game.camera.y + 400):
				self.graph = self.my_graph
			else:
				self.graph = None
				
			self.angle = Program.near_angle(self.angle, self.get_angle(game.player), 10000)

			if self.graph and self.get_dist(game.player) < 40:
				if self.collision(game.player, box = True):

					p_get_angle = math.radians(-self.get_angle(game.player) / 1000)
					s_get_angle = math.radians(-game.player.get_angle(self) / 1000)

					mag = (1 if game.player.velocity.get_mag() < 1 else game.player.velocity.get_mag())

					game.player.bump(Vector2d(dir = p_get_angle, mag = (0.75 * mag)))
					self.bump(Vector2d(dir = s_get_angle, mag = (0.75 * mag)))
					game.player.hull -= 1
						
					game.player.pos += Vector2d(dir = p_get_angle, mag = (0.01  * mag))
					self.pos += Vector2d(dir = s_get_angle, mag = (0.01  * mag))
					
					game.particles.add_pixel_particles(count = 10, x = self.x, y= self.y, angle_from = 0,
														   angle_to = 360000, speed_from = 1, speed_to = 5,
														   particle_col = (128,128,128), life = 10)

			if self.graph and self.get_dist(game.player) < 400:
				if _reload > 10:
					game.media.sounds['laser'].play()					
					Turret_laser(game, (self.x, self.y))
					_reload = 0

			_reload += 1
				
			if self.velocity.get_mag() > 0.1:
				self.velocity *= self.velocity_friction
				self.pos += self.velocity

			if self.graph != None and self.point_collision((Program.mouse.x + Program.scroll[0].x0, Program.mouse.y  + Program.scroll[0].y0), True):
				self.indicator_count += 1
				if self.indicator_count == 5 and self.indicator == None:
					self.indicator = Indicator(game, self.name)
			else:
				self.indicator_count = 0
				if self.indicator != None:
					self.indicator.signal(S_KILL)
					self.indicator = None

			if self.indicator != None:
				pygame.draw.rect(
					Program.screen,
					(125, 50, 125, 150),
					(
					(self.rect.left  - Program.scroll[0].x0, self.rect.top - Program.scroll[0].y0),
					(self.rect.width, self.rect.height)
					),			
					1
				)			

			yield


class Turret_laser(Process):
	def begin(self, game, pos):
		self.ctype = C_SCROLL
		self.x = pos[0]
		self.y = pos[1]
		self.angle = self.father.angle
		self.z = Z_PLAYER
		self.graph = game.media.gfx_turret_laser
		self.life = 0
		self.game = game
		
		while True:
			self.advance(20)
			self.life += 1

			if self.life == 25:
				self.signal(S_KILL)

			collide = self.collision(game.player, box = True)

			if collide:
				collide.bump(Vector2d(dir =  math.radians(-self.angle / 1000), mag = 1))
				self.game.particles.add_pixel_particles(count = 5, x = self.x, y= self.y, angle_from = 0,
														angle_to = 360000, speed_from = 1, speed_to = 5,
														particle_col = (255, 50, 50), life = 10)
				game.player.hull -= 50
				self.signal(S_KILL)
				
			yield
		
if __name__ == '__main__':
	Game()

