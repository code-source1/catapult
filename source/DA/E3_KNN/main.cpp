#include <iostream>
#include <ac_fixed.h>

typedef ac_fixed<16, 8, false> fixed_point;

fixed_point my_abs(fixed_point x) {
    fixed_point negative_x = -x;
    return (x < 0) ? negative_x : x;
}

#pragma hls_design top
void knn(fixed_point query_x, fixed_point query_y, fixed_point *data_x, fixed_point *data_y, int n, int k, int label) {
    fixed_point *distances = new fixed_point[n];
    int labels [n]; 

    for (int i = 0; i < n; i++) {
        labels[i] = i % 2; 
    }


    for (int i = 0; i < n; i++) {
        distances[i] = my_abs(data_x[i] - query_x) + my_abs(data_y[i] - query_y);
    }

    for (int i = 0; i < k; i++) {
        for (int j = i + 1; j < n; j++) {
            if (distances[j] < distances[i]) {
                fixed_point temp = distances[i];
                distances[i] = distances[j];
                distances[j] = temp;
                int temp_label = labels[i];
                labels[i] = labels[j];
                labels[j] = temp_label;
            }
        }
    }

    int count_0 = 0, count_1 = 0;
    for (int i = 0; i < k; i++) {
        if (labels[i] == 0) {
            count_0++;
        } else {
            count_1++;
        }
    }

    label = (count_0 > count_1) ? 0 : 1;

    delete[] distances;
    delete[] labels;
}

