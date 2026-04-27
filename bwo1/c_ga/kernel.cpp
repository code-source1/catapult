#include <fstream>
#include <sstream>
#include <iostream>
#include <vector>
#include <string>
#include <cstdlib>
#include <iomanip>

typedef double size1_t;
typedef double size2_t;
typedef double result_t;

std::vector<result_t> ga(const double nums1[], const double nums2[], size1_t size1, size2_t size2) {
    std::vector<result_t> chosen;
    size_t i = 0, j = 0;
    while (i < static_cast<size_t>(size1) || j < static_cast<size_t>(size2)) {
        if (i < static_cast<size_t>(size1) && j < static_cast<size_t>(size2)) {
            if (nums1[i] < nums2[j]) {
                chosen.push_back(nums1[i]);
                ++i;
            } else if (nums1[i] > nums2[j]) {
                chosen.push_back(nums2[j]);
                ++j;
            } else {
                chosen.push_back(nums1[i]);
                ++i;
                ++j;
            }
        } else if (i < static_cast<size_t>(size1)) {
            chosen.push_back(nums1[i]);
            ++i;
        } else if (j < static_cast<size_t>(size2)) {
            chosen.push_back(nums2[j]);
            ++j;
        }
    }
    return chosen;
}