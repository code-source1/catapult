#include "main.cpp"
#include <iostream>

void test_case(int input[MAX_SIZE][MAX_SIZE], int rows, int cols, int expected, MatrixAnalysis* strategy) {
    int result = strategy->longest(input, rows, cols);
    std::cout << "Test case expected: " << expected << ", got: " << result;
    std::cout << (result == expected ? " - PASS" : " - FAIL") << std::endl;
}

int main() {
    int matrix1[MAX_SIZE][MAX_SIZE] = {{9,9,4},{6,6,8},{2,1,1}};
    int matrix2[MAX_SIZE][MAX_SIZE] = {{3,4,5},{3,2,6},{2,2,1}};
    int matrix3[MAX_SIZE][MAX_SIZE] = {{1}};

    MatrixAnalysis strategy;  
    test_case(matrix1, 3, 3, 4, &strategy);
    test_case(matrix2, 3, 3, 4, &strategy);
    test_case(matrix3, 1, 1, 1, &strategy);

    return 0;
}