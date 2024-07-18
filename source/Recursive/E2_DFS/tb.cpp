#include "main.cpp"
#include <stdio.h>
#include <stdlib.h>
#include <cstring> 

extern "C" {
void process_top(int n, int *input, int *output, int *fallback);
};


typedef struct {
    int n;              
    int input[8];       
    int expected[8];    
} TestCase;

int main(int argc, char** argv) {
    TestCase testCases[] = {
        {7, {4, 2, 6, 1, 3, 5, 7}, {1, 2, 3, 4, 5, 6, 7}},  
        {4, {10, 20, 5, 15}, {5, 10, 15, 20}},             
        {3, {5, 3, 8}, {3, 5, 8}},                         
        {7, {50, 30, 70, 20, 40, 60, 80}, {20, 30, 40, 50, 60, 70, 80}},  
        {5, {1, 3, 5, 7, 9}, {1, 3, 5, 7, 9}},             
        {5, {9, 7, 5, 3, 1}, {1, 3, 5, 7, 9}}             
        {7, {15, 5, 16, 3, 12, 20, 10}, {3, 5, 10, 12, 15, 16, 20}}  
    };
    int numCases = sizeof(testCases) / sizeof(TestCase);

for (int i = 0; i < numCases; i++) {
    int results[8] = {0};
    int fallback = 0;
    memset(results, 0, sizeof(results));
    fallback = 0;

        printf("Test Case %d: ", i+1);
    process_top(testCases[i].n, testCases[i].input, results, &fallback);

    if (fallback) {
        printf("Test Case %d: The kernel reports fallback.\n", i+1);
    } else {
        int passed = 1;
        for (int j = 0; j < testCases[i].n; j++) {
            if (results[j] != testCases[i].expected[j]) {
                passed = 0;
                break;
            }
        }

        if (passed) {
            printf("Test Case %d: Passed\n", i+1);
        } else {
            printf("Test Case %d: Failed\n", i+1);
            printf("Expected: ");
            for (int j = 0; j < testCases[i].n; j++) {
                printf("%d ", testCases[i].expected[j]);
            }
            printf("\nActual: ");
            for (int j = 0; j < testCases[i].n; j++) {
                printf("%d ", results[j]);
            }
            printf("\n");
        }
    }
}


    return 0;
}
