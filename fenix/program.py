import pygame
from pygame.locals import *
from locals import *
import math

import process
from process import Process

def is_iterable(x):
	try:
		iter(x)
		return True
	except TypeError:
		return False

class Mouse(process.Process):
	""" Record for holding mouse info """
	def __setattr__(self, name, value):
		""" Checks if we're setting visibility """
		process.Process.__setattr__(self,name,value)	
		if name == "visible":
			pygame.mouse.set_visible(value)
			

class Text(process.Process):
	""" this is the class for all text handling """
	def __init__(self, font, x, y, alignment, text):
		process.Process.__init__(self)
		self.font = font
		self.x = x
		self.y = y
		self.z = -512
		self.alignment = alignment
		self.text = text
		self.font = font
		self.antialias = True
		self.colour = (255,255,255)
		self.status = 0
		
	def loop(self):
		s = self.font.render(str(self.text), self.antialias, self.colour)
		self.graph = s

	
	def get_draw_position(self, draw_x, draw_y):   
		s = self.transform_graph
		if self.alignment == ALIGN_TOP:
			draw_x -= (s.get_width()/2)
		elif self.alignment == ALIGN_TOP_RIGHT:
			draw_x -= s.get_width()
		elif self.alignment == ALIGN_CENTER_LEFT:
			draw_y -= (s.get_height()/2)
		elif self.alignment == ALIGN_CENTER:
			draw_x -= (s.get_width()/2)
			draw_y -= (s.get_height()/2)
		elif self.alignment == ALIGN_CENTER_RIGHT:
			draw_y -= (s.get_height()/2)
			draw_x -= s.get_width()
		elif self.alignment == ALIGN_BOTTOM_LEFT:
			draw_y -= s.get_height()
		elif self.alignment == ALIGN_BOTTOM:
			draw_x -= (s.get_width()/2)
			draw_y -= s.get_height()
		elif self.alignment == ALIGN_BOTTOM_RIGHT:	   
			draw_y -= s.get_height()
			draw_x -= s.get_width()
		
		return draw_x, draw_y
	
	
class Scroll:
	""" Global class for scrolling backgrounds """
	
	""" The X-coordinate of the main graphic """
	x0 = 0
	""" The Y-coordinate of the main graphic """
	y0 = 0
	""" The X-coordinate of the background graphic """
	x1 = 0
	""" The Y-coordinate of the background graphic """
	y1 = 0
	""" Z order that the scroll will be drawn in """
	z = 512
	""" Region of the scroll, defaults to screen """
	region = 0
	""" Process to be followed """
	camera = None
	""" Graphic that will be scrolled """
	graph = None
	""" Graphic of background that will appear behind """
	background = None
	""" Bit flag saying if the scroll window is scrolled cyclically """
	lock = 0

	ratio = 50
	
	status = 0
	
	def __init__(self, graph, background, region, lock):
		self.graph = graph
		self.background = background
		self.region = region
		self.lock = lock	

		if self.graph != None:
			self.rect = self.graph.get_rect()
		else:
			self.rect = Program.screen_rect
			
		if self.background != None:
			self.back_rect = self.background.get_rect()
		else:
			self.back_rect = Program.screen_rect


	def draw(self):
		
		if self.camera and Program.exists(self.camera):
			self.x0 = self.camera.x-(Program.screen_rect.width/2)
			self.x1 = self.x0
			self.y0 = self.camera.y-(Program.screen_rect.height/2)
			self.y1 = self.y0

		self.sort_out_coords()
		
		if self.region == 0:
			Program.screen.set_clip(Program.screen_rect)
		else:
			Program.screen.set_clip(Program.regions[self.region])
		
		if self.background != None:
			if self.lock & SC_BACKHOR or self.lock & SC_BACKVER:
				tile_x = ((((self.x0 * self.ratio) / 100) / self.back_rect.width) * self.back_rect.width)
				tile_x -= (self.x0 * self.ratio) / 100
				
				tile_y = ((((self.y0 * self.ratio) /100) / self.back_rect.height) * self.back_rect.height)
				tile_y -= (self.y0 * self.ratio) / 100
				
				draw_x, draw_y = tile_x, tile_y
				
				while draw_x < Program.screen_rect.width:
					draw_y = tile_y
					while draw_y < Program.screen_rect.height:
						Program.screen.blit(self.background, (draw_x, draw_y))
						draw_y += self.back_rect.height
					draw_x += self.back_rect.width

			else:
				Program.screen.blit(self.background, (-(self.x0 * self.ratio) / 100, -(self.y0* self.ratio) / 100))

						
		if self.graph != None:
			if self.lock & SC_FOREHOR or self.lock & SC_FOREVER:
				tile_x = ((self.x0 / self.rect.width) * self.rect.width) - self.x0
				tile_y = ((self.y0 / self.rect.height) * self.rect.height) - self.y0
			
				draw_x, draw_y = tile_x, tile_y
				
				while draw_x < Program.screen_rect.width:
					draw_y = tile_y
					while draw_y < Program.screen_rect.height:
						Program.screen.blit(self.graph, (draw_x, draw_y))
						draw_y += self.rect.height
					draw_x += self.rect.width
					 
			else:
				Program.screen.blit(self.graph, (-self.x0, -self.y0))
	
	
	def sort_out_coords(self):
		
		if not self.lock & SC_FOREHOR:
			if self.x0 <= 0 or Program.screen_rect.width > self.rect.width: 
				self.x0	 = 0
			elif self.x0 + Program.screen_rect.width > self.rect.width:
				self.x0 = self.rect.width - Program.screen_rect.width
				
		if not self.lock & SC_FOREVER:
			if self.y0 <= 0 or Program.screen_rect.height > self.rect.height: 
				self.y0	 = 0
			elif self.y0 + Program.screen_rect.height > self.rect.height:
				self.y0 = self.rect.height - Program.screen_rect.height	  
					
		if not self.lock & SC_BACKHOR:
			if self.x1 <= 0 or Program.screen_rect.width > self.back_rect.width: 
				self.x1	 = 0
			elif self.x1 + Program.screen_rect.width > self.back_rect.width:
				self.x1 = self.back_rect.width - Program.screen_rect.width
				
		if not self.lock & SC_BACKVER:
			if self.y1 <= 0 or Program.screen_rect.height > self.back_rect.height: 
				self.y1	 = 0
			elif self.y1 + Program.screen_rect.height > self.back_rect.height:
				self.y1 = self.back_rect.height - Program.screen_rect.height   
			
			
	def __setattr__(self, name, value):
		self.__dict__[name] = value	   
		if name == "graph" and self.graph != None: self.rect = self.graph.get_rect()
		if name == "background" and self.background != None: self.back_rect = self.background.get_rect()

	def on_exit(self):
		pass

import time			

class Program:	 
	""" Main program class. call init_game before doing anything,
	then start_game to make all the processes start looping """
	
	running = False
	clock = None
	current_fps = 30
	fps = 0
	
	processes = {}
	processes_z = []
	z_order_dirty = False
	processes_priority = []
	priority_order_dirty = False
	num_ids = 0
	current_process_running = None
	regions = {}
	scroll = {}
	
	screen = None
	screen_rect = None
	bg_colour = (0, 0, 0)
	
	colorkey = (255, 0, 255)
	
	event_store = []
	keys_pressed  = []
	last_keys_pressed = []
	mouse_buttons_pressed = [False, False, False]
	last_mouse_buttons_pressed = [False, False, False]
	
	mouse = None
		   
	@classmethod	
	def init_game(cls):
		""" Initialises Pygame and starts up lots of other shizzle """
		pygame.mixer.pre_init(22050, -16, 8, 1024)
		pygame.init()
		pygame.mouse.set_visible(True)
		pygame.key.set_repeat(10, 0)
		
		cls.clock = pygame.time.Clock()
   
		cls.keys_pressed  = pygame.key.get_pressed()
		

	@classmethod			
	def start_game(cls):
		""" Deals with everything that happens every frame """

		cls.mouse = Mouse()
		cls.mouse.z = -512
		cls.mouse.visible = True		
		cls.mouse.pos = (0, 0)
		cls.mouse.left = False
		cls.mouse.middle = False
		cls.mouse.right = False
		cls.mouse.left_up = False
		cls.mouse.middle_up = False
		cls.mouse.right_up = False
		cls.mouse.wheelup = False
		cls.mouse.wheeldown = False	   
				   
		while cls.running:
			
			cls.poll_events()
			
			
			#################
			# Draw everything
			#################			 
			if cls.screen != None:
				cls.screen.fill(cls.bg_colour)
				
			if cls.z_order_dirty == True:
				cls.processes_z.sort(
									  reverse=True,
									  key=lambda object:
										object.z if hasattr(object, "z") else 0
									)
				cls.z_order_dirty = False
			
			# Do graphics
			for obj in cls.processes_z:
				if obj.status != S_SLEEP:
					obj.draw()
			
			
			#################
			# Logic everything
			#################
			if cls.priority_order_dirty == True:
				cls.processes_priority.sort(
											 reverse=True,
											 key=lambda object:
												object.priority if hasattr(object, "priority") else 0
											)
				cls.priority_order_dirty = False
			
			for obj in cls.processes_priority:
				if obj.status == 0 and hasattr(obj, "loop"):
					cls.current_process_running = obj
					obj.loop()

			# FPS handle
			cls.fps = int(cls.clock.get_fps())
			timerunning = cls.clock.tick(cls.current_fps)
			pygame.display.flip()
		

	@classmethod
	def add_process(cls, object, is_process = True):
		""" Adds a process to internal dictionaries """
		
		cls.num_ids = cls.num_ids + 1;
		cls.processes[cls.num_ids] = object
		cls.processes_z.append(object)
		cls.processes_priority.append(object)

		object.id = cls.num_ids
		
		cls.z_order_dirty = True
		
		if is_process == True:
			
			cls.priority_order_dirty = True
			
			# Handle relationships
			if cls.current_process_running != None:
				object.father = cls.current_process_running
				
				if not object.father.son == None:
					object.father.son.smallbro = object
					
				object.bigbro = object.father.son
				object.father.son = object

		return cls.num_ids


	@classmethod
	def kill_process(cls, process_id):
		""" Removes a process """
		ref = cls.p(process_id)

		if ref == None:
			return
		
		del cls.processes[process_id]

		cls.processes_z.remove(ref)
		cls.processes_priority.remove(ref)

		ref.on_exit()

		del(ref)
		
		cls.z_order_dirty = True
		cls.priority_order_dirty = True


	@classmethod
	def poll_events(cls):
		""" Go through all events and log them """

		cls.last_keys_pressed  = cls.keys_pressed
		
		pygame.event.pump()
		cls.keys_pressed  = pygame.key.get_pressed()
		
		cls.mouse.pos = pygame.mouse.get_pos()
		cls.mouse.x = cls.mouse.pos[0]
		cls.mouse.y = cls.mouse.pos[1]

		cls.mouse.wheelup = False
		cls.mouse.wheeldown = False
		
		cls.event_store = []
		
		for event in pygame.event.get():
			cls.event_store.append(event)
			if event.type == MOUSEBUTTONDOWN:
				if event.button == 4:
					cls.mouse.wheelup = True
				if event.button == 5:
					cls.mouse.wheeldown = True
					
		cls.last_mouse_buttons_pressed  = cls.mouse_buttons_pressed
		cls.mouse_buttons_pressed = pygame.mouse.get_pressed()

		cls.mouse.left = True if cls.mouse_buttons_pressed[0] else False
		cls.mouse.left_up = True if cls.last_mouse_buttons_pressed[0] and not cls.mouse_buttons_pressed[0] else False
		
		cls.mouse.middle = True if cls.mouse_buttons_pressed[1] else False
		cls.mouse.middle_up = True if cls.last_mouse_buttons_pressed[1] and not cls.mouse_buttons_pressed[1] else False
		
		cls.mouse.right = True if cls.mouse_buttons_pressed[2] else False
		cls.mouse.right_up = True if cls.last_mouse_buttons_pressed[2] and not cls.mouse_buttons_pressed[2] else False
				

	##############################################
	# PROGRAM INTERACTION
	##############################################
	@classmethod	
	def set_mode(cls, resolution, fullscreen = False, use_hardware = False):
		""" Changes screen size. Accepts a tuple of width/height. """
		fullscreen = pygame.FULLSCREEN if fullscreen else 0

		if use_hardware:
			fullscreen = fullscreen | pygame.HWSURFACE | pygame.DOUBLEBUF
			
		cls.screen = pygame.display.set_mode(resolution, fullscreen)
		cls.screen_rect = cls.screen.get_rect()
		cls.regions[0] = cls.screen.get_rect()
	

	@classmethod
	def set_title(cls, title_name):
		""" Changes title of the window. Accepts a string. """
		pygame.display.set_caption(title_name)


	@classmethod
	def set_fps(cls, fps):
		""" Sets the frames per second to a new value. Accepts an integer. """
		cls.current_fps = fps


	@classmethod
	def quit(cls):
		""" Closes the program. """
		cls.running = False
				
	exit = quit
	
	
	##############################################
	# REGIONS
	##############################################
	@classmethod		
	def define_region(cls, region_id, x, y, w, h):
		cls.regions[region_id] = pygame.Rect((x, y), (w, h))
		

	##############################################
	# SCROLLS
	##############################################
	@classmethod		
	def start_scroll(cls, scroll_id, graph = None, background = None, region = 0, lock = 0):
		cls.scroll[scroll_id] = Scroll(graph, background, region, lock)
		cls.add_process(cls.scroll[scroll_id], False)
		
		
	@classmethod
	def stop_scroll(cls, scroll_id):
		if scroll_id in cls.scroll:
			cls.kill_process(cls.scroll[scroll_id].id)
			del cls.scroll[scroll_id]
		

	##############################################
	# INPUT
	##############################################
	@classmethod		
	def key(cls, key_type):
		""" Allows you to easily ask if a key was pressed. Uses pygame constants. """
		if cls.keys_pressed[key_type]:
			return True
		else:
			return False

	@classmethod		
	def key_released(cls, key_type):
		""" Allows you to easily ask if a key was released. Compares keys pressed this frame
		to the keys pressed last frame. Uses pygame constants. """
		if cls.last_keys_pressed[key_type] and not cls.keys_pressed[key_type]:
			return True
		else:
			return False
		

	##############################################
	# PROCESS INTERACTION
	##############################################
	@classmethod	
	def p(cls, id_no):
		""" given an ID number this will return the process """
		if id_no in cls.processes:
			return cls.processes[id_no]
		else:
			return None

	@classmethod
	def processes_in_status(cls, status):
		"""
		Returns list of processes in the given status - one of:
			0			(normal)
			S_FREEZE	(frozen)
			S_SLEEP		(sleeping)			
		"""
		retlist = []
		for proc_id in cls.processes:
			proc = cls.processes[proc_id]
			if proc.status == status:
				retlist.append(proc)
		return retlist


	@classmethod
	def processes_by_type(cls, type_name):
		"""
		Returns a list of processes with a particular class name.
		"""
		process_list = []
		
		for obj in cls.processes:
			if type(type_name) == type(""):
				if cls.processes[obj].__class__.__name__ == type_name:
					process_list.append(cls.processes[obj])
			else:
				if isinstance(cls.processes[obj], type_name):
					process_list.append(cls.processes[obj])
				
		return process_list
	

	@classmethod		
	def signal(cls, process, signal_code, tree=False):
		""" Signal will let you kill a process or put it to sleep
		
			Will accept a process instance or an ID number to check against one,
			or a process type as a string to check for all of a specific type,
			or a list of any of the above
		
			The tree parameter can be used to recursively signal all the 
			processes(es) descendants
		
			Signal types-
			S_KILL - Permanently removes the process
			S_SLEEP - Process will disappear and will stop executing code
			S_FREEZE - Process will stop executing code but will still appear
				and will still be able to be checked for collisions.
			S_WAKEUP - Wakes up or unfreezes the process """
		
		# We've entered a list
		if not isinstance(process, basestring) and is_iterable(process):
			
			# recurse for each item of list
			for p in process:
				cls.signal(p, signal_code, tree)	
		
		# We've entered a process type
		elif isinstance(process, type) and issubclass(process, Process):						
			
			for obj in cls.processes_by_type(process):
				cls.single_object_signal(obj, signal_code, tree)
		
		# We've entered a specific type as a string
		elif type(process) == type(""):
			
			import copy
			process_iter = copy.copy(cls.processes)
			
			#TODO: maybe hash by process type?
			for obj in process_iter:
				if cls.processes[obj].__class__.__name__ == process:
					cls.single_object_signal(cls.processes[obj], signal_code, tree)

		# We've entered an ID number
		elif type(process) == type(1):
			process = cls.p(process)
			
			if process != None:
				cls.single_object_signal(process, signal_code, tree)
			else:
				return
		
		# Passed in an object directly	  
		else:
			cls.single_object_signal(process, signal_code, tree)
			return
	
	
	@classmethod	
	def exists(cls, process_id):
		
		if type(process_id) == type(""):
			for obj in cls.processes:
				if cls.processes[obj].__class__.__name__ == process_id:
					return True
				
			return False

		elif type(process_id) == type(1):
			
		   return process_id in cls.processes
			
		else:
			return process_id.id in cls.processes
		
			
	@classmethod	
	def single_object_signal(cls, process, signal_code, tree=False):
		""" Used by signal as a shortcut """
		
		# do children
		if tree:
			next_child = process.son
			while next_child != None:
				cls.single_object_signal(next_child, signal_code, True)
				next_child = next_child.bigbro
		
		# do this one
		if signal_code == S_KILL:
			cls.kill_process(process.id)
		elif signal_code == S_WAKEUP:
			process.status = 0
		elif signal_code == S_SLEEP:
			process.status = S_SLEEP
		elif signal_code == S_FREEZE:
			process.status = S_FREEZE		 
		
		
	##############################################
	# MATH STUFF
	##############################################
	@classmethod 
	def normalise_angle(cls, angle):
		"""
		Returns an equivalent angle value between -180000 and 180000
		"""
		if angle > 180000:
			angle -= 360000 * ((angle-180000)//360000 + 1)
		if angle < -180000:
			angle += 360000 * ((-angle-180000)//360000 + 1)
		return angle
	
	@classmethod
	def angle_difference(cls, start_angle, end_angle):
		"""
		Returns the angle to turn by to get from start_angle to end_angle.
		The sign of the result indicates the direction in which to turn.
		"""
		start_angle = cls.normalise_angle(start_angle)
		end_angle = cls.normalise_angle(end_angle)
		
		difference = end_angle - start_angle
		if difference > 180000:
			difference -= 360000
		if difference < -180000:
			difference += 360000
			
		return difference
	
	@classmethod
	def near_angle(cls, curr_angle, targ_angle, increment):
		""" 
		Returns an angle which has been moved from 'curr_angle' closer to 
		'targ_angle' by 'increment'. increment should always be positive, as 
		angle will be rotated in the direction resulting in the shortest 
		distance to the target angle.
		"""
		# Normalise curr_angle
		curr_angle = cls.normalise_angle(curr_angle)
			
		# Normalise targ_angle
		targ_angle = cls.normalise_angle(targ_angle)
			
		# calculate difference
		difference = cls.angle_difference(curr_angle, targ_angle)
			
		# do increment
		if math.fabs(difference) < increment:
			return targ_angle
		else:
			dir = difference / math.fabs(difference)
			return curr_angle + increment*dir
	
	@classmethod	
	def fget_angle(cls, pointax, pointay, pointbx, pointby):
		 return math.degrees(math.atan2(-(pointby - pointay), pointbx - pointax))*1000


	@classmethod	
	def fget_dist(cls, pointax, pointay, pointbx, pointby):
		 return int(math.sqrt((math.pow((pointby - pointay), 2) + math.pow((pointbx - pointax), 2))))


	@classmethod
	def get_distx(cls, angle, distance):
		""" Returns the horisontal distance in pixels of a specified displacement. """
		return int(math.cos(
							math.radians(angle/1000)
							) * distance)


	@classmethod
	def get_disty(cls, angle, distance):
		""" Returns the vertical distance in pixels of a specified displacement. """
		return -int(math.sin(
							 math.radians(angle/1000)
							 ) * distance)


	##############################################
	# IMAGE HANDLING
	##############################################
	@classmethod	
	def load_png(cls, filename, colorkey = None):
		""" Loads a file into memory and converts it accordingly """
		try:
			image = pygame.image.load(filename)
		except pygame.error, message:
			print 'Cannot load image:', filename
			raise SystemExit, message
		
		image = image.convert()

		if colorkey is not None:
			image.set_colorkey(colorkey)
		else:
			image.set_colorkey(cls.colorkey)

		return image


	@classmethod
	def save_png(cls, graph, filename):
		""" 
		Saves the surface as specified filename. (BMP, TGA, PNG or JPG)
		"""
		pygame.image.save(graph, filename)
	
	

	##############################################
	# GRAPHIC MANIPULATION
	##############################################
	@classmethod	
	def new_map(cls, width, height):
		"""
		Creates a new graphic, with all transparent pixels at specified w/h
		"""
		new = pygame.Surface((width, height))
		new.set_colorkey(cls.colorkey)
		new.fill(cls.colorkey) 
		return new
	
	map_new = new_map
	

	@classmethod	
	def map_clone(cls, graph, resize = None):
		"""
		Copies the surface passed in and returns a copy of it.
		Can pass in a tuple of width,height to falicitate cropping.
		"""
		if resize == None:
			return graph.copy()
		else:
			new = cls.new_map(resize[0], resize[1])
			cls.map_block_copy(new, 0, 0, graph, 0, 0, resize[0], resize[1])
			return new
	
		
	@classmethod	
	def map_clear(cls, graph, colour):
		 """
		 Clears the surface completely with a colour.
		 Colour is tuple (R, G, B, A)
		 """
		 graph.fill(colour)


	@classmethod	
	def map_put_pixel(cls, graph, x, y, colour):
		 """
		 Will place a single pixel on a surface at the specified coordinate
		 and at the colour specified.
		 Colour is tuple (R, G, B, A)
		 """
		 graph.set_at((int(x), int(y)), colour)

		
	@classmethod
	def unload_map(cls, graph):
		""" 
		Simply kills a map, freeing memory
		"""
		del graph
		
		
	@classmethod	
	def map_block_copy(cls, dest_graph, dest_x, dest_y, origin_graph,
					   origin_x = 0, origin_y = 0, width = None, height = None, flags = 0):
		 """
		 Draws (blits) a rectangular block from one surface onto another surface.
		 """
		 # TODO: Flags
		 width = origin_graph.get_width() if width == None else width
		 height = origin_graph.get_height() if height == None else height
		 
		 dest_graph.blit(origin_graph, (dest_x, dest_y), pygame.Rect((origin_x, origin_y), (width, height)))


	@classmethod
	def map_put(cls, dest_graph, origin_graph, x, y):
		""" 
		Draws a surface on to another surface at specified coords
		"""
		dest_graph.blit(origin_graph, (x, y))


	@classmethod
	def map_xput(cls, dest_graph, origin_graph, x, y, angle = 0, size = 100, flags = 0):
		""" 
		Draws a surface on to another surface at specified coords with extra params
		"""
		# TODO: Flags
		altered = origin_graph.copy()
		
		if size != 100:
			graph_size = altered.get_size()
			new_width = int(graph_size[0] * (size / 100.0))
			new_height = int(graph_size[1] * (size / 100.0))
			altered = pygame.transform.scale(altered, (new_width, new_height))

		if angle != 0:
			altered = pygame.transform.rotate(altered, angle / 1000)
		 
		dest_graph.blit(altered, (x, y))


	@classmethod
	def map_xputnp(cls, dest_graph, origin_graph, x, y, angle = 0, scale_x = 100, scale_y = 100, flags = 0):
		""" 
		Like map_xput but allows you to set the width/height specifically
		"""
		# TODO: Flags
		altered = origin_graph.copy()
		
		if scale_x != 100 or scale_y != 100:
			graph_size = altered.get_size()
			new_width = int(graph_size[0] * (scale_x / 100.0))
			new_height = int(graph_size[1] * (scale_y / 100.0))
			altered = pygame.transform.scale(altered, (new_width, new_height))

		if angle != 0:
			altered = pygame.transform.rotate(altered, angle / 1000)
		 
		dest_graph.blit(altered, (x, y))
		

	
	##############################################
	# TEXT HANDLING
	##############################################
	@classmethod	
	def load_fnt(cls, filename, size = 20):
		return pygame.font.Font(filename, size)
	 
	 
	@classmethod	
	def write(cls, font, x, y, alignment = 0, text = ""):
		return Text(font, x, y, alignment, text)
	

	@classmethod	
	def delete_text(cls, text):
		if cls.processes[text.id] != None:
			cls.kill_process(text.id)
