import math

class VecNd:
	def __init__(self, verticles:iter):
		self.v = list(verticles)


	def __eq__(self, other):
		return hasattr(other, "v") and self.v == other.v


	def __getattr__(self, name):
		vertnames = ('x', 'y', 'z')
		if name in vertnames:
			ind = vertnames.index(name)
			if len(self.v)>ind:
				return self.v[ind]


	def __hash__(self):
		return hash(sum(map(hash, self.v)))


	def __str__(self):
		return " ".join(map(str, self.v))


	def __repr__(self):
		return "VecNd(" + ", ".join(map(str, self.v)) + ")"

	
	def map_by_verticle(self, other, function:callable):
		assert isinstance(other, (VecNd, Vec2d, Vec3d)), "wrong class"
		assert len(self.v) == len(other.v), "wrong dimensions"
		return VecNd([function(x, y) for x, y in zip(self.v, other.v)])

	
	def __add__(self, other):
		return self.map_by_verticle(other, lambda x,y:x+y)

	
	def __iadd__(self, other):
		return self.__add__(other)
	
	
	def __sub__(self, other):
		return self.map_by_verticle(other, lambda x,y:x-y)

	
	def __isub__(self, other):
		return self.__sub__(other)
	
	
	def __mul__(self, other):
		if isinstance(other, (VecNd, Vec2d, Vec3d)):
			return self.map_by_verticle(other, lambda x,y:x*y)
		elif isinstance(other, (int, float)):
			return VecNd(map(lambda x:x*other, self.v))
		else:
			raise TypeError("Cannot multiply vector by " + str(type(other)))

	
	def __imul__(self, other):
		return self.__mul__(other)


	def __truediv__(self, other):
		if isinstance(other, (VecNd, Vec2d, Vec3d)):
			return self.map_by_verticle(other, lambda x,y:x/y)
		elif isinstance(other, (int, float)):
			return VecNd(map(lambda x:x/other, self.v))
		else:
			raise TypeError("Cannot divide vector by " + str(type(other)))

	
	def __itruediv__(self, other):
		return self.__mul__(other)
	

	def len_sqr(self):
		return sum(map(lambda x:x**2, self.v))


	def len(self):
		return math.sqrt(len_sqr(self))
	
	
	def __pos__(self):
		return self
	
	
	def __neg__(self):
		return VecNd([map(lambda x:-x, self.v)])
	
	
	def __abs__(self):
		return VecNd([map(abs, self.v)])

		

class Vec2d(VecNd):
	def __init__(self, x, y):
		super.__init__([x, y])



class Vec3d(VecNd):
	def __init__(self, x, y, z):
		super.__init__([x, y, z])





if __name__ == "__main__":
	v1 = VecNd([1, 2])
	v2 = VecNd([1, 2])
	v3 = VecNd([1, 3])
	
	assert v1 == v2
	assert not (v1 == 1)
	
	assert v1.x == 1
	assert v1.z is None
	
	
	assert str(v3) == "1 3"
	assert repr(v3) == "VecNd(1, 3)"
	print(v1 + v2)
	print(v1 * v2)
	print(v3 * 10)
	try:
		v1 * "error"
	except Exception as e:
		assert "Cannot multiply" in str(e)
	else:
		raise AssertionError("No error while multiplying")
	
	print(v1 / 10)
	try:
		v1 / "error"
	except Exception as e:
		assert "Cannot divide" in str(e)
	else:
		raise AssertionError("No error while division")
	
	
	
