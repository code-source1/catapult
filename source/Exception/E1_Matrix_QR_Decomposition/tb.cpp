#include "main.cpp"
#include <ac_complex.h>
#include <stdlib.h>
#include <iostream>

#define USE_MATH_DEFINES
#include <math.h>

using namespace std;

#ifndef __SYNTHESIS__

CCS_MAIN(int argc, char *argv[])
{
  double lower_limit, upper_limit, step, allowed_magnitude_error, allowed_angle_error;
  cout << "============ ac_qrd test ==================" << endl;
  if ( argc < 3 ) {
    cout << "Warning: using default testbench ranges" << endl;
    allowed_magnitude_error = 3.0;
    allowed_angle_error = 3.0;
  } else {
    allowed_magnitude_error = atof(argv[1]);
    allowed_angle_error = atof(argv[2]);
  }
  cout << "allowed_magnitude_error  = " << allowed_magnitude_error << endl;
  cout << "allowed_angle_error  = " << allowed_angle_error << endl;
  cout << endl;
  double max_error = 0;
  double this_error = 0;

#if defined (TEST_QRD_MATRIX_FIXED)
  typedef ac_matrix <double, M, M> matrix_double;
  typedef double double_type;
#elif defined (TEST_QRD_MATRIX_COMPLEX)
  typedef ac_matrix <ac_complex <double>, M, M> matrix_double;
  typedef ac_complex <double> double_type;
#endif

  input_type input;
  output_type output1;
  output_type output2;

  double this_magnitude_error, max_magnitude_error;
  double this_angle_error, max_angle_error;

  max_magnitude_error = 0.00;
  max_angle_error = 0.00;

  matrix_double input_double;
  matrix_double expected_value_Q;
  matrix_double expected_value_R;
  matrix_double actual_value_Q;
  matrix_double actual_value_R;
  matrix_double recovered_mat;

  int xxx = 0;
  int yyy = 0;
  for (unsigned p = 0 ; p < M ; p++) {
    for (unsigned q = 0; q < M; q++) {
#if defined(RANDOM_INPUT)
#if defined(TEST_QRD_MATRIX_FIXED)
      mc_random (input(p,q));
#elif defined(TEST_QRD_MATRIX_COMPLEX)
      mc_random (input(p,q).r());
      mc_random (input(p,q).i());
#endif
#else
#if defined(TEST_QRD_MATRIX_FIXED)
      input(p,q) = xxx;
      xxx = xxx + 4 + p;
#elif defined(TEST_QRD_MATRIX_COMPLEX)
      input(p,q).r() = xxx;
      xxx++;
      yyy = xxx*p*(q-1)+10;
      input(p,q).i() = yyy;
      xxx = xxx+3+p;
#endif
#endif
      input_double(p,q) = type_to_double(input(p,q));
    }
  }

  CCS_DESIGN(design)(input, output1, output2);
  qrd_compute<M, double_type>(input_double, expected_value_Q, expected_value_R);

  for (unsigned i = 0; i < M; i++) {
    for (unsigned j = 0; j < M; j++) {
      actual_value_Q(i,j) = type_to_double(output1(i,j));
      actual_value_R(i,j) = type_to_double(output2(i,j));
    }
  }

  matrixmul_double<double_type>(actual_value_Q, actual_value_R, recovered_mat);

  matrix_double expected_Q_ct, expected_Q_prod;
  double max_unit_mat_error = 0;

#ifdef TEST_QRD_MATRIX_FIXED

  for (unsigned i = 0; i < M; i++) {
    for (unsigned j = 0; j < M; j++) {
      this_magnitude_error = (abs(input_double(i,j) - recovered_mat(i,j)) / input_double(i,j)) * 100;
      if (abs(input_double(i,j) - recovered_mat(i,j)) < 0.002 && this_magnitude_error > 1) {
        this_magnitude_error = abs((input_double(i,j) / recovered_mat(i,j)) - 1);
      }
      if (this_magnitude_error > max_magnitude_error) {
        max_magnitude_error = this_magnitude_error;
      }
    }
  }

#else

#ifdef TEST_QRD_MATRIX_COMPLEX
  double actual_angle, expected_angle, actual_magnitude, expected_magnitude;
  for (unsigned i = 0; i < M; i++) {
    for (unsigned j = 0; j < M; j++) {
      actual_angle = atan(recovered_mat(i,j).r() / recovered_mat(i,j).i());
      expected_angle = atan(input_double(i,j).r() / input_double(i,j).i());
      this_angle_error = abs(expected_angle - actual_angle) * M_PI / 180;

      actual_magnitude = recovered_mat(i,j).r()*recovered_mat(i,j).r() + recovered_mat(i,j).i()*recovered_mat(i,j).i();
      expected_magnitude = input_double(i,j).r()*input_double(i,j).r() + input_double(i,j).i()*input_double(i,j).i();
      this_magnitude_error = (abs(actual_magnitude - expected_magnitude) / expected_magnitude) * 100;
      if (abs(actual_magnitude - expected_magnitude) < 0.005 && this_magnitude_error > 0.2) {
        this_magnitude_error = abs((expected_magnitude / actual_magnitude) - 1);
      }

      if (this_magnitude_error > max_magnitude_error) {
        max_magnitude_error = this_magnitude_error;
      }
      if (this_angle_error > max_angle_error) {
        max_angle_error = this_angle_error;
      }
    }
  }
#endif

#endif

#ifdef TEST_QRD_MATRIX_FIXED
  cout << "Input given to the model = " << input << endl;
  cout << "Input given to the testbench = " << input_double << endl;
  cout << "Q output of the model = " << output1 << endl;
  cout << "Q output of the testbench = " << expected_value_Q << endl;
  cout << "R output of the model = " << output2 << endl;
  cout << "R output of the testbench = " << expected_value_R << endl;
  cout << "Recovered value of input matrix = " << recovered_mat << endl;
  cout << "Highest error = " << max_magnitude_error << endl;
#else
#ifdef TEST_QRD_MATRIX_COMPLEX
  cout << "Input given to the model = " << input << endl;
  cout << "Input given to the testbench = " << input_double << endl;
  cout << "Q output of the model = " << output1 << endl;
  cout << "Q output of the testbench = " << expected_value_Q << endl;
  cout << "R output of the model = " << output2 << endl;
  cout << "R output of the testbench = " << expected_value_R << endl;
  cout << "Recovered value of input matrix = " << recovered_mat << endl;
  cout << "Highest angle error = " << max_angle_error << endl;
  cout << "Highest magnitude error = " << max_magnitude_error << endl;
#endif
#endif

  if (max_magnitude_error > allowed_magnitude_error) {
    cout << "Error tolerance of " << allowed_magnitude_error << " percent error exceeded - FAIL" << endl;
    CCS_RETURN(-1);
  }
#ifdef TEST_QRD_MATRIX_COMPLEX
  if (max_angle_error > allowed_angle_error) {
    cout << "Error tolerance of " << allowed_angle_error << " degree exceeded in angle- FAIL" << endl;
    CCS_RETURN(-1);
  }
#endif
  cout << "Testbench finished" << endl;
  CCS_RETURN(0);
}
#endif

