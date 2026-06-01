#include <cstdlib>
#include <cstdio>
#include <queue>

struct btnode {
    int value;
    btnode *left, *right;
};
typedef btnode node;

void insert(node *, node *);
void bfs_traverse(node *, int *, int);

node *root = NULL;
int *queue_output = nullptr;
int front = 0, rear = -1;

bool g_fallback = false;

extern "C" {
void process_top(int n, int *input, int *output, int *fallback) {
    node *newitem = NULL;


    root = NULL;
    front = 0; rear = -1; g_fallback = false;
    if(queue_output) { free(queue_output); queue_output = nullptr; }

    for (int i = 0; i < n; i++) {
        newitem = (node*)malloc(sizeof(node));
        if (newitem == NULL) {
            g_fallback = true;
            goto fail;
        }
        newitem->left = newitem->right = NULL;
        newitem->value = input[i];
        if (root == NULL) {
            root = newitem;
        } else {
            insert(newitem, root);
            if (g_fallback) goto fail;
        }
    }

    queue_output = (int *)malloc(sizeof(int) * n);
    if (queue_output == NULL) {
        g_fallback = true;
        goto fail;
    }
    for (int i = 0; i < n; ++i) queue_output[i] = 0;
    bfs_traverse(root, queue_output, n);
    if (g_fallback) goto fail;
    for (int i = 0; i < n; i++)
        output[i] = queue_output[i];
fail:
    *fallback = g_fallback;

}
}; 

void insert(node *newitem, node *root) {
    if (newitem->value > root->value) {
        if (root->right == NULL)
            root->right = newitem;
        else
            insert(newitem, root->right);
    } else {
        if (root->left  ==  NULL)
            root->left = newitem;
        else
            insert(newitem, root->left);
    }
}

void bfs_traverse(node *root, int *queue_output, int n) {
    if (root == nullptr) return;
    std::queue<node *> q;
    int idx = 0;
    q.push(root);
    while (!q.empty() && idx < n) {
        node *cur = q.front(); q.pop();
        queue_output[idx++] = cur->value;
        if (cur->left)  q.push(cur->left);
        if (cur->right) q.push(cur->right);
    }
}
