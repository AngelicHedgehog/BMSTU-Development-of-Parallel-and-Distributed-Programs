#include <Python.h>
#include <omp.h>

static PyObject* openmp_matrix_dot(PyObject* self, PyObject* args) {
    PyObject *matrix_obj, *vector_obj;
    int num_threads;

    // Получение аргументов из Python
    if (!PyArg_ParseTuple(args, "OOi", &matrix_obj, &vector_obj, &num_threads)) {
        return NULL;
    }

    // Проверка типов аргументов
    if (!PyList_Check(matrix_obj) || !PyList_Check(vector_obj)) {
        PyErr_SetString(PyExc_TypeError, "Аргументы должны быть списками");
        return NULL;
    }

    // Получение размеров матрицы и вектора
    Py_ssize_t matrix_rows = PyList_Size(matrix_obj);
    Py_ssize_t matrix_cols = PyList_Size(PyList_GetItem(matrix_obj, 0));
    Py_ssize_t vector_size = PyList_Size(vector_obj);

    // Проверка размеров матрицы и вектора
    if (matrix_cols != vector_size) {
        PyErr_SetString(PyExc_ValueError, "Размеры матрицы и вектора не совпадают");
        return NULL;
    }

    // Создание результирующего вектора
    PyObject* result_vector = PyList_New(matrix_rows);

    #pragma omp parallel num_threads(num_threads)
    {
        #pragma omp for schedule(static) reduction(+:sum)
        for (Py_ssize_t i = 0; i < matrix_rows; ++i) {
            double sum = 0.0;

            // Вычисление скалярного произведения строки матрицы и вектора
            for (Py_ssize_t j = 0; j < matrix_cols; ++j) {
                PyObject* row = PyList_GetItem(matrix_obj, i);
                PyObject* element = PyList_GetItem(row, j);
                double value = PyFloat_AsDouble(element);

                PyObject* vector_element = PyList_GetItem(vector_obj, j);
                double vector_value = PyFloat_AsDouble(vector_element);

                sum += value * vector_value;
            }

            // Запись результата в результирующий вектор
            #pragma omp critical
            {
                PyObject* result_element = PyFloat_FromDouble(sum);
                PyList_SetItem(result_vector, i, result_element);
            }
        }
    }

    return result_vector;
}


static PyMethodDef methods[] = {
    {"openmp_matrix_dot", openmp_matrix_dot, METH_VARARGS, "Умножает матрицу на вектор"},
    {NULL, NULL, 0, NULL}
};

static struct PyModuleDef module = {
   PyModuleDef_HEAD_INIT,
   "OpenMP_funcs",
   NULL,
   -1,
   methods
};

PyMODINIT_FUNC PyInit_OpenMP_funcs(void) {
    return PyModule_Create(&module);
}
