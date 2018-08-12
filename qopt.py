import qvec

class Optimizer():
	def __init__(self, error_eval=None, value=None, changer=None):
		self.error_eval = error_eval
		self.value = value
		self.changer = changer
		self.velosity = None
	def setErrorEval(self, error_eval):
		self.error_eval = error_eval
	def setValue(self, value):
		self.value = value
	def setChanger(self, changer):
		self.changer = changer
	def setVelosity(self, velosity):
		self.velosity = velosity
	def nullVelosity(self):
		self.velosity = None
	def iterate(self):
		self.error = error_eval(value)
		self.changer(value, self.error, self.velosity)

class VectorValueOptimizer():
	def __init__(self):
		super.__init__(value=qvec)
	
