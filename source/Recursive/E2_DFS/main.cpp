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
void dfs_traverse(Allocator<node>::ptr);

Allocator<node>::ptr root = _NULL;
int front = 0, rear = -1;
int queue[MAX_SIZE];

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

        tree.space[newitem].left = tree.space[newitem].right = _NULL;
        tree.space[newitem].value = input[i];

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

    dfs_traverse(root);
    if (g_fallback) {
        *fallback = g_fallback;
        return;
    }
    for (int i = 0; i < n; i++)
        output[i] = queue[i];
}
};


void insert(Allocator<node>::ptr newitem, Allocator<node>::ptr root) {
    if (tree.space[newitem].value > tree.space[root].value) {
        if (tree.space[root].right == _NULL) {
            tree.space[root].right = newitem;
        } else {
            insert(newitem, tree.space[root].right);  
        }
    } else {
        if (tree.space[root].left == _NULL) {
            tree.space[root].left = newitem;
        } else {
            insert(newitem, tree.space[root].left);  
        }
    }
}


void dfs_traverse(Allocator<node>::ptr root) {
    if (root == _NULL) return;  

    if (tree.space[root].left != _NULL) {
        dfs_traverse(tree.space[root].left);  
    }

    queue[++rear] = tree.space[root].value;  

    if (tree.space[root].right != _NULL) {
        dfs_traverse(tree.space[root].right);  
    }
}

