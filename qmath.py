import math

class Vec3d:
	self.x = 0
	self.y = 0
	self.z = 0
	def __init__(self, x, y, z):
		self.x = x
		self.y = y
		self.z = z
	def hypot_sqr(self, other:Vec3d):
		return (self.x-other.x) ** 2 + (self.y-other.y) ** 2 + (self.z-other.z) ** 2
	def hypot(self. other:Vec3d):
		return math.sqrt(self.hypot_sqr(self, other))
