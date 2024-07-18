#include <cstdlib> 

#define MAX_POINTS 300
#define HASH_SIZE 40009 
int my_abs(int x) {
    return (x < 0) ? -x : x;
}

int simple_div(int numerator, int denominator) {
    if (denominator == 0) return 0; 
    int result = 0;
    int sum = denominator;
    while (sum <= numerator) {
        sum += denominator;
        result++;
    }
    return result;
}

class Solution {
public:
    int points[MAX_POINTS][2];
    int numPoints;

    int gcd(int a, int b) {
        #pragma HLS INLINE
        while (a != b) {
            if (a > b) {
                a = a - b;
            } else {
                b = b - a;
            }
        }
        return a;
    }

    #pragma hls_design top
    int maxPoints() {
        if (numPoints <= 2) {
            return numPoints;
        }
        int result = 0;
        for (int i = 0; i < numPoints; i++) {
            if (result >= numPoints - i || result > numPoints / 2) {
                break;
            }
            int map[HASH_SIZE] = {0};
            int maxCount = 0;
            for (int j = i + 1; j < numPoints; j++) {
                int dx = points[j][0] - points[i][0];
                int dy = points[j][1] - points[i][1];
                if (dx == 0) {
                    dy = 1;
                } else if (dy == 0) {
                    dx = 1;
                } else {
                    if (dy < 0) {
                        dx = -dx;
                        dy = -dy;
                    }
                    int gcdXY = gcd(my_abs(dx), my_abs(dy));
                    dx = simple_div(dx, gcdXY);
                    dy = simple_div(dy, gcdXY);
                }
                int hashKey = (dy + 20001 * dx) % HASH_SIZE;
                map[hashKey]++;
                maxCount = max(maxCount, map[hashKey]);
            }
            result = max(result, maxCount + 1);
        }
        return result;
    }

    int max(int a, int b) {
        return a > b ? a : b;
    }
};

