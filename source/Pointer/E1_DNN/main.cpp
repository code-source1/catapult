#include <iostream>
#include <cmath>

const int inputSize = 14;
const int hiddenSize = 20;
const int outputSize = 10;

int** weights_ih;
int** weights_ho;
int* bias_h;
int* bias_o;

int relu(int x) {
    return x > 0 ? x : 0;
}

void initialize_network() {
    weights_ih = new int*[inputSize];
    int weights_ih_data[inputSize][hiddenSize] = {
        {2, -3, 4, 1, 2, -3, 4, 1, 1, 2, -1, 1, 1, 2, -1, 1, 1, 2, -1, 1},
        {1, 2, -1, 1, -3, 4, 1, 2, -3, 4, 1, 1, 2, -1, 1, 1, 2, -1, 1, -5},
        {-1, 1, 2, -2, 2, -1, 1, -3, 4, 1, 2, -3, 4, 1, 1, 2, -1, 1, 1, 2},
        {1, 2, -1, 1, -3, 4, 1, 2, -3, 4, 1, 1, 2, -1, 1, 1, 2, -1, 1, -5},
        {2, -3, 4, 1, 2, -3, 4, 1, 1, 2, -1, 1, 1, 2, -1, 1, 1, 2, -1, 1},
        {2, -3, 4, 1, 2, -3, 4, 1, 1, 2, -1, 1, 1, 2, -1, 1, 1, 2, -1, 1},
        {1, 2, -1, 1, -3, 4, 1, 2, -3, 4, 1, 1, 2, -1, 1, 1, 2, -1, 1, -5},
        {2, -3, 4, 1, 2, -3, 4, 1, 1, 2, -1, 1, 1, 2, -1, 1, 1, 2, -1, 1},
        {2, -3, 4, 1, 2, -3, 4, 1, 1, 2, -1, 1, 1, 2, -1, 1, 1, 2, -1, 1},
        {2, -3, 4, 1, 2, -3, 4, 1, 1, 2, -1, 1, 1, 2, -1, 1, 1, 2, -1, 1},
        {2, -3, 4, 1, 2, -3, 4, 1, 1, 2, -1, 1, 1, 2, -1, 1, 1, 2, -1, 1},
        {2, -3, 4, 1, 2, -3, 4, 1, 1, 2, -1, 1, 1, 2, -1, 1, 1, 2, -1, 1},
        {2, -3, 4, 1, 2, -3, 4, 1, 1, 2, -1, 1, 1, 2, -1, 1, 1, 2, -1, 1},
        {2, -3, 4, 1, 2, -3, 4, 1, 1, 2, -1, 1, 1, 2, -1, 1, 1, 2, -1, 1}
    };
    for (int i = 0; i < inputSize; i++) {
        weights_ih[i] = new int[hiddenSize];
        for (int j = 0; j < hiddenSize; j++) {
            weights_ih[i][j] = weights_ih_data[i][j];
        }
    }

    weights_ho = new int*[hiddenSize];
    int weights_ho_data[hiddenSize][outputSize] = {
        {2, -3, 4, 1, 2, -3, 4, 1, 1, 2},
        {1, 2, -1, 1, -3, 4, 1, 2, -3, 4},
        {-1, 1, 2, -2, 2, -1, 1, -3, 4, 2},
        {1, 2, -1, 1, -3, 4, 1, 2, -3, 1},
        {2, -3, 4, 1, 2, -3, 4, 1, 1, 2},
        {1, 2, -1, 1, -3, 4, 1, 2, -3, 4},
        {-1, 1, 2, -2, 2, -1, 1, -3, 4, 2},
        {1, 2, -1, 1, -3, 4, 1, 2, -3, 1},
        {2, -3, 4, 1, 2, -3, 4, 1, 1, 2},
        {1, 2, -1, 1, -3, 4, 1, 2, -3, 4},
        {-1, 1, 2, -2, 2, -1, 1, -3, 4, 2},
        {1, 2, -1, 1, -3, 4, 1, 2, -3, 1},
        {2, -3, 4, 1, 2, -3, 4, 1, 1, 2},
        {1, 2, -1, 1, -3, 4, 1, 2, -3, 4},
        {-1, 1, 2, -2, 2, -1, 1, -3, 4, 2},
        {1, 2, -1, 1, -3, 4, 1, 2, -3, 1},
        {2, -3, 4, 1, 2, -3, 4, 1, 1, 2},
        {1, 2, -1, 1, -3, 4, 1, 2, -3, 4},
        {-1, 1, 2, -2, 2, -1, 1, -3, 4, 2},
        {1, 2, -1, 1, -3, 4, 1, 2, -3, 1} 
    };
    for (int i = 0; i < hiddenSize; i++) {
        weights_ho[i] = new int[outputSize];
        for (int j = 0; j < outputSize; j++) {
            weights_ho[i][j] = weights_ho_data[i][j];
        }
    }


    bias_h = new int[hiddenSize] {2, -3, 4, 1, 2, -3, 4, 1, 1, 2, -1, 1, 1, 2, -1, 1, 1, 2, -1, 1};
    bias_o = new int[outputSize] {1, 2, -1, 1, -3, 4, 1, 2, -3, 1};
}

#pragma hls_design top
void forward(int input[inputSize], int output[outputSize]) {
    int* hidden = new int[hiddenSize];

    for (int i = 0; i < hiddenSize; i++) {
        hidden[i] = bias_h[i];
        for (int j = 0; j < inputSize; j++) {
            hidden[i] += input[j] * weights_ih[j][i];
        }
        hidden[i] = relu(hidden[i]);
    }

    for (int i = 0; i < outputSize; i++) {
        output[i] = bias_o[i];
        for (int j = 0; j < hiddenSize; j++) {
            output[i] += hidden[j] * weights_ho[j][i];
        }
        output[i] = relu(output[i]);
    }
    delete[] hidden;
}