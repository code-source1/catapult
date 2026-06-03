#ifndef SIMPLE_IMAGE_H
#define SIMPLE_IMAGE_H

#include <vector>


const int MAX_WIDTH = 11;
const int MAX_HEIGHT = 6;

struct SimpleImage {
    int width;
    int height;

    float data[MAX_HEIGHT][MAX_WIDTH];
};


void initializeImageData(SimpleImage& img, int width, int height);
void detectEdges(SimpleImage& img);
int recursiveFunction(int depth);

#endif // SIMPLE_IMAGE_H
