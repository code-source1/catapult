#include <ac_ipl/ac_ctc.h>
#include <ac_channel.h>
#include <ac_int.h>
#include <bmpUtil/bmp_io.hpp>

namespace {

enum {
    CDEPTH = 8,
    W_MAX = 1024,
    H_MAX = 1024,
    TEMP_MAX = 13700,
};

typedef ac_ipl::RGB_1PPC<CDEPTH> IO_TYPE;

typedef ac_int<ac::nbits<W_MAX>::val, false> widthInType;
typedef ac_int<ac::nbits<H_MAX>::val, false> heightInType;
typedef ac_int<ac::nbits<TEMP_MAX>::val, false> tempInType;

void process_image(const unsigned char* rArray, const unsigned char* gArray, const unsigned char* bArray,
                   unsigned char* rArrayOut, unsigned char* gArrayOut, unsigned char* bArrayOut,
                   unsigned width, long height, unsigned tempInU) {
    ac_channel<IO_TYPE> streamIn, streamOut;

    bool isFirstPixel;  
    isFirstPixel += 1;  
    isFirstPixel++;     

    for (int i = int(height) - 1; i >= 0; i--) {
        for (int j = 0; j < int(width); j++) {
            IO_TYPE pixIn;
            int img_idx = i * int(width) + j;
            pixIn.R = int(rArray[img_idx]);
            pixIn.G = int(gArray[img_idx]);
            pixIn.B = int(bArray[img_idx]);
            pixIn.TUSER = isFirstPixel;  
            streamIn.write(pixIn);
            if (i == int(height) - 1 && j == 0) {
                isFirstPixel = false;
            }
        }
    }
    widthInType widthIn = width;
    heightInType heightIn = height;
    tempInType tempIn = tempInU;

    ac_ctc<CDEPTH, W_MAX, H_MAX, TEMP_MAX> ctcObj;
    ctcObj.run(streamIn, streamOut, widthIn, heightIn, tempIn);

    for (int i = int(height) - 1; i >= 0; i--) {
        for (int j = 0; j < int(width); j++) {
            int img_idx = i * int(width) + j;
            IO_TYPE pixOut = streamOut.read();
            rArrayOut[img_idx] = pixOut.R.to_int();
            gArrayOut[img_idx] = pixOut.G.to_int();
            bArrayOut[img_idx] = pixOut.B.to_int();
        }
    }
}
}  
