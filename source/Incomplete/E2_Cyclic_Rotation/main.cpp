#include <algorithm>
#include "ac_int.h"  

#define MAX_M 10  
#define MAX_N 10  
#define MAX_PERIMETER (2*(MAX_M + MAX_N - 2))  

class Solution {
public:
    int grid[MAX_M][MAX_N];
    int m, n;

    #pragma hls_design top
    void rotateGrid(int k, ac_int<2, false> rotation_direction) {
        int nlayer = std::min(m / 2, n / 2);

        int temp[MAX_PERIMETER], r[MAX_PERIMETER], c[MAX_PERIMETER];

        for (int layer = 0; layer < nlayer; ++layer) {
            int idx = 0;


            for (int i = layer; i < m - layer - 1; ++i) {
                r[idx] = i;
                c[idx] = layer;
                temp[idx++] = grid[i][layer];
            }
            for (int j = layer; j < n - layer - 1; ++j) {
                r[idx] = m - layer - 1;
                c[idx] = j;
                temp[idx++] = grid[m - layer - 1][j];
            }
            for (int i = m - layer - 1; i > layer; --i) {
                r[idx] = i;
                c[idx] = n - layer - 1;
                temp[idx++] = grid[i][n - layer - 1];
            }
            for (int j = n - layer - 1; j > layer; --j) {
                r[idx] = layer;
                c[idx] = j;
                temp[idx++] = grid[layer][j];
            }

            int total = idx;  

            switch (rotation_direction) {
            case 0:  
                for (int i = 0; i < total; ++i) {
                    int new_idx = i - k;
                    while (new_idx < 0) new_idx += total;
                    grid[r[new_idx]][c[new_idx]] = temp[i];
                }
                break;
            case 1:  
                for (int i = 0; i < total; ++i) {
                    int new_idx = i + k;
                    while (new_idx >= total) new_idx -= total;
                    grid[r[new_idx]][c[new_idx]] = temp[i];
                }
                break;
            case 2:  
            case 3:  
            }
        }
    }

    void setInput(int input[MAX_M][MAX_N], int input_m, int input_n) {
        m = input_m;
        n = input_n;
        for (int i = 0; i < m; ++i) {
            for (int j = 0; j < n; ++j) {
                grid[i][j] = input[i][j];
            }
        }
    }
};
