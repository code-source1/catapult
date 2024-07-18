#include <ac_fixed.h>
#include <ac_channel.h>
#include <ac_int.h>
#include <ac_dsp/ac_intg_dump.h>

using namespace std;

enum {
  CONFIG = 25,
  NS  = 1024,
  CHN = 4
};

typedef ac_int<16, false> N_TYPE;
typedef ac_fixed<25, 15, false> IN_TYPE;
typedef ac_fixed<60, 15, false> ACC_TYPE;
typedef ac_fixed<30, 15, false> OUT_TYPE;

class ExceptionHandler { 
}

class IntegrationDump {
public:
  void run(ac_channel<IN_TYPE>& fixed_in, ac_channel<OUT_TYPE>& fixed_out, ac_channel<ac_int<16, false>>& n_sample) {
    ac_intg_dump<IN_TYPE, ACC_TYPE, OUT_TYPE, N_TYPE, NS, CHN> i_d_inst;
    i_d_inst.run(fixed_in, fixed_out, n_sample);
  }
};
