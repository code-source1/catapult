#include <iostream>


void printArray(const char* name, int array[], int size) {
    std::cout << name << ": ";
    for (int i = 0; i < size; i++) {
        std::cout << array[i] << " ";
    }
    std::cout << std::endl;
}

int main() {
    int input[inputSize] = {2, -3, 4, 1, 2, -3, 4, 1, 1, 2, -1, 1, 1, -5}; 
    int output[outputSize];

    forward(input, output);

    printArray("Input", input, inputSize);
    printArray("Output", output, outputSize);

    return 0;
}
