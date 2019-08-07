#TODO - rewrite

import qvec

class Optimizer():
	def __init__(self, error_eval=None, value=None, changer=None):
		self.error_eval = error_eval
		self.value = value
		self.changer = changer
		self.velosity = None
	def iterate(self):
		self.error = error_eval(value)
		self.changer(value, self.error, self.velocity)

class VectorValueOptimizer():
	def __init__(self):
		super.__init__(value=qvec)
	
