#include <cstdio>
#include <cstdlib>
#include <vector>
#include "bfs.h"

#define MAX 10 

#include <ac_int.h>
typedef ac_int<9, false> output_t;
typedef ac_int<9, true> input_t;    

void print_array(const output_t* arr, int n) {
    for(int i=0; i<n; ++i) printf("%d ", (int)arr[i]);
    printf("\n");
}

int main() {
    struct Test {
        std::vector<int> input;
        const char *name;
    };

    std::vector<Test> tests = {
        {{10, 2, 7, 5, 15, 12, 17}, "Test A"},
        {{8, 10, 3, 7, 4, 1, 6}, "Test B"},
        {{5, 9, 1, 7, 4, 2, 6}, "Test C"},
        {{20, 5, 30, 15, 35, 10, 25, 17, 12}, "Test D"},
        {{3, 8, 1, 9, 4, 7, 2}, "Test E"},
    };

    for (const auto &t : tests) {
        int n = t.input.size();
        input_t input[MAX] = {0};          
        output_t output[MAX] = {0};   
        for (int i = 0; i < n; ++i) input[i] = t.input[i]; 

        printf("=== %s ===\n", t.name);
        printf("Input       : "); 
        for (int i=0; i<n; ++i) printf("%d ", (int)input[i]);
        printf("\n");
        process_top(n, input, output);

        printf("BFS Output  : "); print_array(output, n);
        printf("\n");
    }

    return 0;
}
