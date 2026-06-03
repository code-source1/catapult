#ifndef FILTER_H
#define FILTER_H

#include <vector>
#include <string>
#include <iostream>
#include <fstream>
#include <sstream>
#include <cstdlib>


typedef double real_t;


constexpr int MAX_SIZE = 1024;


void bubbleSortAndTransform(int n, const real_t input[], real_t output[]);

#endif // FILTER_H
