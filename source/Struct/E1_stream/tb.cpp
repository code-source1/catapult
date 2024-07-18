#include "main.cpp"
#include <iostream>
#include "hls_stream.h"


extern void process_stream(hls::stream<int>& commandStream, hls::stream<int>& dataStream, hls::stream<int>& outputStream, int num_commands);

int main() {
    hls::stream<int> commandStream;
    hls::stream<int> dataStream;
    hls::stream<int> outputStream;

    int commands[] = {1, 1, 1, 1, 1, 2, 2, 2, 1, 2}; 
    int data[] = {3, 0, 2, 5, 4, 2, 3, 4, 8, 2};
    int num_commands = sizeof(commands) / sizeof(commands[0]);

    for (int i = 0; i < num_commands; i++) {
        commandStream.write(commands[i]);
        dataStream.write(data[i]);
    }

    process_stream(commandStream, dataStream, outputStream, num_commands);

    while (!outputStream.empty()) {
        int output = outputStream.read();
        if (output != -1) { // Ignore 'null' outputs which are -1
            std::cout << output << std::endl;
        }
    }

    return 0;
}
