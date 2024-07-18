#include "main.cpp"
#include <algorithm>  
#include <cstring>
#include <iostream>

extern int arr[];
extern int reverseKGroup(int n, int k);

void printArray(int n) {
    for (int i = 0; i < n; i++) {
        std::cout << arr[i] << " ";
    }
    std::cout << std::endl;
}

int main() {
    int test1[5] = {1, 2, 3, 4, 5};
    std::copy(test1, test1 + 5, arr);
    int changes1 = reverseKGroup(5, 2);
    std::cout << "Changes made for test case 1: " << changes1 << std::endl;
    printArray(5);

    int test2[5] = {1, 2, 3, 4, 5};
    std::copy(test2, test2 + 5, arr);
    int changes2 = reverseKGroup(5, 3);
    std::cout << "Changes made for test case 2: " << changes2 << std::endl;
    printArray(5);

    return 0;
}
