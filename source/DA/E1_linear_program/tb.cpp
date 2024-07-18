#include "main.cpp" 
#include <iostream>
#include <cstdint>
#include <iomanip>


#define MAX_ROWS 10
#define MAX_COLS 10
#define SCALING_FACTOR 10000  
int main() {

    int32_t tableau[MAX_ROWS][MAX_COLS] = {
        {-3 * SCALING_FACTOR, -5 * SCALING_FACTOR, 0, 0, 0},  // Objective function: -z + 3x + 5y = 0, scaled
        {1 * SCALING_FACTOR, 1 * SCALING_FACTOR, 1 * SCALING_FACTOR, 0, 7 * SCALING_FACTOR},  // Constraint 1: x + y + s1 = 7, scaled
        {3 * SCALING_FACTOR, 2 * SCALING_FACTOR, 0, 1 * SCALING_FACTOR, 18 * SCALING_FACTOR}  // Constraint 2: 3x + 2y + s2 = 18, scaled
    };

    int m = 3;  // Number of rows
    int n = 5;  // Number of columns

    // Instantiate the solver
    SimplexSolver solver(tableau, m, n);

    // Solve the optimization problem
    solver.solve();

    // Output the final tableau
    std::cout << "Solution Tableau:" << std::endl;
    for (int i = 0; i < m; i++) {
        for (int j = 0; j < n; j++) {
            double val = tableau[i][j] / static_cast<double>(SCALING_FACTOR);  // Convert back to double for display
            std::cout << std::setw(8) << std::setprecision(2) << std::fixed << val << " ";
        }
        std::cout << std::endl;
    }

    return 0;
}
