import numpy as np
import time

import OpenMP_funcs

class SLESolver:

    @classmethod
    def __next_iter(
        cls,
        matrix_a: np.matrix[float, float],
        vector_x: np.ndarray[None, float],
        vector_b: np.ndarray[None, float],
        tau: float
    ) -> np.ndarray[None, float]:
        return vector_x - (openmp_matrix_dot(matrix_a, vector_x) - vector_b) * tau

    @classmethod
    def __end_measure(
        cls,
        matrix_a: np.matrix[float, float],
        vector_x: np.ndarray[None, float],
        vector_b: np.ndarray[None, float],
    ) -> float:
        return (np.linalg.norm(openmp_matrix_dot(matrix_a, vector_x) - vector_b) /
                np.linalg.norm(vector_b))

    @classmethod
    def simple_iteration(
        cls,
        matrix_a: np.matrix[float, float],
        vector_b: np.ndarray[None, float],
        epsilon: float = 1e-10,
    ) -> (np.ndarray[float, float] | None):

        N = vector_b.shape[0]
        assert matrix_a.shape == (N, N)
        assert vector_b.shape == (N, 1)

        tau = .01 / N
        last_iter_measure = None
        vector_x = np.full((N, 1), 0)
        for _ in iter(int, 1):
            actual_iter_measure = cls.__end_measure(
                matrix_a, vector_x, vector_b)
            if actual_iter_measure < epsilon:
                break

            if (last_iter_measure is not None and
                    actual_iter_measure > last_iter_measure):
                if tau < 0:
                    return None
                tau *= -1

            vector_x = cls.__next_iter(matrix_a, vector_x, vector_b, tau)
            last_iter_measure = actual_iter_measure

        return vector_x

def openmp_matrix_dot(
    matrix_a: np.matrix[float, float],
    vector_x: np.ndarray[None, float],
) -> np.ndarray[None, float]:
    
    matrix_a = matrix_a.tolist()
    vector_x = list(vector_x)

    res_matrix = OpenMP_funcs.openmp_matrix_dot(matrix_a, vector_x, num_threads)

    return np.matrix(res_matrix).transpose()


# num_threads = int(input())
num_threads = 1

_matrix_a = np.matrix([
    [9.,  1.,  3., -7.,  9., -0., -9.,  7.],
    [-8., 10., -3., -0., -4.,  1.,  1., -3.],
    [-8.,  7.,  7., -0., -0., 10., -1., -0.],
    [7., -5.,  5.,  9.,  1.,  1., -8., -4.],
    [3., -3.,  8., -4.,  9.,  4.,  4.,  9.],
    [9.,  6., -9.,  7.,  3., 10., -3., -6.],
    [4., -8.,  8.,  2., -2., -2.,  9., 10.],
    [-4., 10.,  1., -7., -2.,  8., -8.,  5.],
])
_vector_x = np.array([
    [-3.],
    [-9.],
    [-2.],
    [-6.],
    [-1.],
    [4.],
    [-4.],
    [5.],
])
_vector_b = openmp_matrix_dot(_matrix_a, _vector_x)

start = time.time()
_res_vector_x = SLESolver.simple_iteration(
    _matrix_a,
    _vector_b,
)
delta_time = time.time() - start

print(_vector_x)
print(_res_vector_x)
print(f"Execute time: {delta_time}")
