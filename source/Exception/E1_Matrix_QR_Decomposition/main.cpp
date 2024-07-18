#include "ac_qrd_tb.h"
#include <mc_scverify.h>
#include <mc_random.h>

#pragma hls_design top
void CCS_BLOCK(design)(
  input_type input,
  output_type &Q,
  output_type &R
)
{
#if defined (TEST_QRD_MATRIX_FIXED)
  ac_math::ac_qrd <ispwl_tb> (input, Q, R);
#elif defined (TEST_QRD_MATRIX_COMPLEX)
  ac_math::ac_qrd <real_diag_tb, ispwl_tb> (input, Q, R);
#endif
}



// Support functions for AC_FIXED
template<int input_width, int input_int, bool input_S, ac_q_mode input_Q, ac_o_mode input_O>
void double_to_type(
  const double double_value,
  ac_fixed<input_width, input_int, input_S, input_Q, input_O> &type_value)
{
  type_value = double_value;
}

template<int input_width, int input_int, bool input_S, ac_q_mode input_Q, ac_o_mode input_O>
double type_to_double(
  ac_fixed<input_width, input_int, input_S, input_Q, input_O> &type_value)
{
  return type_value.to_double();
}

// Support functions for AC_COMPLEX_AC_FIXED
template<int input_width, int input_int, bool input_S, ac_q_mode input_Q, ac_o_mode input_O>
void double_to_type(
  const ac_complex<double> double_value,
  ac_complex<ac_fixed<input_width, input_int, input_S, input_Q, input_O> > &type_value)
{
  double_to_type(double_value.r(), type_value.r());
  double_to_type(double_value.i(), type_value.i());
}

template<int input_width, int input_int, bool input_S, ac_q_mode input_Q, ac_o_mode input_O>
ac_complex<double> type_to_double(
  ac_complex<ac_fixed<input_width, input_int, input_S, input_Q, input_O> > &type_value)
{
  ac_complex<double> double_value;
  double_value.r() = type_to_double(type_value.r());
  double_value.i() = type_to_double(type_value.i());
  return double_value;
}

// Diagonal and Off-diagonal processing elements
template <typename T>
void diagonal_PE (T x, T y, T &c, T &s)
{
  T sqr;
  T root;
#if defined(TEST_QRD_MATRIX_FIXED)
  sqr = x*x + y*y;
#elif defined(TEST_QRD_MATRIX_COMPLEX)
  sqr = x.mag_sqr() + y.mag_sqr();
#endif
  root = sqrt(sqr);
  c = y/root;
  s = -x/root;
}

template<int M, typename T>
void offdiagonal_PE_tb (ac_matrix<T, M, 2*M> (&A), unsigned pivot, T c, T s, unsigned j)
{
  ac_matrix<T, 2, 1> row1;
  ac_matrix<T, 2, 1> row2;

#if defined(TEST_QRD_MATRIX_COMPLEX)
  T c_R = c.conj(), c2_R = c, s_R = s, s2_R = -s.conj(), c_Q = c, c2_Q = c.conj(), s_Q = s.conj(), s2_Q = -s;
#endif

  for (int i=0; i<2*M; i++) {
    row1(0,0) = A(pivot-1,i);
    row1(1,0) = A(pivot,i);
#if defined(TEST_QRD_MATRIX_FIXED)
    row2(0,0) = c*row1(0,0)-s*row1(1,0);
    row2(1,0) = c*row1(1,0)+s*row1(0,0);
#elif defined(TEST_QRD_MATRIX_COMPLEX)
    if (i < M) {
      row2(0,0) = c_R*row1(0,0)  + s2_R*row1(1,0);
      row2(1,0) = c2_R*row1(1,0) + s_R*row1(0,0);
      if (real_diag_tb && i == M - 1 && j == M - 2) {
        double arg_br = atan2(row2(1, 0).i(), row2(1, 0).r());
        row2(1, 0) = sqrt(row2(1, 0).mag_sqr());
        ac_complex<double> exp_arg_br(cos(-arg_br), sin(-arg_br));
        s_Q = (s_R*exp_arg_br).conj();
        c2_Q = (c2_R*exp_arg_br).conj();
      }
    } else {
      row2(0,0) = c_Q*row1(0,0)  + s2_Q*row1(1,0);
      row2(1,0) = c2_Q*row1(1,0) + s_Q*row1(0,0);
    }
#endif
    A(pivot-1,i) = row2(0,0);
    A(pivot,i) = row2(1,0);
  }
}

template <typename T>
void matrixmul_double (ac_matrix<T, M, M> &A, ac_matrix<T, M, M> &B, ac_matrix<T, M, M> &C)
{
  T sum = 0;
  for (unsigned i = 0; i<M; i++) {
    for (unsigned j = 0; j<M; j++) {
      for (unsigned k = 0; k<M; k++) {
        sum = sum + A(i,k) * B(k,j);
      }
      C(i,j) = sum;
      sum = 0;
    }
  }
}

template <int M, typename T>
void qrd_compute (ac_matrix<T, M, M> A, ac_matrix<T, M, M> (&Q), ac_matrix<T, M, M> (&R))
{
  T  c;
  T  s;
  T  s1;
  ac_matrix<T,M,2*M> A1;
  ac_matrix<T,M,M> ans = A;
  for (int i=0; i<M; i++) {
    for (int j=0; j<M; j++) {
      A1(i,j) = A(i,j);
      A1(i,j+M) = (j+M-i == M) ? 1: 0;
    }
  }

  for (int j=0; j<M; j++) {
    for (int k=M-1; k>j; k--) {
      diagonal_PE<T>(A1(k,j), A1(k-1,j), c, s);
      offdiagonal_PE_tb<M,T>(A1,k,c,s,j);
    }
  }

  for (int i=0; i<M; i++) {
    for (int j=0; j<M; j++) {
      Q(j,i) = A1(i,j+M);
      R(i,j) = A1(i,j);
    }
  }
}

class ExceptionHandler { //Need to insert an exception module to terminal other modules
}