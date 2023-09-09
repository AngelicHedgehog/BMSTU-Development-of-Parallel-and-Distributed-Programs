import numpy as np
import asyncio
import time

def dot_matrices(
        left_matrix: np.matrix[np.int64],
        right_matrix : np.matrix[np.int64]
        ) -> np.matrix[np.int64]:

    assert left_matrix.shape == right_matrix.shape and left_matrix.shape[0] == left_matrix.shape[1]
    
    result_matrix = np.matrix(np.zeros(left_matrix.shape, dtype=np.int64))
    
    for row in range(result_matrix.shape[0]):
        for col in range(result_matrix.shape[1]):
            for i in range(result_matrix.shape[0]):
                result_matrix[row, col] += left_matrix[row, i] * right_matrix[i, col]

    return result_matrix

async def private_dot_matrices_parallel(
        left_matrix: np.matrix[np.int64],
        right_matrix : np.matrix[np.int64],
        block_size : np.int8,
        block_cords : tuple[np.int8, np.int8],
        result_matrix : np.matrix[np.int64]
        ) -> None:
    
    for row in range(block_cords[0], block_cords[0] + block_size):
        for col in range(block_cords[1], block_cords[1] + block_size):
            for i in range(left_matrix.shape[0]):
                result_matrix[row, col] += left_matrix[row, i] * right_matrix[i, col]

async def dot_matrices_parallel(
        left_matrix: np.matrix[np.int64],
        right_matrix : np.matrix[np.int64],
        split_size : np.int64 = 1
        ) -> np.matrix[np.int64]:

    assert left_matrix.shape == right_matrix.shape and left_matrix.shape[0] == left_matrix.shape[1]
    
    assert left_matrix.shape[0] % split_size == 0
    
    result_matrix = np.matrix(np.zeros(left_matrix.shape, dtype=np.int64))

    block_size = left_matrix.shape[0] // split_size

    async with asyncio.TaskGroup() as tg:
        for block_row in range(0, split_size * block_size, block_size):
            for block_col in range(0, split_size * block_size, block_size):
                tg.create_task(
                    private_dot_matrices_parallel(
                        left_matrix, right_matrix, 
                        block_size, (block_row, block_col),
                        result_matrix)
                    )
                
    return result_matrix


def main():
    size = 150
    left_matrix = np.matrix(np.random.rand(size, size) * 10, dtype=np.int64)
    right_matrix = np.matrix(np.random.rand(size, size) * 10, dtype=np.int64)

    print("Numpy lib: ", end="")
    start_time = time.time()
    result_matrix = np.dot(left_matrix, right_matrix)
    assert np.array_equal(result_matrix, result_matrix)
    print("%f\n" % (time.time() - start_time))

    print("Parallel hand-made func (treads: 10): ", end="")
    start_time = time.time()
    assert np.array_equal(result_matrix, asyncio.run(dot_matrices_parallel(left_matrix, right_matrix, 10)))
    print("%f\n" % (time.time() - start_time))

    print("Parallel hand-made func (treads: 5): ", end="")
    start_time = time.time()
    assert np.array_equal(result_matrix, asyncio.run(dot_matrices_parallel(left_matrix, right_matrix, 5)))
    print("%f\n" % (time.time() - start_time))

    print("Parallel hand-made func (treads: 2): ", end="")
    start_time = time.time()
    assert np.array_equal(result_matrix, asyncio.run(dot_matrices_parallel(left_matrix, right_matrix, 2)))
    print("%f\n" % (time.time() - start_time))

    print("Parallel hand-made func (treads: 1): ", end="")
    start_time = time.time()
    assert np.array_equal(result_matrix, asyncio.run(dot_matrices_parallel(left_matrix, right_matrix, 1)))
    print("%f\n" % (time.time() - start_time))

    print("Linear hand-made func: ", end="")
    start_time = time.time()
    assert np.array_equal(result_matrix, dot_matrices(left_matrix, right_matrix))
    print("%f\n" % (time.time() - start_time))

if __name__ == "__main__":
    main()