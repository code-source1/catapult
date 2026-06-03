#include "bubble.h"
#include <ac_int.h>

typedef ac_int<8, false> N_TYPE;  

void swap(N_TYPE arr[], int i, int j)
{
    N_TYPE temp;
    if (i == j)
    {
        return;
    }
    temp = arr[i];
    arr[i] = arr[j];
    arr[j] = temp;
}

#pragma hls_design top
void bubbleSort(N_TYPE num[K])
{
    int i, j, q;
    N_TYPE num_l[K];

    for (q = 0; q < K; q++)
    {
        num_l[q] = num[q];
    }

    for (i = 0; i < K - 1; i++)
    {
        for (j = 0; j < K - 1 - i; j++)
        {
            if (num_l[j] > num_l[j + 1])
            {
                swap(num_l, j, j + 1);
            }
        }
    }

    for (q = 0; q < K; q++)
    {
        num[q] = num_l[q];
    }
    return;
}