package main

import "fmt"

func privateDotMatrices(leftMatrix, rightMatrix [][]int, blockSize, blockRow, blockCol int, resultMatrix *[][]int) {
	for row := blockRow; row != blockRow+blockSize; row++ {
		for col := blockCol; col != blockCol+blockSize; col++ {
			for i := 0; i != len(leftMatrix); i++ {
				(*resultMatrix)[row][col] += leftMatrix[row][i] * rightMatrix[i][col]
			}
		}
	}
}

func dotMatrices(leftMatrix, rightMatrix [][]int) (resMatrix [][]int, err error) {
	resultMatrix := [][]int{{0, 0, 0}, {0, 0, 0}, {0, 0, 0}}

	var blockSize int = len(leftMatrix) / 3
	splitSize := 3

	for blockRow := 0; blockRow != splitSize*blockSize; blockRow += blockSize {
		for blockCol := 0; blockCol != splitSize*blockSize; blockCol += blockSize {
			go privateDotMatrices(leftMatrix, rightMatrix, blockSize, blockRow, blockCol, &resultMatrix)
		}
	}

	return resultMatrix, nil
}

func main() {
	matrix1 := [][]int{{1, 2, -1}, {0, 2, 1}, {1, 1, 1}}
	matrix2 := [][]int{{0, 2, 1}, {1, 1, 1}, {1, 2, -1}}

	resMatrix, err := dotMatrices(matrix1, matrix2)
	if err != nil {
		_ = fmt.Errorf("Error: %e", err)
		return
	}

	fmt.Println(resMatrix)
}
