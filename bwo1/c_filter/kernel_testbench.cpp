#include "filter.h"
#include <fstream>
#include <sstream>
#include <iostream>
#include <vector>
#include <string>
#include <cstdlib>
#include <iomanip>

using namespace std;


const string INPUT_FILE_PATH = ".../bwo1/c_filter/1.dat";
const string OUTPUT_DIR = ".../bwo1/c_filter/p";

int main() {
    ifstream inputFile(INPUT_FILE_PATH.c_str());
    if (!inputFile.is_open()) {
        cerr << "Error opening input file: " << INPUT_FILE_PATH << endl;
        return 1;
    }
    

    vector<vector<real_t>> testCases;
    string line;
    while (getline(inputFile, line)) {
        if (line.empty())
            continue;
        istringstream iss(line);
        vector<real_t> numbers;
        real_t val;
        while (iss >> val) {
            numbers.push_back(val);
        }

        if (numbers.size() >= 4)
            testCases.push_back(numbers);
    }
    inputFile.close();
    
    string outputFilePath = OUTPUT_DIR + "/act_3.txt";
    ofstream outputFile(outputFilePath.c_str());
    if (!outputFile.is_open()) {
        cerr << "Error opening output file: " << outputFilePath << endl;
        return 1;
    }
    

    for (size_t t = 0; t < testCases.size(); t++) {
        vector<real_t>& testCase = testCases[t];
        int n = testCase.size();
        int effective_n = (n % 2 == 0) ? n : n - 1;
        real_t input_array[MAX_SIZE];
        for (int i = 0; i < effective_n; i++) {
            input_array[i] = testCase[i];
        }
        real_t output_array[MAX_SIZE];
        bubbleSortAndTransform(effective_n, input_array, output_array);
        int diffCount = (effective_n / 2) - 1;
        for (int i = 0; i < diffCount; i++) {
            outputFile << output_array[i];
            if (i < diffCount - 1)
                outputFile << " ";
        }
        outputFile << "\n";
    }
    
    outputFile.close();
    return 0;
}
