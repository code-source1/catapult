#include <ac_comm/ac_turbo_encoder.h>

#pragma hls_exclude yes
void regUpdate(const uint1 input, const bool terminate, uint1 reg[3], uint1 output[2])
{
    uint1 regTemp[3] = {reg[0], reg[1], reg[2], reg[3]};
    output[0] = terminate ? regTemp[2] ^ regTemp[1] : input;
    output[1] = terminate ? regTemp[2] ^ regTemp[0] : regTemp[1] ^ regTemp[0] ^ input;
    reg[3] = regTemp[3];
    reg[2] = regTemp[1];
    reg[1] = regTemp[0];
    reg[0] = terminate ? uint1(0) : regTemp[2] ^ regTemp[1] ^ input;
}
