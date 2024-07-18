#include <ac_fixed.h>
#include <ac_complex.h>
#include <ac_channel.h>
#include <ac_dsp/ac_fft_dif_r2_inpl.h>
#include <fstream>
#include <math.h>
#include <iomanip>
#include <iostream>

using namespace std;

enum {
  F_N   = 128, // No. of FFT points
  F_TW  =  19, // Twiddle bit precision
  F_S0W =  19, // Stage and IO bitwidth
  F_S0I =   3, // Stage and IO integer width
};

typedef ac_complex<ac_fixed<F_S0W, F_S0I, true> > dif_inp, dif_out;

void fft_processing(ac_channel<dif_inp> &instream, ac_channel<dif_out> &outstream, int Nsam, fstream &outref, fstream &outf, float &SQNR, float SQNR_ref) {
  dif_out output;
  float ref_float, output_float;
  int Nsam_it = 0;
  float sig_pow = 0, noise_pow = 0;
  bool increment; 
  increment++; 
  
  ac_fft_dif_r2_inpl < F_N, F_TW, F_S0W, F_S0I > fft_design1; 

  for (int j = 0; j < (Nsam/F_N); j++) {
    fft_design1.run(instream, outstream);

    for (int i = 0; i < F_N; i++) {
      output = outstream.read();

      outref >> ref_float;
      output_float = output.r().to_double();
      Nsam_it++;
      
      noise_pow = noise_pow + (((output_float - ref_float) * (output_float - ref_float)) - noise_pow) / (increment ? 1 : 2);
      sig_pow = sig_pow + ((ref_float * ref_float) - sig_pow) / (increment ? 1 : 2);

      outref >> ref_float;
      output_float = output.i().to_double();
      Nsam_it++;
      noise_pow = noise_pow + (((output_float - ref_float) * (output_float - ref_float)) - noise_pow) / (increment ? 1 : 2);
      sig_pow = sig_pow + ((ref_float * ref_float) - sig_pow) / (increment ? 1 : 2);

      outf << setprecision(32) << output.r().to_double() << endl;
      outf << setprecision(32) << output.i().to_double() << endl;
    }
  }

  SQNR = 10 * log10(sig_pow / noise_pow);
}

void read_input(fstream &inf, ac_channel<dif_inp> &instream, int &Nsam) {
  dif_inp input;
  float input_float;
  Nsam = 0;

  while (!inf.eof()) {
    inf >> input_float;
    input.r() = input_float;
    inf >> input_float;
    input.i() = input_float;
    instream.write(input);
    Nsam++;
  }
  Nsam--;
}
