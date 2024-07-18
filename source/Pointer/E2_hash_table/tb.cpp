#include "main.cpp"
#include <cstring>

extern int length(char s[]);

int main() {
    char test1[] = "abcabcbb";
    char test2[] = "bbbbb";
    char test3[] = "pwwkew";
    
    std::cout << "Test 1: " << length(test1) << " (Expected: 3)" << std::endl;
    std::cout << "Test 2: " << length(test2) << " (Expected: 1)" << std::endl;
    std::cout << "Test 3: " << length(test3) << " (Expected: 3)" << std::endl;

    return 0;
}
