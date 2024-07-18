#include "main.cpp"
#include <ac_ipl/ac_ctc.h>
#include <string>
#include <fstream>
#include <iostream>
#include <bmpUtil/bmp_io.hpp>


using namespace std;

CCS_MAIN(int argc, char *argv[])
{
  if (argc < 3) {
    cerr << "Usage: " << argv[0] << " <color_temp_val> <outputdir> <first_input_image> <second_input_image> ... <nth_input_image>" << endl;
    CCS_RETURN(-1);
  }

  const int nImages = argc - 3; // Find number of images based on number of command line arguments.
  const unsigned tempInU = atoi(argv[1]); // Store color temp as an unsigned val
  string outDir = argv[2];
  
  unsigned char *rArray = new unsigned char[W_MAX * H_MAX];
  unsigned char *gArray = new unsigned char[W_MAX * H_MAX];
  unsigned char *bArray = new unsigned char[W_MAX * H_MAX];
  
  for (int k = 3; k < argc; k++) {
    cout << "Processing frame number: " << k - 2 << endl;
  
    string inFileName  = argv[k];
    std::size_t leaf = inFileName.rfind("/");
    string outFileName = inFileName.substr(leaf + 1);
    outFileName.insert(0, "ctc_");
    outFileName.insert(0, outDir);
    
    unsigned long width;
    long height;
    
    cout << "Reading input image from file: " << inFileName << endl;
    bool read_fail = bmp_read((char *)inFileName.c_str(), &width, &height, &rArray, &gArray, &bArray);
    
    if (read_fail) {
      cerr << "Failed to read input image: " << inFileName << endl;
      CCS_RETURN(-1);
    }

    cout << "Input image read successfully. Width = " << width << ", height = " << height << endl;
  
    unsigned char *rArrayOut = new unsigned char[W_MAX * H_MAX];
    unsigned char *gArrayOut = new unsigned char[W_MAX * H_MAX];
    unsigned char *bArrayOut = new unsigned char[W_MAX * H_MAX];

    process_image(rArray, gArray, bArray, rArrayOut, gArrayOut, bArrayOut, width, height, tempInU);
    
    cout << "Writing image to file: " << outFileName << endl;
    bool write_fail = bmp_24_write((char *)outFileName.c_str(), width, height, rArrayOut, gArrayOut, bArrayOut);

    if (write_fail) {
      cerr << "Failed to write output image: " << outFileName << endl;
      CCS_RETURN(-1);
    }
    
    cout << "Image written successfully." << endl;

    delete[] rArrayOut;
    delete[] gArrayOut;
    delete[] bArrayOut;
  }
  
  delete[] rArray;
  delete[] gArray;
  delete[] bArray;

  CCS_RETURN(0);
}
