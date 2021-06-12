
from qlibs.math.matrix import PyMatrix4, Matrix4
import time

ITERATIONS = 100000

def matrix_perf():
    for cls in [Matrix4, PyMatrix4]:
        print("Testing", cls.__name__)
        m1 = cls()
        m2 = cls()
        start = time.perf_counter()
        for _ in range(ITERATIONS):
            m1 * m2
        end = time.perf_counter()
        print("%s took %.2f s" % (cls.__name__, end-start))
    



if __name__ == "__main__":
    matrix_perf()

