"""
Ludum Dare 16

Particle system
"""

from fenix.program import Program
from fenix.process import Process
from fenix.locals import *
		
from random import randrange
import math
from copy import copy 
from consts import *

			
class Particles(Process):
	
	draw_layer = None
	persist_layer = None
	particles = []
	game = None
	
	def begin(self, game, draw_layer):
		self.game = game
		self.draw_layer = draw_layer
		self.priority = 200
		self.z = Z_PARTICLES

		while True:
			yield
			
	def draw(self):
		if len(self.particles) > 0:
			for x in copy(self.particles):
				x.update_and_draw(self.draw_layer, self.game)
		
	def add_pixel_particles(self, count = 10, x = 0, y = 0, angle_from = 0,
					  angle_to = 360000, speed_from = 3, speed_to = 4,
					  particle_col = (0,0,0), life = 10):
		
		for c in range(count):
			new_p = self.add_particle(x, y, speed_from, speed_to, angle_from, angle_to, life)
			new_p.particle_col = particle_col
			
		
	def add_graph_particles(self, count = 10, x = 0, y = 0, angle_from = 0,
					  angle_to = 360000, speed_from = 3, speed_to = 4,
					  particle_map = None,
					  life = 10, size_from = 75, size_to = 150, spin_speed = 0):

		for c in range(count):
			new_p = self.add_particle(x, y, speed_from, speed_to, angle_from, angle_to, life)
			if len(particle_map) == 1:
				new_p.graph = particle_map[0]
			else:
				new_p.graph = particle_map[randrange(0, len(particle_map)-1)]
				
			new_p.size = randrange(size_from, size_to) if size_from <> size_to else size_from
			new_p.spin, new_p.spin_angle = spin_speed, new_p.angle

		
	def add_particle(self, x, y, speed_from, speed_to, angle_from, angle_to,  life):
		new_p = Particle()
		self.particles.append(new_p)
		
		new_p.x, new_p.y = x, y	 
		new_p.speed = randrange(speed_from, speed_to)
		new_p.angle = randrange(angle_from, angle_to)
					
		new_p.life = life+randrange(0,5)
		new_p.handler = self
		
		return new_p
		

class Particle():
	
	graph = None
	particle_col = (0,0,0)
	speed = 10
	x = 0
	y = 0
	angle = 0
	size = 100
	life = 10
	spin = 0
	spin_angle = 0
	
	life_count = 0
	
	handler = None
	
	def update_and_draw(self, draw_layer, game):

		if not game.paused:
			self.x += int(self.speed * math.cos(math.radians(self.angle/1000.0)))
			self.y -= int(self.speed * math.sin(math.radians(self.angle/1000.0)))

		draw_x = self.x - Program.scroll[0].x0
		draw_y = self.y - Program.scroll[0].y0
		
		if self.graph != None:

			if not game.paused:
				if self.spin > 0:
					self.spin_angle += self.spin
				else:
					self.spin_angle = self.angle
				self.size -= 7
			Program.map_xput(draw_layer, self.graph, draw_x, draw_y, self.spin_angle, self.size)
		else:
			Program.map_put_pixel(draw_layer, draw_x, draw_y, self.particle_col)
				
		if not game.paused:
			self.speed *= 0.99
		
			self.life_count += 1
			if self.graph == None and (self.life_count > self.life or self.speed < 1):
				self.handler.particles.remove(self)
			elif self.graph != None and self.size <= 0:
				self.handler.particles.remove(self)
			
				
