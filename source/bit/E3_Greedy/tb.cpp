#include "main.cpp"
#include <iostream>
#include <vector>
using namespace std;

int main() {
    vector<vector<int>> tests1 = {
        {2, 4, 5, 8, 10},
        {1, 3, 5, 7, 9},
        {1, 2, 3, 4, 5}
    };
    vector<vector<int>> tests2 = {
        {4, 6, 8, 9},
        {3, 5, 100},
        {6, 7, 8, 9, 10}
    };
    vector<int> expected = {30, 109, 40};
    
    Solution sol;
    bool all_tests_passed = true;

    typedef ac_int<16, false> width2;  // Matches the definition in Solution class
    typedef ac_int<8, false> width3;   // Matches the definition in Solution class

    for (int i = 0; i < tests1.size(); i++) {
        width2 nums1[Solution::MAX_SIZE];
        width2 nums2[Solution::MAX_SIZE];
        width3 size1 = tests1[i].size();
        width3 size2 = tests2[i].size();

        for (int j = 0; j < size1; j++) {
            nums1[j] = tests1[i][j];
        }
        for (int j = 0; j < size2; j++) {
            nums2[j] = tests2[i][j];
        }

        int result = sol.maxSum(nums1, size1, nums2, size2);
        cout << "Test " << (i+1) << ": Result = " << result << ", Expected = " << expected[i] << endl;
        if (result != expected[i]) {
            all_tests_passed = false;
        }
    }
    
    if (all_tests_passed) {
        cout << "All tests passed!" << endl;
    } else {
        cout << "Some tests failed." << endl;
    }
    
    return 0;
}
