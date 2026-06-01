#include <ac_int.h>
#define MAX 10
#define NULL_IDX MAX

struct TreeNode {
    int left;    
    int right;
    int value;   
};

TreeNode Pool[MAX];

void initialize(int n) {
    for (int i = 0; i < MAX; ++i) {
        Pool[i].left = NULL_IDX;
        Pool[i].right = NULL_IDX;
        Pool[i].value = -1;
    }
}

void buildTree(const ac_int<9, true> input[MAX], int n, int &outRootIndex) {
    int nextFree = 0;
    if (n == 0) { outRootIndex = NULL_IDX; return; }
    Pool[nextFree].value = input[0];
    Pool[nextFree].left = Pool[nextFree].right = NULL_IDX;
    outRootIndex = nextFree++;
    for (int i = 1; i < n; ++i) {
        int curr = outRootIndex;
        while (1) {
            if (input[i] > Pool[curr].value) {
                if (Pool[curr].right == NULL_IDX) {
                    Pool[nextFree].value = input[i];
                    Pool[nextFree].left = Pool[nextFree].right = NULL_IDX;
                    Pool[curr].right = nextFree++;
                    break;
                } else {
                    curr = Pool[curr].right;
                }
            } else {
                if (Pool[curr].left == NULL_IDX) {
                    Pool[nextFree].value = input[i];
                    Pool[nextFree].left = Pool[nextFree].right = NULL_IDX;
                    Pool[curr].left = nextFree++;
                    break;
                } else {
                    curr = Pool[curr].left;
                }
            }
        }
    }
}

void bfs_traverse(int rootIndex, ac_int<9, false> output[MAX], int n) {
    if (rootIndex == NULL_IDX) return;
    int queue[MAX];
    int front = 0, rear = 0;
    queue[rear++] = rootIndex;
    int idx = 0;
    while (front < rear && idx < n) {
        int curr = queue[front++];
        output[idx++] = Pool[curr].value;
        if (Pool[curr].left != NULL_IDX)
            queue[rear++] = Pool[curr].left;
        if (Pool[curr].right != NULL_IDX)
            queue[rear++] = Pool[curr].right;
    }
}

extern "C" {
#pragma hls_design top
void process_top(int n, ac_int<9, true> input[MAX], ac_int<9, false> output[MAX]) {
    int bst_root;
    initialize(n);
    buildTree(input, n, bst_root);
    bfs_traverse(bst_root, output, n);
}
}
