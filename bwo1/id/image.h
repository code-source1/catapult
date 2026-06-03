#ifndef SIMPLE_IMAGE_H
#define SIMPLE_IMAGE_H
#include <ac_fixed.h>
#include <vector>

#define MAX_WIDTH 15
#define MAX_HEIGHT 15
typedef ac_fixed<22, 20, true> fixed_t;
struct SimpleImage {
    int width;
    int height;
    fixed_t data[MAX_HEIGHT][MAX_WIDTH];
};
void initializeImageData(SimpleImage& img, int width, int height);
void denoiseImage(SimpleImage& img);
#endif
