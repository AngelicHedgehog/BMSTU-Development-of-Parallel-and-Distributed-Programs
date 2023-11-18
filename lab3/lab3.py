import numpy as np
from OpenMP_funcs import openmp_matrix_dot

matrix = np.array([[1.0, 2.0], [3.0, 4.0]])
array = np.array([5.0, 6.0])

result = openmp_matrix_dot(matrix.tolist(), list(array), 1)
print(result) # Output: [17.0, 39.0]
