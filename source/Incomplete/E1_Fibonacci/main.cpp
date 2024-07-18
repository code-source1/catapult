#include <iostream>
#include <algorithm>
#include "ac_int.h"

#define MAX_N 10  

class Solution {
public:
    int arr[MAX_N];
    int indices[MAX_N];
    int dp[MAX_N][MAX_N];
    
    #pragma hls_design top
    int FibSubseq(int n, ac_int<1, false> computeMode) {
        for (int i = 0; i < n; ++i) {
            indices[i] = -1;  // Initialize indices mapping to -1
        }
        for (int i = 0; i < n; ++i) {
            indices[arr[i]] = i;
        }

        int ans = 0;
        for (int i = 0; i < n; ++i) {
            for (int j = 0; j < i; ++j) {
                dp[j][i] = 0;  
                int k = -1;
                if (arr[i] - arr[j] < arr[j] && indices[arr[i] - arr[j]] != -1) {
                    k = indices[arr[i] - arr[j]];
                    switch (computeMode) {
                        case 0:
                            dp[j][i] = (dp[k][j] > 0) ? dp[k][j] + 1 : 3;
                            break;
                        case 1:
                    }
                }
                ans = std::max(ans, dp[j][i]);
            }
        }
        return (ans >= 3 ? ans : 0);  
    }
};


