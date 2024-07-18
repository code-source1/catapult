
#include <algorithm>
#include <iostream>

#define MAX_SIZE 10

int arr[MAX_SIZE];

void myReverse(int start, int end) {
    if (start >= end) {
        return;
    }
    std::swap(arr[start], arr[end]); 
    myReverse(start + 1, end - 1); 
}

#pragma hls_design top
int reverseKGroup(int n, int k) {
    int changes = 0;
    for (int i = 0; i < n; i += k) {
        int end = std::min(i + k - 1, n - 1);
        if (end - i + 1 == k) {
            myReverse(i, end);
            changes++;
        }
    }
    return changes;
}
