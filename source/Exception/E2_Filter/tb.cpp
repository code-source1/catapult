#include "main.cpp"
#include <mc_scverify.h>
#include <iostream>
#include <fstream>

using namespace std;

CCS_MAIN(int argc, char *argv[])
{
  fstream outf;
  outf.open("./gcc_log.dat", fstream::out);

  ac_channel<IN_TYPE> fixed_in;
  ac_channel<OUT_TYPE> fixed_out;
  ac_channel<ac_int<16, false>> n_sample;
  IN_TYPE in;
  bool pass;
  unsigned int error_count = 0;
  ac_int<16, false> in_t;
  IntegrationDump i_d_inst;

  for (int j = 1; j < CONFIG; j++) {
    IN_TYPE cnt = 0;
    ac_int<16, false> N1 = rand() % 1023;
    n_sample.write(N1);
    
    for (int inread = 0; inread < N1; inread++) {
      in_t = rand() % 900;
      for (int i = 0; i < CHN; i++) {
        in = in_t;
        fixed_in.write(in);
      }
      cnt = cnt + in_t;
    }
    
    i_d_inst.run(fixed_in, fixed_out, n_sample);
    pass = true;
    
    for (int i = 0; i < CHN; i++) {
      OUT_TYPE fixed_data_out = fixed_out.read();
      ac_int<16, false> temp = fixed_data_out.to_double();
      
      if (temp != cnt) {
        pass = false;
        cout << "@ERROR! data_mismatch in Channel " << i << " expected: " << cnt << " received: " << temp << endl;
        ++error_count;
      }
    }
    
    if (pass) {
      cout << "Config " << j << " PASS" << endl;
      outf << "Config " << j << " PASS" << endl;
    } else {
      cout << "Config " << j << " FAIL" << endl;
      outf << "Config " << j << " FAIL" << endl;
    }
    
    pass = true;
  }

  outf.close();
  CCS_RETURN(error_count);
}
