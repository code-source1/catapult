#include <ac_fixed.h>

#define MAX_DEPTH 30  // 定义数组最大深度为 70

// 定点数类型：总宽度22位，整数部分12位，带符号
typedef ac_fixed<22,12,true> fixed_t;

// HLS 顶层函数：贪婪算法
#pragma hls_design top
void ga(const fixed_t nums1[MAX_DEPTH], const fixed_t nums2[MAX_DEPTH],
        int size1, int size2,
        fixed_t out[MAX_DEPTH], int *out_size) {
    int i = 0, j = 0, k = 0;
    while (i < size1 || j < size2) {
        if (i < size1 && j < size2) {
            if (nums1[i] < nums2[j]) {
                out[k++] = nums1[i];
                i++;
            } else if (nums1[i] > nums2[j]) {
                out[k++] = nums2[j];
                j++;
            } else {
                // 当两个值相等时，将其视为公共节点，加入结果，并同时前进
                out[k++] = nums1[i];
                i++;
                j++;
            }
        } else if (i < size1) {
            out[k++] = nums1[i];
            i++;
        } else if (j < size2) {
            out[k++] = nums2[j];
            j++;
        }
    }
    *out_size = k;
}
