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

import math

class AStar(object):
    """
    Abstract A* base class which can be extended to implement A* searches. The
    'cost' and 'expand' methods should be overridden in order to acheive this.
    See the docstrings for these methods for more information.
    The 'search' method is used to perform the search itself.
    
    example:
        
        class MyAStar(AStar):
            ...
    
        astar = MyAStar()
        path = astar.search(start, finish)
    """
    
    class State(object):
        """
        Represents a particular way of reaching a problem state. 
        Attributes:
            value:       The state value
            path_cost:   The cost of the path up to and including this state
            cost:        The cost of this state: path_cost plus an esimate of distance to goal            
            previous:    The state this state was reached from
        """
                
        def __init__(self, value, previous):
            self.value = value
            self.path_cost = 0
            self.cost = 0
            self.previous = previous
            
        def cost_compare(self, other):
            if self.cost > other.cost:
                return 1
            elif self.cost < other.cost:
                return -1
            else:
                return 0
            
        def __str__(self):
            return str(self.value)+":"+str(self.cost)
    
    def __init__(self):
        self._reset()
        
    def _reset(self):
        self.open_set = {}
        self.closed_set = {}
        self.start = None
        self.finish = None
    
    def search(self, start, finish):
        """
        Performs the A* search. start and finish are the starting and ending state
        values, respectively.
        Returns the ordered list of state values representing the found path, or 
        None if no path could be found.        
        """
        self._reset()
        self.start = start
        self.finish = finish
        
        # Get cost of start state and add to open set
        start_state = AStar.State(start, None)
        costs = self.cost(start_state)
        if costs!=None:
            start_state.path_cost = costs[0]
            start_state.cost = costs[1]
            self.open_set[start_state.value] = start_state
        
        while len(self.open_set)>0:
            
            # Get state in open set with lowest cost
            open_sorted = sorted(self.open_set.values(),AStar.State.cost_compare)
            best = open_sorted[0]
            
            # If this is the finish state, return path
            if best.value == finish:
                return self._make_path(best)
        
            # Move the state to closed set
            del(self.open_set[best.value])
            self.closed_set[best.value] = best
            
            # Expand the state and iterate through branches
            for b in self.expand(best):
                
                # Ignore if already expanded
                if self.closed_set.has_key(b.value):
                    continue
                
                # Ignore if already open with a better path_cost
                if (self.open_set.has_key(b.value) 
                        and self.open_set[b.value].path_cost <= b.path_cost):
                    continue
                
                # Add state to open set
                self.open_set[b.value] = b
        
        return None
    
    def _make_path(self, finish_state):
        path = [finish_state.value]
        next = finish_state.previous
        while next != None:
            path = [next.value] + path
            next = next.previous
        return path
    
    def expand(self, state):
        """
        Should be overidden by subclasses to return the list of states branching
        from the given state (whether already visited or not). state is an instance
        of AStar.State and returned states should be too, with all their attributes
        filled in. The cost function can be used to calculate each state's path_cost
        and cost values. Note that cost will return None if a state represents an
        impossible move which should not be included in the branching states.
        """
        return []
    
    def cost(self, state):
        """
        Should be overidden by subclasses to return the cost of a state, indicating
        to the algorithm how preferable a choice of move is. state is an instance
        of AStar.State with its cost and path_cost attributes set to 0. 
        Should return a 2-item tuple containing the path_cost and cost values 
        respectively, or None if the state should not be considered at all (an 
        impossible move). 
        The path_cost is the total cost to move along the path from the start to 
        this state, and cost is path_cost plus an estimate of the distance to 
        the goal. The path_cost can be found by adding the movement cost of this 
        state to state.previous.path_cost, if available.        
        """
        return 0;