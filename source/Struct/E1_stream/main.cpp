#include "hls_stream.h"

#define N 40010

class ProductOfNumbers {
private:
    int numbers[N];
    int len;

public:
    ProductOfNumbers() : len(0) {}

    void add(int num) {
        if (num == 0) {
            len = 0;
        } else if (len < N) {
            numbers[len++] = num;
        }
    }

    int getProduct(int k) {
        if (len < k) return 0;
        int product = 1;
        for (int i = len - k; i < len; i++) {
            product *= numbers[i];
            if (product == 0) return 0;
        }
        return product;
    }
};

struct InterfaceHandler {
    hls::stream<int>& in;
    hls::stream<int>& out;
    ProductOfNumbers pon;

    void processCommand() {
        int command = in.read();  
        int data = in.read();     

        if (command == 1) {  
            pon.add(data);
            out.write(-1);  
        } else if (command == 2) {  
            int result = pon.getProduct(data);
            out.write(result);
        }
    }
};

#pragma hls_design top
void top(hls::stream<int>& commandDataStream, hls::stream<int>& resultStream, int num_commands) {
#pragma HLS DATAFLOW
    hls::stream<int> intermediateStream;
    InterfaceHandler handler1{commandDataStream, intermediateStream};
    InterfaceHandler handler2{intermediateStream, resultStream};

    for (int i = 0; i < num_commands; i++) {
        handler1.processCommand();  
        handler2.processCommand();  
    }
}
