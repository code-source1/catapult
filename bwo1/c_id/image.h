#ifndef SIMPLE_IMAGE_H
#define SIMPLE_IMAGE_H

#include <vector>  // 此处虽然没有用到 STL，但保留也无妨

#define MAX_WIDTH 15
#define MAX_HEIGHT 15

struct SimpleImage {
    int width;
    int height;
    float data[MAX_HEIGHT][MAX_WIDTH]; 
};

void initializeImageData(SimpleImage& img, int width, int height);
void denoiseImage(SimpleImage& img);

#endif
