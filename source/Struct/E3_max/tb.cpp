#include "main.cpp"
#include <iostream>


void test_case(int points[][2], int numPoints, int expected) {
    Solution sol;
    sol.numPoints = numPoints;
    for (int i = 0; i < numPoints; ++i) {
        sol.points[i][0] = points[i][0];
        sol.points[i][1] = points[i][1];
    }
    int result = sol.maxPoints();
    std::cout << "Test case expected: " << expected << ", got: " << result;
    std::cout << (result == expected ? " - PASS" : " - FAIL") << std::endl;
}

int main() {
    int points1[][2] = {{1,1}, {2,2}, {3,3}};
    test_case(points1, 3, 3);

    int points2[][2] = {{1,1}, {3,2}, {5,3}, {4,1}, {2,3}, {1,4}};
    test_case(points2, 6, 4);

    return 0;
}
