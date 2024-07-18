#include <iostream>

#define MAX_N 1000
#define n 12

#pragma hls_design top
int trap(const int* height) {
    if (n == 0) {
        return 0;
    }

    int leftMax[MAX_N];
    int rightMax[MAX_N];

    const int* ptr = height; 
    int* lMax = leftMax; 
    int* rMax = rightMax + n - 1; 

    *lMax = *ptr; 
    for (const int* end = height + n; ++ptr != end; ++lMax) {
        *(lMax + 1) = std::max(*lMax, *ptr);
    }

    ptr = height + n - 1; 
    *rMax = *ptr; 
    for (const int* start = height - 1; ptr-- != start; --rMax) {
        *(rMax - 1) = std::max(*(rMax), *ptr);
    }

    int ans = 0;
    lMax = leftMax; 
    rMax = rightMax; 
    ptr = height; 
    for (int i = 0; i < n; i++, lMax++, rMax++, ptr++) {
        ans += std::min(*lMax, *rMax) - *ptr;
    }

    return ans;
}
