#include "main.cpp"
#include <iostream>
#include "ac_fixed.h"

typedef ac_fixed <16, 8, true> fixed_point_type;

extern int svm_classify(fixed_point_type features[10]);

int main() {
    fixed_point_type test_features1[10] = {0.5, -0.3, 0.8, -0.2, -0.75, 0.5, -0.1, 0.6, 0.21};
    fixed_point_type test_features2[10] = {-0.4, 0.6, -0.7, 0.3,  -0.3, 0.8, -0.2, -0.75, 0.85};

    int result1 = svm_classify(test_features1);
    int result2 = svm_classify(test_features2);

    std::cout << "Result for test set 1: " << result1 << std::endl;
    std::cout << "Result for test set 2: " << result2 << std::endl;

    return 0;
}
