#ifndef KERNEL_H
#define KERNEL_H

#include <algorithm>
#include <climits>
#include <stack>
#include <vector>

const int MAX_K = 10;

struct TreeNode {
    int val;
    int left;  
    int right;  

    TreeNode() : val(0), left(-1), right(-1) {} 
    TreeNode(int x, int l = -1, int r = -1) : val(x), left(l), right(r) {}
};

struct DFSState {
    int nodeIndex;
    int stage; 
    int leftVals;
    int rightVals;
    int MAX_K;
    int MAX_NODES;


    DFSState() 
        : nodeIndex(-1), stage(0) {
        std::fill_n(leftVals, MAX_K, INT_MAX);
        std::fill_n(rightVals, MAX_K, INT_MAX);
    }


    DFSState(int idx) 
        : nodeIndex(idx), stage(0) {
        std::fill_n(leftVals, MAX_K, INT_MAX);
        std::fill_n(rightVals, MAX_K, INT_MAX);
    }
};


struct FixedStack {
    DFSState stack[MAX_NODES];
    int top;

    FixedStack() : top(-1) {}

    void push(const DFSState& state) {
        if (top < MAX_NODES - 1) {
            stack[++top] = state;
        }
    }

    void pop() {
        if (top >= 0) {
            top--;
        }
    }

    DFSState& back() {
        return stack[top];
    }

    bool empty() const {
        return top == -1;
    }
};

class Solution {
public:
    TreeNode tree[MAX_NODES]; 
    int count = 0; 

    Solution() {} 

    int CountGreatEnoughNodes(int rootIndex, int k) {
        int vals[MAX_K];
        std::fill_n(vals, k, INT_MAX); 
        count = 0; 
        DFS(rootIndex, k, vals); 
        return count;
    }


private:
    #pragma hls_design top
    void DFS(int rootIndex, int k, int vals[MAX_K]) {
        FixedStack stack;
        stack.push(DFSState(rootIndex));

        while (!stack.empty()) {
            DFSState &top = stack.back();
            TreeNode &node = tree[top.nodeIndex];

            if (top.stage == 0) {
                if (node.left != -1) {
                    stack.push(DFSState(node.left));
                }
                top.stage++;
            } else if (top.stage == 1) {
                if (node.right != -1) {
                    stack.push(DFSState(node.right));
                }
                top.stage++;
            } else if (top.stage == 2) {
                Merge(node.val, top.leftVals, top.rightVals, k, vals);
                if (node.val > vals[k - 1]) {
                    count++;
                }
                stack.pop();
                if (!stack.empty()) {
                    DFSState &parentTop = stack.back();
                    if (parentTop.stage == 1) {
                        for (int i = 0; i < k; ++i) {
                            parentTop.leftVals[i] = vals[i];
                        }
                    } else {
                        for (int i = 0; i < k; ++i) {
                            parentTop.rightVals[i] = vals[i];
                        }
                    }
                }
            }
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
};

#endif // KERNEL_H
