#include "main.cpp"
#include "bubble.h"
#include <stdio.h>
#include <stdlib.h>
#include <ac_int.h>

int main()
{
    N_TYPE array[K] = {10, 2, 56, 12, 11, 1, 90, 34, 75, 4};
    printf("Original array:\n");
    for (int i = 0; i < K; i++)
    {
        printf("%d ", (int)array[i]);
    }
    printf("\n");

    bubbleSort(array);

    printf("Sorted array:\n");
    for (int i = 0; i < K; i++)
    {
        printf("%d ", (int)array[i]);
    }
    printf("\n");

    return 0;
}
