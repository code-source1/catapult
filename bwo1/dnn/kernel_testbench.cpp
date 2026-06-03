#include <ac_int.h>
#include <fstream>
#include <iostream>
#include <sstream>
#include <string>
#include <ac_fixed.h>

using namespace std;
typedef ac_fixed<17, 10, true> DataType;
const int MOD = 1000000007;
const int MAX_INPUTS = 10;
const int MAX_NODES = 10;
const int MAX_LAYERS = 5;
const string INPUT_FILE_PATH = ".../bwo1/dnn/1.dat";
const string OUTPUT_DIR = ".../bwo1/dnn/p";
void loadWeights(DataType weights[MAX_LAYERS][MAX_NODES][MAX_INPUTS],
                 int num_layers,
                 int nodes_in[MAX_LAYERS],
                 int nodes_out[MAX_LAYERS]);
void loadBiases(DataType biases[MAX_LAYERS][MAX_NODES],
                int num_layers,
                int nodes_out[MAX_LAYERS]);
void dnn(DataType inputs[MAX_INPUTS],
         DataType weights[MAX_LAYERS][MAX_NODES][MAX_INPUTS],
         DataType biases[MAX_LAYERS][MAX_NODES],
         DataType accumu_outputs[MAX_LAYERS][MAX_NODES],
         DataType bias_outputs[MAX_LAYERS][MAX_NODES],
         DataType act_outputs[MAX_LAYERS][MAX_NODES],
         int num_layers,
         int nodes_in[MAX_LAYERS],
         int nodes_out[MAX_LAYERS]);
void saveLayerOutputs(DataType layer_outputs[MAX_LAYERS][MAX_NODES],
                      int num_layers,
                      int nodes_out[MAX_LAYERS],
                      const char* prefix,
                      const char* output_dir) {
    for (int l = 0; l < num_layers; ++l) {
        string filename = string(output_dir) + "/" + prefix + to_string(l + 1) + ".txt";
        ofstream file(filename);
        if (!file.is_open()) {
            printf("Error: Unable to open %s\n", filename.c_str());
            continue;
        }
        for (int i = 0; i < nodes_out[l]; ++i) {
            file << layer_outputs[l][i] << " ";
        }
        file << "\n";
        file.close();
    }
}

int main() {
    ifstream input_file(INPUT_FILE_PATH.c_str());
    if (!input_file.is_open()) {
        cerr << "Error: Unable to open input file." << endl;
        return 1;
    }
    string line;
    DataType testCases[10][MAX_INPUTS];
    int numTestCases = 0;
    while (getline(input_file, line) && numTestCases < 10) {
        istringstream iss(line);
        int n, idx = 0;
        while (iss >> n && idx < MAX_INPUTS) {
            testCases[numTestCases][idx++] = n;
            if (iss.peek() == ',')
                iss.ignore();
        }
        numTestCases++;
    }
    input_file.close();
    DataType weights[MAX_LAYERS][MAX_NODES][MAX_INPUTS];
    DataType biases[MAX_LAYERS][MAX_NODES];
    DataType accumu_outputs[MAX_LAYERS][MAX_NODES];
    DataType bias_outputs[MAX_LAYERS][MAX_NODES];
    DataType act_outputs[MAX_LAYERS][MAX_NODES];
    int num_layers = 3;
    int nodes_in[MAX_LAYERS] = {5, 8, 9};
    int nodes_out[MAX_LAYERS] = {8, 9, 6};
    loadWeights(weights, num_layers, nodes_in, nodes_out);
    loadBiases(biases, num_layers, nodes_out);
    for (int i = 0; i < numTestCases; ++i) {
        dnn(testCases[i], weights, biases, accumu_outputs, bias_outputs, act_outputs,
            num_layers, nodes_in, nodes_out);
        saveLayerOutputs(accumu_outputs, num_layers, nodes_out, "accumu_", OUTPUT_DIR.c_str());
        saveLayerOutputs(bias_outputs, num_layers, nodes_out, "bias_", OUTPUT_DIR.c_str());
        saveLayerOutputs(act_outputs, num_layers, nodes_out, "act_", OUTPUT_DIR.c_str());
    }
    return 0;
}
