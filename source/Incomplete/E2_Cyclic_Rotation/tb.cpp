#include "main.cpp"
#include <iostream>

void printGrid(Solution &sol) {
    for (int i = 0; i < sol.m; ++i) {
        for (int j = 0; j < sol.n; ++j) {
            std::cout << sol.grid[i][j] << " ";
        }
        std::cout << std::endl;
    }
}

int main() {
    Solution sol;

    int grid1[MAX_M][MAX_N] = {{40, 10}, {30, 20}};
    sol.setInput(grid1, 2, 2);
    sol.rotateGrid(1, 0);  
    std::cout << "Output for Example 1:" << std::endl;
    printGrid(sol);


    int grid2[MAX_M][MAX_N] = {{1,2,3,4},{5,6,7,8},{9,10,11,12},{13,14,15,16}};
    sol.setInput(grid2, 4, 4);
    sol.rotateGrid(2, 0);  
    std::cout << "Output for Example 2:" << std::endl;
    printGrid(sol);

    return 0;
}
