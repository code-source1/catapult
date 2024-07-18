#include <iostream>
#include "main.cpp"

#define MAX_N 1000  
#define N 12        

extern int trap(const int height[]);

void testTrap() {
    int height1[N] = {0, 1, 0, 2, 1, 0, 1, 3, 2, 1, 2, 1};
    int expected1 = 6;
    int result1 = trap(height1);
    std::cout << "Test 1 - Expected: " << expected1 << ", Got: " << result1 << std::endl;

    int height2[N] = {4, 2, 0, 3, 2, 5};
    int expected2 = 9;
    int result2 = trap(height2);
    std::cout << "Test 2 - Expected: " << expected2 << ", Got: " << result2 << std::endl;
}

int main() {
    testTrap();
    return 0;
}
