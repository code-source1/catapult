#include <algorithm>
#include <ac_int.h>

class Solution {
private:
    typedef ac_int<32, false> width1;  // 32-bit unsigned integer
    typedef ac_int<16, false> width2;  // 16-bit unsigned integer
    typedef ac_int<8, false> width3;   // 8-bit unsigned integer

    static const width1 mod;           // Modulus for result normalization

public:
    static const int MAX_SIZE = 50;    // Maximum size of the arrays

    // Inline max function to replace std::max
    static inline width1 max(width1 a, width1 b) {
        return (a > b) ? a : b;
    }

    #pragma hls_design top
    width1 maxSum(width2 nums1[MAX_SIZE], width3 size1, width2 nums2[MAX_SIZE], width3 size2) {
        #pragma HLS PIPELINE II=1
        width1 best1 = 0, best2 = 0;
        width3 i = 0, j = 0;

        while (i < size1 || j < size2) {
            #pragma HLS LOOP_TRIPCOUNT min=1 max=MAX_SIZE
            if (i < size1 && j < size2) {
                if (nums1[i] < nums2[j]) {
                    best1 += nums1[i];
                    ++i;
                } else if (nums1[i] > nums2[j]) {
                    best2 += nums2[j];
                    ++j;
                } else {
                    width1 best = max(best1, best2) + nums1[i];
                    best1 = best2 = best;
                    ++i;
                    ++j;
                }
            } else if (i < size1) {
                best1 += nums1[i];
                ++i;
            } else if (j < size2) {
                best2 += nums2[j];
                ++j;
            }
        }

        return max(best1, best2) % mod;
    }
};

// Definition of the static member 'mod'.
const Solution::width1 Solution::mod = 1000000007;
