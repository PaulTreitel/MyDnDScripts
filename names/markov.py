import random

class Markov:
	def __init__(self, table, initial_state):
		self.table = table
		self.state = initial_state

	def step(self):
		old_state = self.state
		if len(self.state) > 1:
			old_state = self.state[-2:]
		r = random.random()
		s = 0
		states = self.table[old_state]
		for next, prob in states.items():
			s += prob
			if r <= s:
				self.state += next
				return

	def setState(self, st):
		self.state = st