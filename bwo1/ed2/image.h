#ifndef SIMPLE_IMAGE_H
#define SIMPLE_IMAGE_H
#include <ac_fixed.h>
#include <ac_math.h>

typedef ac_fixed<22,20,true> fixed_t;
const int MAX_WIDTH = 11;
const int MAX_HEIGHT = 6;
struct SimpleImage {
    int width;
    int height;
    fixed_t data[MAX_HEIGHT][MAX_WIDTH];
};
void initializeImageData(SimpleImage& img, int width, int height);
void detectEdges(SimpleImage& img);
int recursiveFunction(int depth);
#endif
