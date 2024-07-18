#include <stdlib.h>
#include <stdio.h>

#define MAX_SIZE 8
const long long _NULL = -1;

template <class T>
struct Allocator {
    typedef long long ptr;

    T space[MAX_SIZE];
    ptr freeMemory[MAX_SIZE];
    int noOffreeMemory;

    Allocator() {
        noOffreeMemory = MAX_SIZE;
        for (int i = 0; i < noOffreeMemory; i++) {
            space[i].left = _NULL;
            space[i].right = _NULL;
            freeMemory[i] = i;
        }
    }

    ptr malloc() {
        if (noOffreeMemory < 1) {
            return _NULL;
        } else {
            noOffreeMemory--;
            return freeMemory[noOffreeMemory];
        }
    }

    void free(ptr ptr1) {
        freeMemory[noOffreeMemory++] = ptr1;
    }
};

struct btnode {
    int value;
    long long left, right;
};
typedef struct btnode node;

Allocator<node> tree;


void insert(Allocator<node>::ptr, Allocator<node>::ptr);
void bfs_traverse(Allocator<node>::ptr, int output[MAX_SIZE]);

Allocator<node>::ptr root = _NULL;
int queue[MAX_SIZE];
int front = 0, rear = -1;

bool g_fallback = false;

extern "C" {
#pragma hls_design top
void process_top(int n, int input[MAX_SIZE], int output[MAX_SIZE], int *fallback) {
    g_fallback = false;
    front = 0;
    rear = -1;
    root = _NULL;
    tree = Allocator<node>();

    Allocator<node>::ptr newitem = _NULL;
    *fallback = false;

    for (int i = 0; i < n; i++) {
        newitem = tree.malloc();
        if (newitem == _NULL) {
            *fallback = true;
            return;
        }

        tree.space[newitem].value = input[i];
        tree.space[newitem].left = tree.space[newitem].right = _NULL;

        if (root == _NULL) {
            root = newitem;
        } else {
            insert(newitem, root);
            if (g_fallback) {
                *fallback = g_fallback;
                return;
            }
        }
    }

    bfs_traverse(root, output);
    if (g_fallback) {
        *fallback = g_fallback;
        return;
    }
}
};

void insert(Allocator<node>::ptr newitem, Allocator<node>::ptr curr) {
    if (tree.space[newitem].value > tree.space[curr].value) {
        if (tree.space[curr].right == _NULL) {
            tree.space[curr].right = newitem;
        } else {
            insert(newitem, tree.space[curr].right);
        }
    } else {
        if (tree.space[curr].left == _NULL) {
            tree.space[curr].left = newitem;
        } else {
            insert(newitem, tree.space[curr].left);
        }
    }
}


void bfs_traverse_level(int index, int level_size, int output[MAX_SIZE]) {
    if (index >= level_size) return; 
    Allocator<node>::ptr currentNode = queue[index];
    output[rear++] = tree.space[currentNode].value; 

    if (tree.space[currentNode].left != _NULL) {
        queue[rear] = tree.space[currentNode].left; 
    }
    if (tree.space[currentNode].right != _NULL) {
        queue[rear++] = tree.space[currentNode].right; 
    }
    bfs_traverse_level(index + 1, level_size, output); 
}

void bfs_traverse(Allocator<node>::ptr root, int output[MAX_SIZE]) {
    if (root == _NULL) return; 
    rear = 0; // Initialize rear for BFS queue
    queue[rear++] = root; 
    int currentLevelSize = 1; 
    for (int start = 0; rear > start; start += currentLevelSize) {
        int end = rear;
        currentLevelSize = end - start; 
        bfs_traverse_level(start, currentLevelSize, output); 
    }
}
