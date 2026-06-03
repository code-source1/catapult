// kernel.cpp
#include <fstream>
#include <iostream>
#include <sstream>
#include <string>
using namespace std;


typedef double DataType;

const int MOD = 1000000007; // Modulus for result normalization
const int MAX_INPUTS = 10;  // Maximum input count
const int MAX_NODES = 10;   // Maximum nodes per layer
const int MAX_LAYERS = 5;   // Maximum layers


DataType relu(DataType x) {
    return (x > 0) ? x : 0;
}


void computeLayer(DataType inputs[MAX_INPUTS],
                  DataType weights[MAX_NODES][MAX_INPUTS],
                  DataType biases[MAX_NODES],
                  DataType outputs[MAX_NODES],
                  DataType accumu[MAX_NODES],
                  DataType bias[MAX_NODES],
                  DataType act[MAX_NODES],
                  int num_inputs,
                  int num_nodes) {
    for (int i = 0; i < num_nodes; ++i) {
        DataType acc = 0;
        for (int j = 0; j < num_inputs; ++j) {
            acc += inputs[j] * weights[i][j];
        }
        accumu[i] = acc;
        acc += biases[i];
        bias[i] = acc;
        act[i] = relu(acc);
        outputs[i] = act[i];
    }
}

void loadWeights(DataType weights[MAX_LAYERS][MAX_NODES][MAX_INPUTS],
                 int num_layers,
                 int nodes_in[MAX_LAYERS],
                 int nodes_out[MAX_LAYERS]) {
    const char* filename = "/nas/ei/share/TUEIEDAscratch/ge86pak/hls/bwo1/dnn/c/w.dat";
    ifstream file(filename);
    if (!file.is_open()) {
        cerr << "Error: Unable to open " << filename << endl;
        return;
    }
    file >> num_layers; 
    for (int l = 0; l < num_layers; ++l) {
        file >> nodes_in[l] >> nodes_out[l];
        for (int i = 0; i < nodes_out[l]; ++i) {
            for (int j = 0; j < nodes_in[l]; ++j) {
                double tmp;
                file >> tmp;
                weights[l][i][j] = tmp;
            }
        }
    }
    file.close();
}


void loadBiases(DataType biases[MAX_LAYERS][MAX_NODES],
                int num_layers,
                int nodes_out[MAX_LAYERS]) {
    const char* filename = "/nas/ei/share/TUEIEDAscratch/ge86pak/hls/bwo1/dnn/c/a.dat";
    ifstream file(filename);
    if (!file.is_open()) {
        cerr << "Error: Unable to open " << filename << endl;
        return;
    }
    file >> num_layers;
    for (int l = 0; l < num_layers; ++l) {
        file >> nodes_out[l];
        for (int i = 0; i < nodes_out[l]; ++i) {
            double tmp;
            file >> tmp;
            biases[l][i] = tmp;
        }
    }
    file.close();
}


void dnn(DataType inputs[MAX_INPUTS],
         DataType weights[MAX_LAYERS][MAX_NODES][MAX_INPUTS],
         DataType biases[MAX_LAYERS][MAX_NODES],
         DataType accumu_outputs[MAX_LAYERS][MAX_NODES],
         DataType bias_outputs[MAX_LAYERS][MAX_NODES],
         DataType act_outputs[MAX_LAYERS][MAX_NODES],
         int num_layers,
         int nodes_in[MAX_LAYERS],
         int nodes_out[MAX_LAYERS]) {

    DataType layer_input[MAX_INPUTS];
    DataType layer_output[MAX_NODES];


    for (int i = 0; i < MAX_INPUTS; ++i) {
        layer_input[i] = inputs[i];
    }

    for (int l = 0; l < num_layers; ++l) {
        computeLayer(layer_input, weights[l], biases[l], layer_output,
                     accumu_outputs[l], bias_outputs[l], act_outputs[l],
                     nodes_in[l], nodes_out[l]);


        for (int i = 0; i < nodes_out[l]; ++i) {
            layer_input[i] = layer_output[i];
        }
    }
}
