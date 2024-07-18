#include "main.cpp"
#include <iostream>
#include <cstdlib>
#include <ac_channel.h>

using namespace std;

CCS_MAIN(int argc, char *argv[])
{
    enum { kValsTested = 188, };
    static_assert(kValsTested > 0, "You must test one or more k values.");
    static_assert(kValsTested <= 188, "You can't test more than 188 k values.");

    int kOld = -4, f1Old = 0, f2Old = 0;
    uint1 inputArrOld[6144];
    ac_turbo_encoder turboEncInst;

    bool test_fail = false;

    for (int kValCnt = 0; kValCnt < 2 * kValsTested + 1; kValCnt++) {
        int k = 0;
        int f1 = 0;
        int f2 = 0;

        const bool finalIt = (kValCnt == 2 * kValsTested);

        #include <ac_comm/ac_turbo_encoder_rom.h>

        if (!finalIt) {
            int tableInd = kValCnt < kValsTested ? kValCnt : 2 * kValsTested - kValCnt - 1;
            if (tableInd <= 59) {
                k = 8 * tableInd + 40;
            } else if (tableInd <= 91) {
                k = (tableInd - 59) * 16 + 512;
            } else if (tableInd <= 123) {
                k = (tableInd - 91) * 32 + 1024;
            } else {
                k = (tableInd - 123) * 64 + 2048;
            }
            f1 = f1Arr[tableInd];
            f2 = f2Arr[tableInd];
        }

        cout << "Testing with k = " << k << ", kOld = " << kOld << endl;

        uint1 inputArr[6144];
        uint3 outputDes[6144 + 4];
        ac_channel<uint1> inChan;
        ac_channel<uint3> outChan;
        ac_channel<uint13> kChan;

        for (int i = 0; i < k; i++) {
            int inputVal = rand() % 2;
            inputArr[i] = inputVal;
            inChan.write(inputVal);
        }

        kChan.write(k);
        turboEncInst.run(inChan, outChan, kChan);

        #ifndef __CCOV__
        if (inChan.debug_size() != 0) {
            cout << "Test FAILED. Input channel values were not entirely consumed by design." << endl;
            test_fail = true;
            break;
        }

        if (kChan.debug_size() != 0) {
            cout << "Test FAILED. k value was not consumed by design." << endl;
            test_fail = true;
            break;
        }

        if (outChan.debug_size() != unsigned(kOld + 4)) {
            cout << "Test FAILED. Output channel has incorrect number of values." << endl;
            test_fail = true;
            break;
        }
        #endif

        for (int i = 0; i < kOld + 4; i++) {
            outputDes[i] = outChan.read();
        }

        uint3 outputRef[6144 + 4];
        uint1 reg1[3] = {0, 0, 0};
        uint1 reg2[3] = {0, 0, 0};

        for (int i = 0; i < kOld; i++) {
            uint1 outputEnc1[2], outputEnc2[2];
            const bool terminate = false;
            int iLvInd = ((uint32(f1Old) * uint32(i) + uint32(f2Old) * uint32(i) * uint32(i)) % uint32(kOld)).to_int();

            regUpdate(inputArrOld[i], terminate, reg1, outputEnc1);
            regUpdate(inputArrOld[iLvInd], terminate, reg2, outputEnc2);
            outputRef[i][0] = outputEnc1[0];
            outputRef[i][1] = outputEnc1[1];
            outputRef[i][2] = outputEnc2[1];
        }

        uint3 outputTerm[2];

        for (int i = 0; i < 3; i++) {
            uint1 outputEnc1[2], outputEnc2[2];
            const bool terminate = true;
            regUpdate(0, terminate, reg1, outputEnc1);
            regUpdate(0, terminate, reg2, outputEnc2);
            switch (i) {
                case 0:
                    outputRef[kOld][0] = outputEnc1[0];
                    outputTerm[0][0] = outputEnc2[0];
                    outputRef[kOld][1] = outputEnc1[1];
                    outputTerm[0][1] = outputEnc2[1];
                    break;
                case 1:
                    outputRef[kOld][2] = outputEnc1[0];
                    outputTerm[0][2] = outputEnc2[0];
                    outputRef[kOld + 1][0] = outputEnc1[1];
                    outputTerm[1][0] = outputEnc2[1];
                    break;
                default:
                    outputRef[kOld + 1][1] = outputEnc1[0];
                    outputTerm[1][1] = outputEnc2[0];
                    outputRef[kOld + 1][2] = outputEnc1[1];
                    outputTerm[1][2] = outputEnc2[1];
                    break;
            }
        }

        for (int i = 0; i < 2; i++) {
            outputRef[kOld + 2 + i] = outputTerm[i];
        }

        #ifndef __CCOV__
        for (int i = 0; i < kOld + 4; i++) {
            if (outputRef[i] != outputDes[i]) {
                cout << "Test FAILED. Design output does not match reference output." << endl;
                test_fail = true;
                break;
            }
        }

        if (test_fail) {
            break;
        }
        #endif

        kOld = k;
        f1Old = f1;
        f2Old = f2;

        for (int i = 0; i < k; i++) {
            inputArrOld[i] = inputArr[i];
        }
    }

    #ifndef __CCOV__
    if (test_fail) {
        CCS_RETURN(-1);
    }
    #endif

    cout << "Test PASSED!" << endl;

    CCS_RETURN(0);
}
