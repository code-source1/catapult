#include "filter.h"
#include <iostream>
#include <stdexcept>

static void swap(real_t array[], int i, int j) {
    real_t temp = array[i];
    array[i] = array[j];
    array[j] = temp;
}

#pragma hls_design top
void bubbleSortAndTransform(int n, const real_t input[MAX_SIZE], real_t output[MAX_SIZE]) {
    real_t sorted[MAX_SIZE];
    if (n > MAX_SIZE) {
        std::cerr << "Error: n exceeds MAX_SIZE." << std::endl;
        return;
    }
    for (int i = 0; i < n; i++) {
        sorted[i] = input[i];
    }
    for (int i = 0; i < n - 1; i++) {
        for (int j = 0; j < n - 1 - i; j++) {
            if (sorted[j] > sorted[j + 1]) {
                swap(sorted, j, j + 1);
            }
        }
    }
    int effective_n = (n % 2 == 0) ? n : n - 1;
    int numPairs = effective_n / 2;
    if (numPairs < 2) {
        return;
    }
    real_t products[MAX_SIZE/2];
    for (int i = 0; i < numPairs; i++) {
        products[i] = sorted[2*i] * sorted[2*i+1];
    }
    for (int i = 0; i < numPairs - 1; i++) {
        output[i] = products[i+1] - products[i];
    }
}
