#include "main.cpp"
#include <iostream>

int main() {
    // Case 1
    {
        Solution sol;
        int k = 2;

        // Building the tree
        // Indices start from 0, therefore, TreeNode(index_value, left_child_index, right_child_index)
        sol.tree[0] = TreeNode(7, 1, 2);
        sol.tree[1] = TreeNode(6, 3, 4);
        sol.tree[2] = TreeNode(5, 5, 6);
        sol.tree[3] = TreeNode(4);
        sol.tree[4] = TreeNode(3);
        sol.tree[5] = TreeNode(2);
        sol.tree[6] = TreeNode(1);

        std::cout << "Case 1: Expected = 3, Got = " << sol.CountGreatEnoughNodes(0, k) << std::endl;
    }

    // Case 2
    {
        Solution sol;
        int k = 1;

        // Building a straight line tree (skewed to the right)
        sol.tree[0] = TreeNode(1, 1); // Node 0 has value 1 and a right child at index 1
        sol.tree[1] = TreeNode(2, 2); // Node 1 has value 2 and a right child at index 2
        sol.tree[2] = TreeNode(3);    // Node 2 has value 3 and no children

        std::cout << "Case 2: Expected = 0, Got = " << sol.CountGreatEnoughNodes(0, k) << std::endl;
    }

    // Case 3
    {
        Solution sol;
        int k = 2;

        // Building a small tree
        sol.tree[0] = TreeNode(3, 1, 2);
        sol.tree[1] = TreeNode(1);
        sol.tree[2] = TreeNode(2);

        std::cout << "Case 3: Expected = 1, Got = " << sol.CountGreatEnoughNodes(0, k) << std::endl;
    }

    return 0;
}
