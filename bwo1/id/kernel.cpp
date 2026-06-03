#include <cmath>
#include <iostream>
#include <sstream>
#include <fstream>
#include <string>
#include "image.h"

void initializeImageData(SimpleImage& img, int width, int height) {
    img.width = width;
    img.height = height;
    for (int i = 0; i < height; ++i) {
        for (int j = 0; j < width; ++j) {
            img.data[i][j] = 0;
        }
    }
}

#pragma hls_design top
void denoiseImage(SimpleImage& img) {
    fixed_t edges[MAX_HEIGHT][MAX_WIDTH] = {0};
    int nonZeroCount = 0;
    int zeroCount = 0;
    fixed_t filter[3][3] = {
        {1, 1, 1},
        {1, 1, 1},
        {1, 1, 1}
    };
    fixed_t filterSum = 9;
    for (int y = 1; y < img.height - 1; y++) {
        for (int x = 1; x < img.width - 1; x++) {
            fixed_t sum = 0;
            for (int i = -1; i <= 1; i++) {
                for (int j = -1; j <= 1; j++) {
                    int ny = y + i;
                    int nx = x + j;
                    sum += img.data[ny][nx] * filter[i + 1][j + 1];
                }
            }
            edges[y][x] = sum / filterSum;
        }
    }
    for (int y = 0; y < img.height; y++) {
        for (int x = 0; x < img.width; x++) {
            img.data[y][x] = edges[y][x];
            if (edges[y][x] != 0)
                nonZeroCount++;
            else
                zeroCount++;
        }
    }
    std::cout << "Non-zero Pixels: " << nonZeroCount << std::endl;
    std::cout << "Zero Pixels: " << zeroCount << std::endl;
}
