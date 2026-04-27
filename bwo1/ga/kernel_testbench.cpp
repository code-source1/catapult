#include <fstream>
#include <sstream>
#include <iostream>
#include <string>
#include <cstdlib>
#include <iomanip>
#include <ac_fixed.h>

using namespace std;

// 定点数类型：总宽度22位，整数部分12位，带符号
typedef ac_fixed<22, 12, true> fixed_t;

// 声明贪婪算法函数（在 ga.cpp 中实现）
extern void ga(const fixed_t nums1[], const fixed_t nums2[], int size1, int size2,
               fixed_t out[], int *out_size);

// 固定的输入和输出路径
const string INPUT_FILE_PATH = "/nas/ei/share/TUEIEDAscratch/ge86pak/hls/bwo1/ga/1.dat";
const string OUTPUT_DIR = "/nas/ei/share/TUEIEDAscratch/ge86pak/hls/bwo1/ga/p";

int main() {
    ifstream inputFile(INPUT_FILE_PATH.c_str());
    if (!inputFile.is_open()) {
        cerr << "Error opening input file: " << INPUT_FILE_PATH << endl;
        return 1;
    }
    
    // 假设每个测试用例为输入文件的一行，该行应包含 14 个数字（定点数格式）
    // 每行拆分为两部分：前 7 个数字为数组1，后 7 个数字为数组2
    const int expectedCols = 14;
    const int halfCols = expectedCols / 2;  // 7
    
    string line;
    // 假设最多处理 10 个测试用例
    const int maxTestCases = 10;
    int testCaseCount = 0;
    
    // 输出文件路径
    string outputFilePath = OUTPUT_DIR + "/act_3.txt";
    ofstream outputFile(outputFilePath.c_str());
    if (!outputFile.is_open()) {
        cerr << "Error opening output file: " << outputFilePath << endl;
        return 1;
    }
    // 设置固定格式和两位小数的输出（HLS仿真时打印定点数时会转换为浮点显示）
    outputFile << fixed << setprecision(2);
    
    // 逐行读取输入文件
    while(getline(inputFile, line) && testCaseCount < maxTestCases) {
        if(line.empty()) continue;
        istringstream iss(line);
        double temp;
        fixed_t rowValues[expectedCols];
        int count = 0;
        // 以 double 形式读取，再转换为 fixed_t
        while (iss >> temp && count < expectedCols) {
            rowValues[count++] = temp;
        }
        if(count != expectedCols) {
            cerr << "Error: Expected " << expectedCols << " numbers in a row, but got " << count << endl;
            continue;
        }
        // 拆分成两个数组
        fixed_t arr1[halfCols], arr2[halfCols];
        for (int i = 0; i < halfCols; i++) {
            arr1[i] = rowValues[i];
        }
        for (int i = 0; i < halfCols; i++) {
            arr2[i] = rowValues[i + halfCols];
        }
        
        fixed_t result[expectedCols];
        int out_size;
        ga(arr1, arr2, halfCols, halfCols, result, &out_size);
        
        // 将结果数组写入输出文件，每个数字之间以空格分隔
        for (int i = 0; i < out_size; i++) {
            outputFile << result[i];
            if (i < out_size - 1)
                outputFile << " ";
        }
        outputFile << "\n";
        testCaseCount++;
    }
    
    inputFile.close();
    outputFile.close();
    return 0;
}
