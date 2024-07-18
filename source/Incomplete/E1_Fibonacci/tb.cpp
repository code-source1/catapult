#include "main.cpp"
#include <iostream>

void test_case(int* input, int n, int expected, int mode) {  
    Solution sol;
    for (int i = 0; i < n; ++i) {
        sol.arr[i] = input[i];
    }
    int result = sol.FibSubseq(n, mode);  // Pass mode to FibSubseq
    std::cout << "Test case with expected result " << expected << ": " << (result == expected ? "PASS" : "FAIL") << std::endl;
}

int main() {
    int arr1[] = {1, 2, 3, 4, 5, 6, 7, 8};
    int expected1 = 5;
    test_case(arr1, 8, expected1, 0);  

    int arr2[] = {1, 3, 7, 11, 12, 14, 18};
    int expected2 = 3;
    test_case(arr2, 7, expected2, 0);  

    return 0;
}
