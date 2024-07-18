#include <iostream>
#include <ac_fixed.h>

typedef ac_fixed<16, 8, false> fixed_point;

void knn(fixed_point query_x, fixed_point query_y, fixed_point *data_x, fixed_point *data_y, int n, int k, int &label);

int main() {
    fixed_point data_x[10] = {1.0, 2.0, 3.0, 4.5, 5.5, 6.5, 7.0, 8.0, 9.0, 10.0};
    fixed_point data_y[10] = {1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0, 5.5};
    fixed_point query_x = 5.0;
    fixed_point query_y = 5.0;
    int n = 10;
    int k = 3;
    int label;

    knn(query_x, query_y, data_x, data_y, n, k, label);

    std::cout << "Test Label: " << label << std::endl;
    return 0;
}
