"""
Copyright (c) 2009 Mark Frimston

Permission is hereby granted, free of charge, to any person
obtaining a copy of this software and associated documentation
files (the "Software"), to deal in the Software without
restriction, including without limitation the rights to use,
copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following
conditions:

The above copyright notice and this permission notice shall be
included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
OTHER DEALINGS IN THE SOFTWARE.
"""
 
from mrf.search import *
import math

def _trc_check_axis(axis, start_pos, diff, grid_size, end_grid_pos, end_pos, collision_callback):
	
	oth_ax = 1 if axis==0 else 0
	
	coll_point = None
	
	# if direction not perpendicular, find collision along this axis
	if diff[axis] != 0:
		
		pos = (start_pos[0],start_pos[1])
		dir = (diff[0]/math.fabs(diff[0]) if diff[0]!=0 else 0, 
			   diff[1]/math.fabs(diff[1]) if diff[1]!=0 else 0)
		
		# calculate gradient
		grad = diff[oth_ax]/diff[axis]
		
		# work out how far to move to the next boundary on this axis
		offset = pos[axis] % grid_size[axis]
		ax_inc = (grid_size[axis] if diff[axis]>=0 else 0) - offset
		oth_ax_inc = grad * ax_inc
		inc = { axis : ax_inc , oth_ax : oth_ax_inc }
	
		# move to first boundary and test for collision
		collision = _trc_move_collide(axis, pos,inc,dir,grid_size,
									  end_grid_pos,end_pos,collision_callback)
		pos = collision[0]
		
		# if ray collided
		if collision[1] != None:
			coll_point = collision[1]
			
		else:
			
			#work out how far to move to the next boundary on this axis
			inc = {axis:grid_size[axis]*dir[axis], oth_ax:grid_size[axis]*dir[axis]*grad}

			iter_ = 0
			
			while collision[1] == None:
				
				collision = _trc_move_collide(axis, pos,inc,dir,grid_size,
											  end_grid_pos,end_pos,collision_callback)
				pos = collision[0]
				
				if collision[1] != None:
					coll_point = collision[1]
					
				iter_ +=1

				if iter_ == 1000:
					print "too many iterations in tile checker thing"
					exit()
					
	if coll_point != None:
		
		# Determine distance to this collision point
		sq_dist = math.pow(coll_point[0][0]-start_pos[0],2) + math.pow(coll_point[0][1]-start_pos[1],2)
		
		return (sq_dist, coll_point)
	
	else:
		return None
	

def _trc_move_collide(axis, pos, inc, dir, grid_size, end_grid_pos, end_pos, collision_callback):
	
	oth_ax = 0 if axis==1 else 1
	
	# move
	pos = (pos[0]+inc[0], pos[1]+inc[1])
		
	# determine grid ref(s) to check
	grid_poses = []
	if pos[oth_ax] % grid_size[oth_ax] == 0:
		# if we are on the boundary between 2 tiles, need to check both of these tiles
		grid_poses.append({ axis: int(math.floor((pos[axis] + dir[axis]*(grid_size[axis]/2)) / grid_size[axis])),
						   oth_ax : int(math.floor((pos[oth_ax] - dir[oth_ax]*(grid_size[oth_ax]/2)) / grid_size[oth_ax])) })
		grid_poses.append({ axis: int(math.floor((pos[axis] + dir[axis]*(grid_size[axis]/2)) / grid_size[axis])),
						   oth_ax : int(math.floor((pos[oth_ax] + dir[oth_ax]*(grid_size[oth_ax]/2)) / grid_size[oth_ax])) })
	else:
		grid_poses.append({ axis : int(math.floor((pos[axis] + dir[axis]*(grid_size[axis]/2)) / grid_size[axis])), 
				oth_ax : int(math.floor(pos[oth_ax] / grid_size[oth_ax])) })
		
	# call function to determine if the block(s) we're at should stop the ray
	blocked = False
	grid_pos = None
	for gp in grid_poses:
		if collision_callback(pos, (gp[0],gp[1])):
			blocked = True
			grid_pos = gp
			
	if blocked:
			
		norm = { axis : -dir[axis], oth_ax : 0 }
				
		return (pos , (pos,(grid_pos[0],grid_pos[1]),(norm[0],norm[1])))
	
	else:
		
		grid_pos = grid_poses[0]
		
		# Check if this is the square with the end position in it
		if (grid_pos[0],grid_pos[1]) == end_grid_pos:
			
			return (pos, (end_pos, None, None))
		
		else:
			return (pos, None)
	

def tile_ray_cast(start_pos, end_pos, grid_size, collision_callback):
	"""
	Function to determine where a ray, projected across a grid of blocking and 
	non-blocking squares, should stop.
	
	Parameters:
		start_pos			Tuple containing the x and y coordinates of the ray's origin
		end_pos				Tuple containing the x and y coordinates of the ray's end point, 
							thus specifying the ray's direction and maximum length.						   
		grid_size			Tuple containing the width and height of the grid across which
							to project the ray.
		collision_callback	Function which will be called to determine whether a square
							on the grid should stop the ray or not. See section below. 
							Note the sequence in which this function is called does not 
							correspond with the path of the ray.							
	Returns:
		A tuple containing:
			The coordinates of the stopping point as a 2-item tuple
			The grid position of the square the ray collided with, as a 2-item tuple
				(or None if the ray never collided)
			The normal of the square edge the ray collided with, as a 2-item tuple
				(or None if the ray never collided)
			
	collision_callback:
		Parameters:
			The coordinates of the potential collision point as a 2-item tuple
			The grid position of the square to check, as a 2-item tuple
		Returns:
			True if this square would stop the ray, False otherwise
	"""
	
	diff = (end_pos[0]-start_pos[0],end_pos[1]-start_pos[1])
	
	# Work out grid ref of end pos
	end_grid_pos = (int(math.floor(end_pos[0]/grid_size[0])),
					int(math.floor(end_pos[1]/grid_size[1])))
	
	# Check if we're in the end grid pos
	grid_pos = (int(math.floor(start_pos[0]/grid_size[0])),
				int(math.floor(start_pos[1]/grid_size[1])))
	
	if(grid_pos == end_grid_pos):
		
		result = (end_pos, None, None)
		
	else:
	
		x_cand = _trc_check_axis(0, start_pos, diff, grid_size, end_grid_pos, 
								 end_pos, collision_callback)
		y_cand = _trc_check_axis(1, start_pos, diff, grid_size, end_grid_pos, 
								 end_pos, collision_callback)
		
		if x_cand == None and y_cand == None:
			
			# No collisions
			result = (end_pos, None, None)
		
		elif x_cand != None and y_cand == None:
			
			# X collision only
			result = x_cand[1]
		
		elif y_cand != None and x_cand == None:
			
			# Y collision only
			result = y_cand[1]
			
		else:
			
			# Compare distances to x and y collisions
			if x_cand[0] < y_cand[0]:
				result = x_cand[1]
			elif y_cand[0] < x_cand[0]:
				result = y_cand[1]
			else:
				
				# Special case - we've hit exactly on a corner. Test the surrounding
				# squares to determine the surface direction. 
				# The collision testing counts a boundary as a collision if either 
				# of the tiles are blocking, so we only need to test for combinations of
				# the 2 adjacent blocks - the corner block is irrelevant unless both of
				# these are non-blocking.
				dir = (diff[0]/math.fabs(diff[0]),diff[1]/math.fabs(diff[1]))
				
				grid_poses = {}
				grid_blocks = {}
				for i in [-1,1]:
					for j in [-1,1]:
						grid_poses[(i,j)] = (int(math.floor((x_cand[1][0][0]+grid_size[0]/2*i)/grid_size[0])),
											 int(math.floor((x_cand[1][0][1]+grid_size[1]/2*j)/grid_size[1])))				  
						grid_blocks[(i,j)]= collision_callback(x_cand[1][0],grid_poses[(i,j)])
				
				root_half = math.sqrt(0.5)
				
				# Horizontal surface / side glance
				if grid_blocks[(dir[0]*-1,dir[1])] and not grid_blocks[(dir[0],dir[1]*-1)]:
					
					result = (x_cand[1][0], grid_poses[(dir[0]*-1,dir[1])], (0,dir[1]*-1))
					
				# Vertical surface / side glance
				elif not grid_blocks[(dir[0]*-1,dir[1])] and grid_blocks[(dir[0],dir[1]*-1)]:
					
					result = (x_cand[1][0], grid_poses[(dir[0],dir[1]*-1)], (dir[0]*-1,0))
					
				# Convex corner
				elif not grid_blocks[(dir[0]*-1,dir[1])] and not grid_blocks[(dir[0],dir[1]*-1)]:
					
					result = (x_cand[1][0], grid_poses[(dir[0],dir[1])], (dir[0]*root_half*-1,dir[1]*root_half*-1))
					
				# Concave corner / squeeze
				else:
					
					# Which block do we hit here? Just assume a vertical surface collision but
					# bounce straight back 
					result = (x_cand[1][0], grid_poses[(dir[0],dir[1]*-1)], (dir[0]*root_half*-1,dir[1]*root_half*-1))
				
	return result




class TilePathfinder(AStar):
	"""
	An A* search implementation for navigating a map of square tiles. Uses a 
	callback to determine the cost of moving to different tiles.
	"""
	
	DIAG_VAL = math.sqrt(2)
	
	def __init__(self, tilecost_func):
		"""
		tilecost_func should be a function returning the cost of moving to a 
		given tile position. It should take 2 parameters: the x and y positions 
		of a tile respectively, and return the cost value as a float value. If
		a tile should never be moved into, None should be returned
		"""
		AStar.__init__(self)
		self.tilecost_func = tilecost_func
		
	def search(self, start, finish):
		"""
		Performs the search, taking two 2-item tuples of x and y tile coordinates 
		for the start position and the end position respectively, and returning a 
		list of 2-item tuples representing the pairs of x-y tile coordinates 
		making up the path from the start position to the end position.
		"""
		return AStar.search(self, start, finish)
		
	def cost(self, state):
		diag = False
		# Check the 2 sides of the diagonal move for impossible moves
		if state.previous != None:
			xmove = state.value[0]-state.previous.value[0]
			ymove = state.value[1]-state.previous.value[1]
			diag = xmove !=0 and ymove !=0
			if diag:
				xcheck = (state.previous.value[0]+xmove, state.previous.value[1])
				ycheck = (state.previous.value[0], state.previous.value[1]+ymove)
				if (self.tilecost_func(xcheck[0],xcheck[1])==None 
						or self.tilecost_func(ycheck[0],ycheck[1])==None):
					return None				   
		tile_cost = self.tilecost_func(state.value[0],state.value[1])
		if tile_cost != None:
			path_cost = ((state.previous.path_cost if state.previous != None else 0)
						 + tile_cost * (TilePathfinder.DIAG_VAL if diag else 1))
			cost = (path_cost
						+ math.sqrt(math.pow(self.finish[0]-state.value[0],2) 
									+ math.pow(self.finish[1]-state.value[1],2))) 
			return path_cost, cost
		else:
			return None
	
	def expand(self, state):
		expanded = []
		for i in range(-1,2):
			for j in range(-1,2):
				if not(i==0 and j==0):
					new_state = AStar.State((state.value[0]+i,state.value[1]+j), state)
					costs = self.cost(new_state)
					if costs!=None:
						new_state.path_cost = costs[0]
						new_state.cost = costs[1]
						expanded.append(new_state)
		return expanded



#-------------------------------------------------------------------------------
# Testing
#-------------------------------------------------------------------------------
if __name__ == "__main__":
	
	import unittest
	
	class RayCastTest(unittest.TestCase):
		
		def setUp(self):
			self.blocks = [
				[1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
				[1, 0, 0, 0, 0, 0, 0, 0 ,1 ,0, 1],
				[1, 0, 0, 0, 0, 0, 0, 0 ,1 ,0, 1],
				[1, 0, 0, 1, 1, 0, 0, 0 ,0 ,0, 1],
				[1, 0, 0, 1, 0, 0, 0, 0 ,0 ,0, 1],
				[1, 0, 0, 0, 0, 0, 1, 0 ,0 ,0, 1],
				[1, 0, 0, 0, 0, 0, 1, 0 ,0 ,0, 1],
				[1, 0, 0, 0, 0, 1, 0, 0 ,0 ,0, 1],
				[1, 0, 1, 0, 0, 0, 0, 1 ,0 ,0, 1],
				[1, 0, 0, 0, 0, 0, 0, 1 ,0 ,0, 1],
				[1, 1, 1, 1, 1, 1, 1, 1 ,1 ,1, 1]
			  ]
			self.root_half = math.sqrt(0.5)
		
		def ray_collide(self, pos, grid_pos):
	
			if grid_pos[0]<0 or grid_pos[0]>=11 or grid_pos[1]<0 or grid_pos[1]>=11:
				return True
		
			return self.blocks[grid_pos[1]][grid_pos[0]] == 1 
			
		def testStandardCollision(self):
			
			start_pos = (5.5*32,5.5*32)
			end_pos = (7.5*32,4.5*32)
			coll = tile_ray_cast(start_pos, end_pos, (32,32), self.ray_collide)
			expected = ((6*32,5.25*32), (6,5), (-1,0))	   
			self.assertEqual(coll, expected)
			
		def testSameTile(self):
			
			start_pos = (5.5*32,5.5*32)
			end_pos = (5.6*32,5.6*32)
			coll = tile_ray_cast(start_pos, end_pos, (32,32), self.ray_collide)
			expected = ((5.6*32,5.6*32), None, None)
			self.assertEqual(coll,expected)
			
		def testNonCollision(self):
			
			start_pos = (5.5*32,5.5*32)
			end_pos = (4.5*32,7.5*32)
			coll = tile_ray_cast(start_pos, end_pos, (32,32), self.ray_collide)
			expected = ((4.5*32,7.5*32), None, None)
			self.assertEqual(coll,expected)
			
		def testHorizontal(self):
			
			start_pos = (5.5*32,5.5*32)
			end_pos = (6.5*32,5.5*32)
			coll = tile_ray_cast(start_pos, end_pos, (32,32), self.ray_collide)
			expected = ((6*32,5.5*32), (6,5), (-1,0))
			self.assertEqual(coll,expected)
			
			start_pos = (4.5*32,5.5*32)
			end_pos = (6.5*32,5.5*32)
			coll = tile_ray_cast(start_pos, end_pos, (32,32), self.ray_collide)
			expected = ((6*32,5.5*32), (6,5), (-1,0))
			self.assertEqual(coll,expected)
			
		def testVertical(self):
			
			start_pos = (4.5*32,4.5*32)
			end_pos = (4.5*32,3.5*32)
			coll = tile_ray_cast(start_pos, end_pos, (32,32), self.ray_collide)
			expected = ((4.5*32,4*32), (4,3), (0,1))
			self.assertEqual(coll,expected)
			
			start_pos = (4.5*32,5.5*32)
			end_pos = (4.5*32,3.5*32)
			coll = tile_ray_cast(start_pos, end_pos, (32,32), self.ray_collide)
			expected = ((4.5*32,4*32), (4,3), (0,1))
			self.assertEqual(coll,expected)
			
		def testConcaveCorner(self):
			
			start_pos = (5.5*32,5.5*32)
			end_pos = (3.5*32,3.5*32)
			coll = tile_ray_cast(start_pos, end_pos, (32,32), self.ray_collide)
			expected = ((4*32,4*32), (3,4), (self.root_half,self.root_half))
			self.assertEqual(coll,expected)
			
			start_pos = (5.5*32,6.5*32)
			end_pos = (6.5*32,7.5*32)
			coll = tile_ray_cast(start_pos, end_pos, (32,32), self.ray_collide)
			expected = ((6*32,7*32), (6,6), (-self.root_half,-self.root_half))
			self.assertEqual(coll,expected)
			
		def testConvexCorner(self):
			
			start_pos = (4.5*32,5.5*32)
			end_pos = (3.5*32,4.5*32)
			coll = tile_ray_cast(start_pos, end_pos, (32,32), self.ray_collide)
			expected = ((4*32,5*32), (3,4), (self.root_half,self.root_half))
			self.assertEqual(coll,expected)
			
		def testVerticalSurfaceCorner(self):
			
			start_pos = (5.5*32,5.5*32)
			end_pos = (6.5*32,6.5*32)
			coll =	tile_ray_cast(start_pos, end_pos, (32,32), self.ray_collide)
			expected = ((6*32,6*32), (6,5), (-1,0))
			self.assertEqual(coll,expected)
			
		def testHorizontalSurfaceCorner(self):
			
			start_pos = (5.5*32,9.5*32)
			end_pos = (4.5*32,10.5*32)
			coll = tile_ray_cast(start_pos, end_pos, (32,32), self.ray_collide)
			expected = ((5*32,10*32), (5,10), (0,-1)) 
			self.assertEqual(coll,expected)
			
			
			
	class TestPathfind(unittest.TestCase):
		
		def setUp(self):
			
			self.map = [
							[0, 8, 8, 8, 8, 0, 0, 0, 0, 0],
							[0, 8, 0, 0, 8, 0, 8, 8, 8, 0],
							[0, 8, 0, 0, 0, 0, 1, 1, 1, 0],
							[0, 8, 0, 0, 8, 0, 8, 8, 8, 8],
							[0, 8, 8, 8, 8, 0, 0, 0, 0, 0],
							[0, 0, 0, 0, 8, 0, 0, 8, 0, 0],
							[8, 8, 8, 1, 8, 0, 0, 0, 8, 0],
							[0, 0, 0, 1, 8, 0, 0, 0, 0, 8],
							[0, 0, 8, 1, 8, 0, 8, 8, 8, 8],
							[0, 0, 8, 1, 0, 0, 8, 0, 0, 0]							  
						]			 
			self.search = TilePathfinder(self.costFunc)
			
		def costFunc(self, x, y):
			if x<0 or x>=10 or y<0 or y>=10:
				return None
			else:
				if self.map[y][x] == 0:
					return 1
				elif self.map[y][x] == 1:
					return 3
				else:
					return None
		
		def testSimple(self):
			path = self.search.search((9,0), (5,0))
			self.assertEquals([(9,0),(8,0),(7,0),(6,0),(5,0)],path)
		  
		def testCost(self):
			path = self.search.search((9,1), (5,1))
			self.assertEquals([(9,1),(9,0),(8,0),(7,0),(6,0),(5,0),(5,1)],path)
			
		def testLong(self):
			path = self.search.search((9,2),(0,0))
			self.assertEquals([(9,2),(9,1),(9,0),(8,0),(7,0),(6,0),(5,0),(5,1),
							   (5,2),(5,3),(5,4),(5,5),(5,6),(5,7),(5,8),(5,9),
							   (4,9),(3,9),(3,8),(3,7),(3,6),(3,5),(2,5),(1,5),
							   (0,5),(0,4),(0,3),(0,2),(0,1),(0,0)],path)
		   
		def testBlocked(self):
			path = self.search.search((9,9),(0,0))
			self.assertEquals(None, path) 
			
		def testDiagWall(self):
			path = self.search.search((9,6),(8,7))
			self.assertEquals([(9,6),(9,5),(8,4),(7,4),(6,4),(6,5),(6,6),(7,7),(8,7)],path)

	unittest.main()
	
	
	
