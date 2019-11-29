# The guide to vectors

## Overview

Vectors are collections of numbers. They can be added, substracted, multiplied and divided, in addition to several useful methods. Because of that they are great for representing locations and directions.

## Creating vectors

- Vec(iterable) - creates vector from iterable
- Vec(*args) - creates vector as if args were an iterable, so that `Vec([0, 1])` and `Vec(0, 1)` are equal.
- Vec2(x, y) - specialized vector class, which is faster(direct access to **x** and **y** fields) and is always two-dimensional.

## Indexing

First 4 components of vector can be accessed when they are present like this:
```python
from qlibs.math import Vec
vec = Vec(0, 1, 2, 3)
print(vec.x, vec.y, vec.z, vec.w)
#Also possible to index like list
assert vec.x == vec[0]
assert vec.y == vec[1]
assert vec.z == vec[2]
assert vec.w == vec[3]
```

## Operators
```python
from qlibs.math import Vec

v0 = Vec(10, 5)
v1 = Vec(0, 20)

#Plus and minus work elementwise
print(v0+v1) #Vec(10, 25)
print(v0-v1) #Vec(10, -15)

#You can multiply or divide vectors by vectors, only by numbers
#Resulting vector will have elements of first array with operations applied
print(v0*2)  #Vec(20, 10)
print(v0/2)  #Vec(5.0, 2.5)
print(v0//2) #Vec(5, 2)

#Unary minus is also supported
print(-v0)   #Vec(-10, -5)

#As well as abs()
print(abs(-v0)) # Vec(10, 5)

#It is also possible to iterate for each element in vector, like list
for e in v0:
    print(e)

#Length of the vector (Note: to get number of dimensions len(vec) is required)
print(v0.len())    #equal to math.hypot(v0.x, v0.y), but also works for more dimensions
print(v0.len_sq()) #v0.len()**2

#Calculates dot product of vectors
print(v0.dot(v1))

#Normalize divides vector by it's length, so it will have length of 1
v0.normalize()
assert v0.len() == 1
```

