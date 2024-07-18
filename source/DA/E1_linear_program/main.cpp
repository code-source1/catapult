#ifndef SIMPLEX_SOLVER_H
#define SIMPLEX_SOLVER_H

#include <cstdint>
#include <iostream>
#include <climits>
#include <iomanip>

#define SCALING_FACTOR 10000 

int32_t my_abs(int32_t x) {
    return (x < 0) ? -x : x;
}

int32_t simple_divide(int32_t numerator, int32_t denominator) {
    int32_t quotient = 0;
    int32_t remainder = numerator;

    while (remainder >= denominator) {
        remainder -= denominator;
        ++quotient;
    }

    return quotient;
}

class SimplexSolver {
public:
    int32_t tableau[MAX_ROWS][MAX_COLS];
    int numRows, numCols;

    SimplexSolver(int32_t inputTableau[MAX_ROWS][MAX_COLS], int m, int n) : numRows(m), numCols(n) {
        for (int i = 0; i < numRows; ++i) {
            for (int j = 0; j < numCols; ++j) {
                tableau[i][j] = inputTableau[i][j];
            }
        }
    }
    #pragma hls_design top
    void solve() {
        int pivotRow, pivotCol;

        while (true) {
            pivotCol = findPivotColumn();
            if (pivotCol == -1) break;

            pivotRow = findPivotRow(pivotCol);
            if (pivotRow == -1) {
                std::cout << "Problem is unbounded." << std::endl;
                break;
            }

            pivot(pivotRow, pivotCol);
        }
    }

    int findPivotColumn() {
        int index = -1;
        int32_t min = 0;
        for (int i = 0; i < numCols - 1; i++) {
            if (tableau[0][i] < min) {
                min = tableau[0][i];
                index = i;
            }
        }
        return index;
    }

    int findPivotRow(int pivotCol) {
        int index = -1;
        int32_t minRatio = INT32_MAX;
        for (int i = 1; i < numRows; i++) {
            if (tableau[i][pivotCol] > 0) {
                int32_t ratio = simple_divide(tableau[i][numCols - 1] * SCALING_FACTOR, tableau[i][pivotCol]);
                if (ratio < minRatio) {
                    minRatio = ratio;
                    index = i;
                }
            }
        }
        return index;
    }

    void pivot(int pivotRow, int pivotCol) {
        int32_t pivotValue = tableau[pivotRow][pivotCol];
        for (int j = 0; j < numCols; j++) {
            tableau[pivotRow][j] = simple_divide(tableau[pivotRow][j] * SCALING_FACTOR, pivotValue);
        }

        for (int i = 0; i < numRows; i++) {
            if (i != pivotRow) {
                int32_t factor = tableau[i][pivotCol];
                for (int j = 0; j < numCols; j++) {
                    tableau[i][j] = tableau[i][j] * SCALING_FACTOR - factor * tableau[pivotRow][j];
                    tableau[i][j] /= SCALING_FACTOR; // Re-normalize to avoid overflow
                }
            }
        }
    }
};

#endif // SIMPLEX_SOLVER_H
