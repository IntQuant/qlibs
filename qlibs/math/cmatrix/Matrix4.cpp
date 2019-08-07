//#include <iostream>
//#include "Matrix4.h"

#pragma GCC optimize ("-O3,-ffast-math")
#define fl float
extern "C" {
    void __declspec(dllexport) mat4mul(const fl * a, const fl * other, fl * res) {
        //fl * res[16];
        res[0] = (other[0] * a[0] + other[1] * a[4] + other[2] * a[8] + other[3] * a[12]);
        res[1] = (other[0] * a[1] + other[1] * a[5] + other[2] * a[9] + other[3] * a[13]);
        res[2] = (other[0] * a[2] + other[1] * a[6] + other[2] * a[10] + other[3] * a[14]);
        res[3] = (other[0] * a[3] + other[1] * a[7] + other[2] * a[11] + other[3] * a[15]);
        res[4] = (other[4] * a[0] + other[5] * a[4] + other[6] * a[8] + other[7] * a[12]);
        res[5] = (other[4] * a[1] + other[5] * a[5] + other[6] * a[9] + other[7] * a[13]);
        res[6] = (other[4] * a[2] + other[5] * a[6] + other[6] * a[10] + other[7] * a[14]);
        res[7] = (other[4] * a[3] + other[5] * a[7] + other[6] * a[11] + other[7] * a[15]);
        res[8] = (other[8] * a[0] + other[9] * a[4] + other[10] * a[8] + other[11] * a[12]);
        res[9] = (other[8] * a[1] + other[9] * a[5] + other[10] * a[9] + other[11] * a[13]);
        res[10] = (other[8] * a[2] + other[9] * a[6] + other[10] * a[10] + other[11] * a[14]);
        res[11] = (other[8] * a[3] + other[9] * a[7] + other[10] * a[11] + other[11] * a[15]);
        res[12] = (other[12] * a[0] + other[13] * a[4] + other[14] * a[8] + other[15] * a[12]);
        res[13] = (other[12] * a[1] + other[13] * a[5] + other[14] * a[9] + other[15] * a[13]);
        res[14] = (other[12] * a[2] + other[13] * a[6] + other[14] * a[10] + other[15] * a[14]);
        res[15] = (other[12] * a[3] + other[13] * a[7] + other[14] * a[11] + other[15] * a[15]);
    }
}
//int main() {}
int main() {
    fl IDENTITY[] = {1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1};
    fl out[16];
    mat4mul(IDENTITY, IDENTITY, out);
//    //for (int i=0;i<16;i++) std::cout << res[i] << " ";
}
