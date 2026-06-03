#ifndef FILTER_H
#define FILTER_H
#include <ac_fixed.h>
#include <iostream>
#include <fstream>
#include <sstream>
#include <cstdlib>

typedef ac_fixed<12,10,true> real_t;
#define MAX_SIZE 128
void bubbleSortAndTransform(int n, const real_t input[MAX_SIZE], real_t output[MAX_SIZE]);
#endif
