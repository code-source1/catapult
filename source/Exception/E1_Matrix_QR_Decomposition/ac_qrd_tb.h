#ifndef _INCLUDED_AC_QRD_TB_H_
#define _INCLUDED_AC_QRD_TB_H_

//Define the headers for which the QRD function implemented
#include <ac_fixed.h>
#include <ac_complex.h>

// Include specific header file
#include <ac_math/ac_qrd.h>

//Define the matrix dimension
const unsigned M = 3;
const int input_width = 16;
const int input_int = 8;
const int output_width = 64;
const int output_int = 32;
const bool real_diag_tb = false; // Flag to switch between output where all diagonal elements real vs. output with complex bottom-right diagonal element.
const bool ispwl_tb = true; // Flag to toggle usage of PWL functions.

// Define input and output types using typedefs
#if defined (TEST_QRD_MATRIX_FIXED)
  typedef ac_matrix <ac_fixed <input_width, input_int, true, AC_RND, AC_SAT>, M, M> input_type;
  typedef ac_matrix <ac_fixed <output_width, output_int, true, AC_RND, AC_SAT>, M, M> output_type;
#elif defined (TEST_QRD_MATRIX_COMPLEX)
  typedef ac_matrix <ac_complex <ac_fixed <input_width, input_int, true, AC_RND, AC_SAT> >, M, M> input_type;
  typedef ac_matrix <ac_complex <ac_fixed <output_width, output_int, true, AC_RND, AC_SAT> >, M, M> output_type;
#endif

// Function prototype
void design(
  input_type input, // input matrix
  output_type &Q,   // matrix for Q
  output_type &R    // matrix for R
);

#endif

