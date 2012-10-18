
""" 
Ludum Dare 16
Loads media files
"""

import os
from fenix.program import Program
import pygame
from consts import *


class Media:

	fonts = {}
	sounds = {}
	player_gfx = {}
	gfx_hud = {}

	gfx_debris = []
	gfx_debris_particles = {}
	gfx_debris_inventory = None
	gfx_valuable_debris = {}

	gfx_particles_trail = {}

	gfx_exp = None
	gfx_mine = None
	gfx_turret = None
	gfx_turret_laser = None
	gfx_title = None

	gfx_tutorial_messages = {}

	gfx_landmarks = {}

	def __init__(self):
		
		# FONTS
		self.fonts['system'] = Program.load_fnt(os.path.join("fnt","system_font.ttf"), 10)
		self.fonts['vera'] = Program.load_fnt(os.path.join("fnt","vera.ttf"), 12)
		self.fonts['mini_vera'] = Program.load_fnt(os.path.join("fnt","vera.ttf"), 11)

		# GRAPHICS
		self.player_gfx['ship'] = Program.load_png(os.path.join("gfx", "player.png"))
		self.player_gfx['crosshair'] = Program.load_png(os.path.join("gfx", "crosshair.png"))
		self.player_gfx['laser'] = Program.load_png(os.path.join("gfx", "lazor.png"))
		self.player_gfx['tractor'] = Program.load_png(os.path.join("gfx", "tractor.png"))
		self.player_gfx['wormhole'] = Program.load_png(os.path.join("gfx", "wormhole.png"))
		self.player_gfx['hub_arrow'] = Program.load_png(os.path.join("gfx", "hub_arrow.png"))

		self.gfx_landmarks['spacestation'] = Program.load_png(os.path.join("gfx", "landmark-spacestation.png"))
		self.gfx_landmarks['cruiser'] = Program.load_png(os.path.join("gfx", "landmark-cruiser.png"))

		self.gfx_exp = Program.load_png(os.path.join("gfx", "exp.png"))

		self.gfx_mine = Program.load_png(os.path.join("gfx", "mine.png"))
		self.gfx_turret = Program.load_png(os.path.join("gfx", "turret.png"))
		self.gfx_turret_laser = Program.load_png(os.path.join("gfx", "enemylazor.png"))
		self.gfx_title = Program.load_png(os.path.join("gfx", "title.png"))

		self.gfx_hud['hold'] = Program.load_png(os.path.join("gfx", "holdhud.png"))
		self.gfx_hud['hull'] = Program.load_png(os.path.join("gfx", "hullhud.png"))
		self.gfx_hud['invenbutton'] = self.load_tile_map(Program.load_png(os.path.join("gfx", "hudinvenbutton.png")), size = 105, height = 24)
		self.gfx_hud['inventory'] = Program.load_png(os.path.join("gfx", "hudinven.png"))
		self.gfx_hud['hub'] = Program.load_png(os.path.join("gfx", "hudhub.png"))
		self.gfx_hud['hub_launch'] = self.load_tile_map(Program.load_png(os.path.join("gfx", "hudhub_launch.png")), size = 105, height = 24)
		self.gfx_hud['hub_repair'] = self.load_tile_map(Program.load_png(os.path.join("gfx", "hudhub_repair.png")), size = 105, height = 24)
		self.gfx_hud['hub_upgradehull'] = self.load_tile_map(Program.load_png(os.path.join("gfx", "hudhub_upgradehull.png")), size = 156, height = 24)
		self.gfx_hud['hub_upgradehold'] = self.load_tile_map(Program.load_png(os.path.join("gfx", "hudhub_upgradehold.png")), size = 156, height = 24)
		self.gfx_hud['hub_upgradetractor'] = self.load_tile_map(Program.load_png(os.path.join("gfx", "hudhub_upgradetractor.png")), size = 174, height = 24)
		self.gfx_hud['hub_upgradeengine'] = self.load_tile_map(Program.load_png(os.path.join("gfx", "hudhub_upgradeengine.png")), size = 174, height = 24)
		self.gfx_hud['hub_sellstuff'] = self.load_tile_map(Program.load_png(os.path.join("gfx", "hudhub_sell.png")), size = 105, height = 24)
		self.gfx_hud['hub_sell'] = Program.load_png(os.path.join("gfx", "hudsell.png"))
		self.gfx_hud['hub_sell_cancel'] = self.load_tile_map(Program.load_png(os.path.join("gfx", "hudhub_cancel.png")), size = 60, height = 17)
		self.gfx_hud['hub_sell_sell'] = self.load_tile_map(Program.load_png(os.path.join("gfx", "hudhub_sellall.png")), size = 60, height = 17)

		self.gfx_debris_inventory = Program.load_png(os.path.join("gfx", "debris", "debris_inventory.png"))
		
		for a in xrange(1, DEBRIS_GFX_NUM+1):
			self.gfx_debris.append(
				Program.load_png(os.path.join("gfx", "debris", "debris" + str(a) + ".png"))
				)

		self.gfx_debris_particles = self.load_tile_map(
			Program.load_png(os.path.join("gfx", "debris", "debris_particles.png")),
			size = 10
			)

		for a in xrange(1, 6):
			self.gfx_valuable_debris['tier'+str(a)] = self.load_tile_map(
				Program.load_png(os.path.join("gfx", "debris", "tier"+str(a)+"_valuables.png")),
				size = 30
				)

		self.player_gfx['indicator'] = self.load_tile_map(
			Program.load_png(os.path.join("gfx", "indicator.png")),
			size = 4
			)

		self.gfx_particles_trail = self.load_tile_map(
			Program.load_png(os.path.join("gfx", "particles", "trail.png")),
			size = 6
			)

		for a in xrange(1, 7):
			self.gfx_tutorial_messages[a] = Program.load_png(os.path.join("gfx", "tut"+str(a)+".png"))
			
		# SOUNDS
		self.sounds['collision'] = pygame.mixer.Sound(os.path.join("sounds", "collision.wav"))
		self.sounds['wormhole'] = pygame.mixer.Sound(os.path.join("sounds", "wormholeout.wav"))
		self.sounds['tractor'] = pygame.mixer.Sound(os.path.join("sounds", "tractor.wav"))
		self.sounds['pickup'] = pygame.mixer.Sound(os.path.join("sounds", "pickup.wav"))
		self.sounds['laser'] = pygame.mixer.Sound(os.path.join("sounds", "laser.wav"))
		self.sounds['explosion'] = pygame.mixer.Sound(os.path.join("sounds", "explosion.wav"))
		self.sounds['beep'] = pygame.mixer.Sound(os.path.join("sounds", "beep.wav"))
		self.sounds['moneyout'] = pygame.mixer.Sound(os.path.join("sounds", "moneyout.wav"))
		self.sounds['startfly'] = pygame.mixer.Sound(os.path.join("sounds", "startfly.wav"))
		self.sounds['flyloop'] = pygame.mixer.Sound(os.path.join("sounds", "flyloop.wav"))


	def load_tile_map(self, tilemap_sur, start_height = 0, end_height = None, size = 16, height = None):

		if height == None:
			height = size
			
		w = tilemap_sur.get_width()
		h = tilemap_sur.get_height()

		tiles = {}
		num = 0

		for a in range(start_height, h/height):
			for b in range(w/size):
				tiles[num] = Program.new_map(size,height)
				Program.map_block_copy(tiles[num], 0, 0, tilemap_sur, b*size, a*height, size, height)
				num+=1
			if end_height != None and end_height == a:
				return tiles

		return tiles
