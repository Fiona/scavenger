import os
import pygame
from pygame.locals import *
import math

from locals import *

import program


class Process(object):

	def __init__(self, *args, **kargs):

		# Stuff to be referenced
		self.x = 0
		self.y = 0
		self.z = 0
		self.graph = None
		self.size = 100
		self.angle = 0
		self.flags = 0
		self.alpha = 255
		self.priority = 0
		self.region = 0
		self.father = None
		self.son = None
		self.smallbro = None
		self.bigbro = None
		self.special_flags = 0
		self.redraw_transform_graph = True
		self.rect = pygame.Rect(0, 0, 0, 0)

		self.ctype = C_SCREEN
		self.scroll_id = 0
		
		# Start program if we haven't
		if program.Program.running == False:
			program.Program.init_game()
		
		# add the processes
		self.id = program.Program.add_process(self)		   

		self.status = 0

		self.gen = self.begin(*args, **kargs)
		
		# Start off the process loop if we haven't
		if program.Program.running == False:
			program.Program.running = True
			program.Program.start_game()

	
	def begin(self):
		""" This is where the main code for the process sits """
		while True:
			yield
					 
	
	def loop(self):
		if program.Program.running == False:
			return
		try:
			self.gen.next()
		except StopIteration:
			self.signal(S_KILL)


	def draw(self):
		
		if self.graph == None:
			return
		
		self.graph_size = self.graph.get_size()
		
		self.transform_graph = self.get_real_surface()
		center = self.transform_graph.get_size()

		self.rect = pygame.Rect(self.x - (center[0]/2), self.y - (center[1]/2), center[0], center[1])
				
		if self.region == 0:
			program.Program.screen.set_clip(program.Program.screen_rect)
		else:
			program.Program.screen.set_clip(program.Program.regions[self.region])
		
		x, y = self.x, self.y 
		
		if self.ctype == C_SCROLL:
			if self.scroll_id in program.Program.scroll:
				x,y = self.calculate_scroll_draw_pos(x,y)
			else:
				return
		
		program.Program.screen.blit(self.transform_graph, self.get_draw_position(x, y), None, self.special_flags)

	def calculate_scroll_draw_pos(self, x, y):
		return (x-program.Program.scroll[self.scroll_id].x0,
				y-program.Program.scroll[self.scroll_id].y0)
	   
	def get_draw_position(self, x, y):
		center = self.transform_graph.get_size()
		return (x - (center[0]/2), y - (center[1]/2))
	
	
	def get_real_surface(self):
		""" Returns a real-world reprisentation of graphic including size and angle """
		
		if (self.size == 100 and self.angle == 0 and self.flags == 0 and self.alpha >= 255):
			return self.graph
		elif self.redraw_transform_graph == False:
			return self.transform_graph_cached

		graph_size = self.graph.get_size()		
		transform_graph = self.graph.copy()

		if self.size != 100:
			if self.size < 0: self.size = 0
			new_width = int(graph_size[0] * (self.size / 100.0))
			new_height = int(graph_size[1] * (self.size / 100.0))
			transform_graph = pygame.transform.scale(transform_graph, (new_width, new_height))
			
		if self.angle != 0:
			transform_graph = pygame.transform.rotate(transform_graph, self.angle / 1000)
			
		if self.flags != 0:
			transform_graph = pygame.transform.flip(transform_graph, (True if self.flags & B_HMIRROR else False), (True if self.flags & B_VMIRROR else False))

		self.special_flags = 0

		if self.flags & B_ABLEND:
			self.special_flags = BLEND_ADD
			
		if self.flags & B_TRANSLUCENT:
			transform_graph.set_alpha(int(round(255/2)))
		else:
			transform_graph.set_alpha(self.alpha)

		self.transform_graph_cached = transform_graph
		self.redraw_transform_graph = False
		
		return transform_graph
	

	def point_collision(self, point, box = False):
		""" 
		super fast collision check, will only check against a single point - a tuple of x,y
		Checks for collision against rectangle defined when "draw" is called - in other 
		words, checks for collision with position and orientation object was last drawn at 
		"""
		
		if self.rect.collidepoint(point):
			
			if box == True:
				return True

			point = (
					 point[0]-self.rect.left,
					 point[1]-self.rect.top
					 )
			"""
			TODO: this check could be avoided if self.rect was guaranteed to be 
			the same size as the surface. It appears to be a pixel out sometimes.
			"""
			surface = self.get_real_surface() 
			if point[0]<surface.get_width() and point[1]<surface.get_height():
				if self.get_real_surface().get_at(point) == (255, 0, 255, 255):
					return False				
				else:
					return True
			else:
				return False			
		else:
			return False
		
	
	def collision(self, other, box = False):
		""" Check for collision with other object.
			Will accept a process instance or an ID number to check against one,
			or a process type as a string to check for all of a specific type
			It return False if none found, or a reference to the object that was collided with."""
			  
		if type(other) == type(""):

			# TODO: Ouch. Maybe hash by process type name?
			for obj in program.Program.processes:
				if obj != self.id:
					if program.Program.processes[obj].__class__.__name__ == other:					
						check = self.single_object_collision(program.Program.processes[obj], box)
						if check != False:
							return check
				
			return False

		elif type(other) == type(1):
			
			other = program.Program.p(other)
			
			if other != None and other != self:
				return self.single_object_collision(other, box)
			else:
				return False
			
		else:
			if other != None and other != self:
				return self.single_object_collision(other, box)
			else:
				return False

		
	def single_object_collision(self, other, box):
		""" Copy paste saving function used for collision() """

		if other.graph == None:
			return False
		
		# First check for box collisions - fast and easy
		if self.rect.colliderect(other.rect):
			
			if box == True:
				return other
			
			# if we have box collisioning, we can try pixel-perfect
			mymask = pygame.mask.from_surface(self.get_real_surface())
			othermask = pygame.mask.from_surface(other.get_real_surface())
			
			mycenter = mymask.get_size()
			othercenter = othermask.get_size()
			 
			offset = (
					  (self.x - mycenter[0]/2) - (other.x - othercenter[0]/2),
					  (self.y - mycenter[1]/2) - (other.y - othercenter[1]/2)
					  )

			pixels = othermask.overlap_area(mymask, offset)

			return False if pixels == 0 else other
		
		else:
			return False
		
		
	def signal(self, signal_code, tree=False):
		""" Signal will let you kill the process or put it to sleep.
			The 'tree' parameter can be used to signal to a process and all its
			descendant processes (provided an unbroken tree exists)
		
			Signal types-
			S_KILL - Permanently removes the process
			S_SLEEP - Process will disappear and will stop executing code
			S_FREEZE - Process will stop executing code but will still appear
				and will still be able to be checked for collisions.
			S_WAKEUP - Wakes up or unfreezes the process """
		program.Program.signal(self, signal_code, tree)
		
		
	def let_me_alone(self):
		""" Worst Spanish translation ever. This will kill all processes 
			except for the one calling this. """
		import copy
		process_iter = copy.copy(program.Program.processes)
		
		for obj in process_iter:
			if program.Program.processes[obj] != self:
				program.Program.single_object_signal(program.Program.processes[obj], S_KILL)

		
	def out_region(self, region_id = None):
		""" Checks if the item is out of the region, region_id defaults to current region.
		Can be useful for checking if something is off-screen too. """
		region_id = self.region if region_id == None else self.region
		return False if self.rect.colliderect(program.Program.regions[region_id]) else True
			

	def advance(self, distance):
		""" Process will move forward x pixels, based on current angle """
		self.xadvance(self.angle, distance)


	def xadvance(self, angle, distance):
		""" Process will move along the defined angle x number of pixels """
		self.x += int(distance * math.cos(math.radians(angle/1000.0)))
		self.y -= int(distance * math.sin(math.radians(angle/1000.0)))
		
		
	def get_angle(self, process):
		""" Returns the angle between the current process and the one passed in """
		return -1 if not program.Program.exists(process) else program.Program.fget_angle(self.x, self.y, process.x, process.y)
	
	
	def get_dist(self, process):
		""" Returns the distance between two processes in pixels """
		return -1 if not program.Program.exists(process) else program.Program.fget_dist(self.x, self.y, process.x, process.y)
	
	
	def get_distx(self, process):
		""" Returns the distance along the x plane between two processes in pixels """
		return -1 if not program.Program.exists(process) else program.Program.fget_dist(self.x, 0, process.x, 0)

	
	def get_disty(self, process):
		""" Returns the distance along the y plane between two processes in pixels """
		return -1 if not program.Program.exists(process) else program.Program.fget_dist(0, self.y, 0, process.y)
	
		
	def __setattr__(self, name, value):
		if self.__dict__.has_key(name) and name in ['graph', 'size', 'angle', 'flags', 'alpha'] and self.__dict__[name] != value:
			self.redraw_transform_graph = True
			
		object.__setattr__(self, name, value)
		
		if name == "z": program.Program.z_order_dirty = True
		if name == "priority": program.Program.priority_order_dirty = True
		
	def on_exit(self):
		"""
		May be overidden by subclasses to perform cleanup operations. This method
		is called by Program when a process comes to an end - either by reaching
		the end of its 'begin' method or after being killed by a signal.
		"""
		pass

