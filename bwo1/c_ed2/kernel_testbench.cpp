#include "image.h"
#include <fstream>
#include <iostream>
#include <sstream>
#include <string>
#include <filesystem>  // C++17 filesystem
#include <cstdlib>

using namespace std;


const std::string INPUT_FILE_PATH = "...1/c_ed2/1.dat";
const std::string OUTPUT_DIR = ".../c_ed2/p";


SimpleImage readImage(const std::string& filename) {
    ifstream file(filename);
    if (!file.is_open()) {
        cerr << "Error opening file: " << filename << endl;
        exit(1);
    }
    
    SimpleImage img;
    img.width = 0;
    img.height = 0;
    
    string line;
    int y = 0;
    while (getline(file, line) && y < MAX_HEIGHT) {
        istringstream iss(line);
        float value;
        int x = 0;
        while (iss >> value && x < MAX_WIDTH) {
            img.data[y][x] = value;
            x++;
        }
        if (y == 0) {
            img.width = x; 
        }
        y++;
    }
    img.height = y;
    file.close();
    return img;
}


void saveImage(const SimpleImage& img, const std::string& filename) {
    ofstream file(filename);
    if (!file.is_open()){
        cerr << "Cannot write to file: " << filename << endl;
        return;
    }
    for (int y = 0; y < img.height; ++y) {
        for (int x = 0; x < img.width; ++x) {
            file << img.data[y][x];
            if (x < img.width - 1)
                file << " ";
        }
        file << "\n";
    }
    file.close();
}

int main() {

    string outputFile = OUTPUT_DIR + "/act_3.txt";
    
    SimpleImage img = readImage(INPUT_FILE_PATH);
    detectEdges(img);

    int nonZeroCount = 0;
    int zeroCount = 0;
    for (int y = 0; y < img.height; ++y) {
        for (int x = 0; x < img.width; ++x) {
            if (img.data[y][x] != 0.0f)
                nonZeroCount++;
            else
                zeroCount++;
        }
    }
    

    saveImage(img, outputFile);
    

    ofstream nonZeroFile(OUTPUT_DIR + "/nzctxt");
    ofstream zeroFile(OUTPUT_DIR + "/zc.txt");
    
    if (nonZeroFile.is_open()) {
        nonZeroFile << nonZeroCount << endl;
        nonZeroFile.close();
    } else {
        cerr << "Cannot write to file: " << OUTPUT_DIR + "/nzctxt" << endl;
    }
    
    if (zeroFile.is_open()) {
        zeroFile << zeroCount << endl;
        zeroFile.close();
    } else {
        cerr << "Cannot write to file: " << OUTPUT_DIR + "/zc.txt" << endl;
    }
    
    cout << "Edge detection completed. Processed image saved to " << outputFile << endl;
    return 0;
}
