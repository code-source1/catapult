#ifndef BFS_H
#define BFS_H
#include <ac_int.h>
#define MAX 10
typedef ac_int<9, false> output_t;
#ifdef __cplusplus
extern "C" {
#endif
void process_top(int n, ac_int<9, true> input[MAX], ac_int<9, false> output[MAX]);
#ifdef __cplusplus
}
#endif
#endif
