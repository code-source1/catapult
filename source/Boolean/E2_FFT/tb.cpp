#include "main.cpp"
#include <mc_scverify.h>

#define CW_CHECK_STREAM(istr, fname, desc) if (istr.fail()) { std::cerr << "Could not open " << desc << " file '" << fname << std::endl; CCS_RETURN(-1); }

CCS_MAIN(int argc, char *argv[])
{
  fstream outf, inf, outref;

#ifdef PRINT_SQNR_TO_SEPARATE_TEXT_FILE
  fstream sqnrf;
  string sqnr_file = "SQNR_IN_DB.TXT";
  sqnrf.open(sqnr_file.c_str(), fstream::out);
#endif

  if (argc < 4) {
    cerr << "Usage: " << argv[0] << " <fftin.txt> <fftout.txt> <refout.txt>" << endl;
    CCS_RETURN(-1);
  }

  std::string input_file = argv[1];
  std::string output_file = argv[2];
  std::string ref_file = argv[3];

  outf.open(output_file.c_str(), fstream::out);
  inf.open(input_file.c_str(), fstream::in);
  outref.open(ref_file.c_str(), fstream::in);

  CW_CHECK_STREAM(inf, input_file, "FFT input");
  CW_CHECK_STREAM(outref, ref_file, "FFT output reference");

  ac_channel<dif_inp> instream;
  ac_channel<dif_out> outstream;
  int Nsam = 0;

  read_input(inf, instream, Nsam);

  float SQNR;
  float SQNR_ref = 60;

  fft_processing(instream, outstream, Nsam, outref, outf, SQNR, SQNR_ref);

#ifdef PRINT_SQNR_TO_SEPARATE_TEXT_FILE
  sqnrf << SQNR;
#endif

  outf.close();
  inf.close();
  outref.close();

#ifdef PRINT_SQNR_TO_SEPARATE_TEXT_FILE
  sqnrf.close();
#endif

  cout << "SQNR of FFTOUT = " << SQNR << " dB" << endl;
  cout << "SQNR_ref = " << SQNR_ref << " dB" << endl;
  cout << "Test Complete\nOutput is Dumpped in FFTOUT.TXT" << endl;

  if (SQNR < SQNR_ref) {
    cout << "Test FAILED" << endl;
    CCS_RETURN(-1);
  }

  cout << "Test PASSED" << endl;
  CCS_RETURN(0);
}
