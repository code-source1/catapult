#include <iostream>
#include <algorithm>
using namespace std;
111
#define MAX_LENGTH 1000


struct SimpleSet {
    char elements[MAX_LENGTH];
    int count;

    SimpleSet() : count(0) {} 

    void insert(char c) {
        if (!contains(c)) {
            elements[count++] = c;
        }
    }

    bool contains(char c) {
        for (int i = 0; i < count; ++i) {
            if (elements[i] == c) return true;
        }
        return false;
    }

    void erase(char c) {
        for (int i = 0; i < count; ++i) {
            if (elements[i] == c) {
                elements[i] = elements[--count];
                return;
            }
        }
    }

    void clear() {
        count = 0;
    }
};

int myStrlen(char* s) {
    int length = 0;
    while (*s != '\0') {
        length++;
        s++;
    }
    return length;
}

#pragma hls_design top
int length(char* s) {
    SimpleSet occ;
    int n = myStrlen(s); 
    int rk = -1, ans = 0;
    occ.clear();

    for (int i = 0; i < n; ++i) {
        if (i != 0) {
            occ.erase(*(s + i - 1));
        }
        while (rk + 1 < n && !occ.contains(*(s + rk + 1))) {
            occ.insert(*(s + rk + 1));
            ++rk;
        }
        ans = max(ans, rk - i + 1);
    }
    return ans;
}
