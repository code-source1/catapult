#include <cstdio>
#include <cstdlib>
#include <vector>
#include "bfs.cpp" 

void print_array(const int* arr, int n) {
    for(int i=0; i<n; ++i) printf("%d ", arr[i]);
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
        int *input = (int*)malloc(sizeof(int)*n);
        int *output = (int*)malloc(sizeof(int)*n);
        for (int i = 0; i < n; ++i) input[i] = t.input[i];
        int fallback = 0;

        printf("=== %s ===\n", t.name);
        printf("Input       : "); print_array(input, n);
        process_top(n, input, output, &fallback);
        printf("BFS Output  : "); print_array(output, n);
        printf("Fallback    : %d\n\n", fallback);

        free(input);
        free(output);
    }

    return 0;
}
