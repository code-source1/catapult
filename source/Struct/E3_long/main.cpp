#include "hls_stream.h"
#include <algorithm>
#define MAX_SIZE 100

using namespace hls;

class MatrixAnalysis {
private:
    int memo[MAX_SIZE][MAX_SIZE];
    static constexpr int dirs[4][2] = {{-1, 0}, {1, 0}, {0, -1}, {0, 1}};

    struct Command {
        int type;   // 0 for setup, 1 for run DFS
        int row;
        int col;
    };

    struct Node {
        int row;
        int col;
        int depth;
    };

public:
    #pragma hls_design top
    void process(stream<Command>& cmdStream, stream<int>& inputStream, stream<int>& outputStream) {
        #pragma HLS DATAFLOW
        Command cmd;
        stream<int> matrixStream; 

        cmd = cmdStream.read();
        int rows = cmd.row;
        int cols = cmd.col;

        loadMatrixToStream(inputStream, matrixStream, rows, cols);

        cmd = cmdStream.read();
        if (cmd.type == 1) {
            int matrix[MAX_SIZE][MAX_SIZE];
            loadMatrixFromStream(matrixStream, matrix, rows, cols);
            int ans = longest(matrix, rows, cols);
            outputStream.write(ans);
        }
    }

    void loadMatrixToStream(stream<int>& inputStream, stream<int>& matrixStream, int rows, int cols) {
        for (int i = 0; i < rows * cols; ++i) {
            matrixStream.write(inputStream.read());
        }
    }

    void loadMatrixFromStream(stream<int>& matrixStream, int matrix[MAX_SIZE][MAX_SIZE], int rows, int cols) {
        for (int i = 0; i < rows; ++i) {
            for (int j = 0; j < cols; ++j) {
                matrix[i][j] = matrixStream.read();
            }
        }
    }

    int longest(int matrix[MAX_SIZE][MAX_SIZE], int rows, int columns) {
        int ans = 0;
        Node stack[MAX_SIZE * MAX_SIZE];
        int stack_size = 0;

        for (int i = 0; i < rows; ++i) {
            for (int j = 0; j < columns; ++j) {
                memo[i][j] = 0;
                stack[stack_size++] = {i, j, 1};

                while (stack_size > 0) {
                    Node top = stack[--stack_size];
                    memo[top.row][top.col] = std::max(memo[top.row][top.col], top.depth);
                    ans = std::max(ans, memo[top.row][top.col]);

                    for (int d = 0; d < 4; ++d) {
                        int newRow = top.row + dirs[d][0];
                        int newCol = top.col + dirs[d][1];
                        if (newRow >= 0 && newRow < rows && newCol >= 0 && newCol < columns &&
                            matrix[newRow][newCol] > matrix[top.row][top.col] &&
                            top.depth + 1 > memo[newRow][newCol]) {
                            stack[stack_size++] = {newRow, newCol, top.depth + 1};
                        }
                    }
                }
            }
        }
        return ans;
    }
};

constexpr int MatrixAnalysis::dirs[4][2];
