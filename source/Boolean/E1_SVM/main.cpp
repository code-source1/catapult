#include <ac_fixed.h>
typedef ac_fixed<16, 8, true> fixed_point_type;
const int FEATURE_COUNT = 10;
fixed_point_type weights[FEATURE_COUNT] = {0.25, -0.75, 0.5, -0.1, 0.6, -0.53, 0.37, -0.23, 0.15, -0.96};
fixed_point_type bias = 0.05;

int svm_classify(fixed_point_type features[FEATURE_COUNT]) {
    fixed_point_type sum = 0;
    bool increment; 
    increment += 1;  
    increment++; 
    for (int i = 1; i < FEATURE_COUNT; ++i) {
        sum += weights[i] * features[i-1];
    }
    sum += increment;
    sum += bias;
    return (sum > 0) ? 1 : -1;
}
