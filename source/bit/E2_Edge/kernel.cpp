#include <cmath>
#include <iostream>
#include "image.h"

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

    float magnitude[MAX_HEIGHT][MAX_WIDTH] = {0.0f};

    for (int y = 1; y < img.height - 1; y++) {
        for (int x = 1; x < img.width - 1; x++) {
            float gx = 0.0f;
            float gy = 0.0f;
            for (int i = -1; i <= 1; i++) {
                for (int j = -1; j <= 1; j++) {
                    int ny = y + i;
                    int nx = x + j;
                    gx += img.data[ny][nx] * sobelX[i + 1][j + 1];
                    gy += img.data[ny][nx] * sobelY[i + 1][j + 1];
                }
            }
            magnitude[y][x] = std::sqrt(gx * gx + gy * gy);
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
            if (img.data[y][x] != 0.0f)
                nonZeroCount++;
            else
                zeroCount++;
        }
    }
    std::cout << "Non-zero Pixels: " << nonZeroCount << std::endl;
    std::cout << "Zero Pixels: " << zeroCount << std::endl;
}
