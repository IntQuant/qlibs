import unittest
try:
    from qlibs_cyan.math.mat4 import Matrix4
except:
    print("Skipping C matrix tests")
else:
    class Matrix4TestCase(unittest.TestCase):
        def test_creation(self):
            Matrix4()
        
        def test_mapping(self):
            m = Matrix4()
            for i in range(4):
                for j in range(4):
                    m[i, j] = i*13+j+1
            for i in range(4):
                for j in range(4):
                    self.assertAlmostEqual(m[i, j], i*13+j+1)
        
        def test_bytes(self):
            m = Matrix4()
            b = m.bytes()
            self.assertEqual(b, bytes([0]*64))
            m[0, 1] = 10
            for i in range(4):
                for j in range(4):
                    m[i, j] = i*13+j+1
                    self.assertNotEqual(m.bytes(), bytes([0]*64), msg=f"Changing element at [{i}, {j}] does not affect output")
                    m[i, j] = 0
        
        def test_multiply(self):
            m1 = Matrix4()
            m2 = Matrix4()
            m1 @ m2
