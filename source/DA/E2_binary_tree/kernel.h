#include <algorithm>
#include <climits>

const int MAX_NODES = 100; // Maximum number of nodes in the tree
const int MAX_K = 10;      // Maximum value for k

struct TreeNode {
    int val;
    int left;   // Index of the left child
    int right;  // Index of the right child

    // Update the constructor to accept integers for indices
    TreeNode(int x, int l = -1, int r = -1) : val(x), left(l), right(r) {}
};


class Solution {
private:
    TreeNode tree[MAX_NODES];
    int count = 0;

    void DFS(int nodeIndex, int k, int vals[MAX_K]) {
        if (nodeIndex == -1) {
            std::fill_n(vals, k, INT_MAX);
            return;
        }
        
        TreeNode node = tree[nodeIndex];
        int leftVals[MAX_K], rightVals[MAX_K];
        std::fill_n(leftVals, k, INT_MAX);
        std::fill_n(rightVals, k, INT_MAX);

        DFS(node.left, k, leftVals);
        DFS(node.right, k, rightVals);
        Merge(node.val, leftVals, rightVals, k, vals);

        if (node.val > vals[k - 1]) {
            count++;
        }
    }

    void Merge(int nodeVal, int leftVals[MAX_K], int rightVals[MAX_K], int k, int merged[MAX_K]) {
        std::fill_n(merged, k, INT_MAX);
        int leftIndex = 0, rightIndex = 0, mergedIndex = 0;
        while (mergedIndex < k) {
            if (nodeVal <= std::min(leftVals[leftIndex], rightVals[rightIndex])) {
                merged[mergedIndex++] = nodeVal;
                nodeVal = INT_MAX;
            } else if (leftVals[leftIndex] <= rightVals[rightIndex]) {
                merged[mergedIndex++] = leftVals[leftIndex++];
            } else {
                merged[mergedIndex++] = rightVals[rightIndex++];
            }
        }
    }

public:
    int CountGreatEnoughNodes(int rootIndex, int k) {
        int vals[MAX_K];
        std::fill_n(vals, k, INT_MAX);
        DFS(rootIndex, k, vals);
        return count;
    }
};
