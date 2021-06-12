//#include <iostream>
//#include "Matrix4.h"
#define PY_SSIZE_T_CLEAN
#include <Python.h>

extern PyTypeObject Matrix4_Type;

#pragma GCC optimize ("-O3,-ffast-math")

void mat4mul(const float * a, const float * other, float * res) {
    //float * res[16];
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

static PyObject *method_mat4mul(PyObject *self, PyObject *args) {
    return PyLong_FromLong(10l);
}

static PyMethodDef mat4_methods[] = {
    {"mat4mul", method_mat4mul, METH_VARARGS, "Faster matrix multiplication"},
    {NULL, NULL, 0, NULL}
};

typedef struct {
    PyObject_HEAD
    float data[16];
} Matrix4_Object;

static Py_ssize_t Matrix4_len_(PyObject *self) {
    return (Py_ssize_t)16;
}

static PyObject *Matrix4_getitem_(Matrix4_Object *self, PyObject *args) {
    int x, y;
    if (!PyArg_ParseTuple(args, "ii", &x, &y)) {
        return NULL;
    }
    if (x<0 || x>3 || y<0 || y>3) {
        PyErr_SetString(PyExc_IndexError, "Indexes out of range [0..3]");
        return NULL;
    };
    float value = self->data[x*4+y];
    return PyFloat_FromDouble((double)value);
}

static int Matrix4_setitem_(Matrix4_Object *self, PyObject *key, PyObject *value) {
    int x, y;
    double v;
    if (value == NULL) {
        PyErr_SetString(PyExc_TypeError, "Can not delete elements from matrix");
        return -1;
    }

    if (!PyArg_ParseTuple(key, "ii", &x, &y)) {
        return -1;
    }
    
    v = PyFloat_AsDouble(value);
    if (PyErr_Occurred() != NULL) return -1;
    
    if (x<0 || x>3 || y<0 || y>3) {
        PyErr_SetString(PyExc_IndexError, "Indexes out of range [0..3]");
        return -1;
    };
    self->data[x*4+y] = (float)v;
    return 0;
}

static PyObject *Matrix4_multiply(Matrix4_Object *self, PyObject *other) {
    if (!PyObject_TypeCheck(other, &Matrix4_Type)) {
        Py_RETURN_NOTIMPLEMENTED;
    }
    PyObject *type = PyObject_Type((PyObject*)self);
    
    Matrix4_Object *new_matrix = (Matrix4_Object*)PyObject_Call(type, Py_BuildValue("()"), NULL);
    mat4mul(self->data, ((Matrix4_Object*)other)->data, new_matrix->data);
    return (PyObject*)new_matrix;

}

static PyObject *Matrix4_richcompare(Matrix4_Object *self, PyObject *other, int op) {
    if (op != Py_EQ && op != Py_NE) {
        Py_RETURN_NOTIMPLEMENTED;
    }
    if (!PyObject_TypeCheck(other, &Matrix4_Type)) {
        Py_RETURN_FALSE;
    }
    int res = memcmp(self->data, ((Matrix4_Object*)other)->data, sizeof(self->data))==0;
    if (res == (op == Py_EQ)) {
        Py_RETURN_TRUE;
    } else {
        Py_RETURN_FALSE;
    }
}

static PyObject *Matrix4_bytes(Matrix4_Object *self, PyObject *args) {
    return PyBytes_FromStringAndSize((char*)self->data, sizeof(self->data));
}

static PyMethodDef Matrix4_methods[] = {
    //{"__getitem__", (PyCFunction)Matrix4_getitem_, METH_VARARGS, ""},
    {"bytes", (PyCFunction)Matrix4_bytes, METH_NOARGS, "Returns internal data as bytes"},
    {NULL, NULL, 0, NULL}
};

static PyMappingMethods Matrix4_mapping = {
    .mp_length = Matrix4_len_,
    .mp_subscript = (binaryfunc)Matrix4_getitem_,
    .mp_ass_subscript = (objobjargproc)Matrix4_setitem_,
};

static PyNumberMethods Matrix4_number = {
    .nb_matrix_multiply = (binaryfunc)Matrix4_multiply,
    .nb_inplace_matrix_multiply = (binaryfunc)Matrix4_multiply,
};

PyTypeObject Matrix4_Type = {
    PyVarObject_HEAD_INIT(NULL, 0)
    .tp_name = "qlibs.math.mat4.Matrix4",
    .tp_doc = "4 by 4 matrix class",
    .tp_basicsize = sizeof(Matrix4_Object),
    .tp_itemsize = 0,
    .tp_flags = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,
    .tp_new = PyType_GenericNew,
    .tp_methods = Matrix4_methods,
    .tp_as_mapping = &Matrix4_mapping,
    .tp_as_number = &Matrix4_number,
    .tp_richcompare = (richcmpfunc)&Matrix4_richcompare,
};

static int mat4_exec(PyObject *m)
{
    if (PyType_Ready(&Matrix4_Type) < 0)
        goto fail;
    PyModule_AddObject(m, "Matrix4", (PyObject *)&Matrix4_Type);
    return 0;
 fail:   
    Py_XDECREF(m);
    return -1;
}

static struct PyModuleDef_Slot mat4_slots[] = {
    {Py_mod_exec, mat4_exec},
    {0, NULL},
};

static struct PyModuleDef mat4module = {
    PyModuleDef_HEAD_INIT,
    "mat4mul",
    "Faster matrix operations",
    0,
    mat4_methods,
    mat4_slots,
};

PyMODINIT_FUNC PyInit_mat4(void)
{
    return PyModuleDef_Init(&mat4module);
}

/*
int main() {
    float IDENTITY[] = {1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1};
    float out[16];
    mat4mul(IDENTITY, IDENTITY, out);
//    //for (int i=0;i<16;i++) std::cout << res[i] << " ";
}
*/
