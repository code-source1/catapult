#include <fstream>
#include <sstream>
#include <iostream>
#include <vector>
#include <string>
#include <cstdlib>
#include <iomanip>


typedef double size1_t;
typedef double size2_t;
typedef double result_t;

extern std::vector<result_t> ga(const double nums1[], const double nums2[], size1_t size1, size2_t size2);


const std::string INPUT_FILE_PATH = "/nas/ei/share/TUEIEDAscratch/ge86pak/hls/bwo1/c_ga/1.dat";
const std::string OUTPUT_DIR = "/nas/ei/share/TUEIEDAscratch/ge86pak/hls/bwo1/c_ga/p";

int main() {
    std::ifstream inputFile(INPUT_FILE_PATH);
    if (!inputFile.is_open()) {
        std::cerr << "Error opening input file: " << INPUT_FILE_PATH << std::endl;
        return 1;
    }
    
    const size_t expectedCols = 14;
    const size_t halfCols = expectedCols / 2;   
    std::vector<std::pair<std::vector<double>, std::vector<double>>> testCases;
    std::string line;
    while (std::getline(inputFile, line)) {
        if (line.empty()) continue; 
        std::istringstream iss(line);
        std::vector<double> rowValues;
        double val;
        while (iss >> val) {
            rowValues.push_back(val);
        }
        if (rowValues.size() != expectedCols) {
            std::cerr << "Error: Expected " << expectedCols << " numbers in a row, but got " 
                      << rowValues.size() << std::endl;
            continue;
        }
        std::vector<double> nums1(rowValues.begin(), rowValues.begin() + halfCols);
        std::vector<double> nums2(rowValues.begin() + halfCols, rowValues.end());
        testCases.emplace_back(nums1, nums2);
    }
    inputFile.close();
    
    std::string outputFilePath = OUTPUT_DIR + "/act_3.txt";
    std::ofstream outputFile(outputFilePath);
    if (!outputFile.is_open()) {
        std::cerr << "Error opening output file: " << outputFilePath << std::endl;
        return 1;
    }
    
    outputFile << std::fixed << std::setprecision(2);
    
    for (size_t i = 0; i < testCases.size(); ++i) {
        const std::vector<double>& vec1 = testCases[i].first;
        const std::vector<double>& vec2 = testCases[i].second;
        
        double* arr1 = new double[vec1.size()];
        double* arr2 = new double[vec2.size()];
        for (size_t j = 0; j < vec1.size(); ++j)
            arr1[j] = vec1[j];
        for (size_t j = 0; j < vec2.size(); ++j)
            arr2[j] = vec2[j];
        
        size1_t size1 = static_cast<size1_t>(vec1.size());
        size2_t size2 = static_cast<size2_t>(vec2.size());
        
        std::vector<result_t> resultArray = ga(arr1, arr2, size1, size2);
        
        for (size_t k = 0; k < resultArray.size(); ++k) {
            outputFile << resultArray[k];
            if (k < resultArray.size() - 1)
                outputFile << " ";
        }
        outputFile << std::endl;
        
        delete[] arr1;
        delete[] arr2;
    }
    
    outputFile.close();
    return 0;
}