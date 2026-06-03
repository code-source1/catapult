#include <ac_fixed.h>
#include <iostream>
#include "image.h"
#include <cmath>

typedef ac_fixed<22,20,true> fixed_t;

fixed_t sqrt_fixed(fixed_t x) {
    if (x <= 0) {
        return 0;
    }
    fixed_t r = x;
    for (int i = 0; i < 10; i++) {
        r = (r + x / r) / 2;
    }
    return r;
}

#pragma hls_design top
void detectEdges(SimpleImage& img) {
    int sobelX[3][3] = {
        {-1,  0,  1},
        {-2,  0,  2},
        {-1,  0,  1}
    };
    int sobelY[3][3] = {
        {-1, -2, -1},
        { 0,  0,  0},
        { 1,  2,  1}
    };
    fixed_t magnitude[MAX_HEIGHT][MAX_WIDTH] = {0};
    for (int y = 1; y < img.height - 1; y++) {
        for (int x = 1; x < img.width - 1; x++) {
            fixed_t gx = 0;
            fixed_t gy = 0;
            for (int i = -1; i <= 1; i++) {
                for (int j = -1; j <= 1; j++) {
                    int ny = y + i;
                    int nx = x + j;
                    gx += img.data[ny][nx] * sobelX[i + 1][j + 1];
                    gy += img.data[ny][nx] * sobelY[i + 1][j + 1];
                }
            }
            fixed_t sum_fixed = (gx * gx) + (gy * gy);
            magnitude[y][x] = sqrt_fixed(sum_fixed);
        }
    }
    for (int y = 1; y < img.height - 1; y++) {
        for (int x = 1; x < img.width - 1; x++) {
            img.data[y][x] = magnitude[y][x];
        }
    }
    int nonZeroCount = 0;
    int zeroCount = 0;
    for (int y = 0; y < img.height; y++) {
        for (int x = 0; x < img.width; x++) {
            if (img.data[y][x] != 0)
                nonZeroCount++;
            else
                zeroCount++;
        }
    }
    std::cout << "Non-zero Pixels: " << nonZeroCount << std::endl;
    std::cout << "Zero Pixels: " << zeroCount << std::endl;
}
