#ifndef _INCLUDED_AC_SQRT_H_
#define _INCLUDED_AC_SQRT_H_
#include <ac_int.h>
#include <ac_fixed.h>
#include <ac_float.h>
#include <ac_std_float.h>
#include <ac_math/ac_shift.h>

#if (defined(__GNUC__) && (__cplusplus < 201103L))
#error Please use C++11 or a later standard for compilation.
#endif
#if (defined(_MSC_VER) && (_MSC_VER < 1920) && !defined(__EDG__))
#error Please use Microsoft VS 2019 or a later standard for compilation.
#endif
namespace ac_math
{
  template< int XW, int OW, bool OS >
  void ac_sqrt(
    ac_int<XW,false> x,
    ac_int<OW,OS> &sqrt
  )
  {
    const int RW = (XW+1)/2;
    ac_int<RW+2, false> mask_d = 0;
    ac_int<RW+2, false> d = 0;
    ac_int<RW, false> r = 0;
    ac_int<2*RW, false> z = x;
    unsigned int z_shift = (RW-1)*2;
    for (int i = RW-1; i >= 0; i--) {
      r <<= 1;
      mask_d = (mask_d << 2) | 0x3;
      d = (mask_d & (d << 2)) | ((z >> z_shift) & 0x3 );
      ac_int<RW+2, false> t = (ac_int<RW+2, false>)(d - (( ((ac_int<RW+1, false>)r) << 1) | 0x1));
      if ( !t[RW+1] ) {
        r |= 0x1;
        d = mask_d & t;
      }
      z <<= 2;
    }
    sqrt = r;
  }
  template< int XW, int XI, ac_q_mode XQ, ac_o_mode XO,
            int OW, int OI, ac_q_mode OQ, ac_o_mode OO >
  void ac_sqrt(
    ac_fixed<XW,XI,false,XQ,XO> x,
    ac_fixed<OW,OI,false,OQ,OO> &sqrt
  )
  {
    const int RBIT = (OQ == AC_TRN || OQ == AC_TRN_ZERO) ? 0 : 1;
    const int OF = (OW-OI) + RBIT;
    const int RI = (XI+1)/2;
    #pragma hls_waive CNS
    if (RI-1 < -OF) {
      sqrt = 0.0;
      return;
    }
    const int RF = AC_MAX(OF, -RI+1);
    const int RW = RI + RF;
    const int ZF = 2*AC_MIN((XW-XI+1)/2, RF);
    const int ZW = 2*RI+ZF;
    ac_fixed<ZW,ZW,false> z_fx;
    ac_math::ac_shift_left(x, ZF, z_fx);
    ac_int<ZW,false> z = z_fx.template slc<ZW>(0);
    ac_int<RW+2,false> mask_d = 0;
    ac_int<RW+2,false> d = 0;
    ac_int<RW,false> r = 0;
    unsigned int z_shift = ZW-2;
    for (int i = RW-1; i >= 0; i--) {
      r <<= 1;
      mask_d = (mask_d << 2) | 0x3;
      d = (mask_d & (d << 2)) | ((z >> z_shift) & 0x3 );
      ac_int<RW+2,false> t = (ac_int<RW+2, false>)(d - (( ((ac_int<RW+1,false>)r) << 1) | 0x1));
      if ( !t[RW+1] ) {
        r |= 0x1;
        d = mask_d & t;
      }
      z <<= 2;
    }
    ac_fixed<RW+1,RW,false> r2 = (ac_fixed<RW+1,RW,false>) r;
    #pragma hls_waive CNS
    if (OQ == AC_RND_ZERO || OQ == AC_RND_MIN_INF || OQ == AC_RND_CONV ||  OQ == AC_RND_CONV_ODD) {
      bool rem = (d != 0) || ((z >> 2*RW) != 0);
      if (ZF < (XW-XI)) {
        const int rbits = AC_MAX((XW-XI)-ZF,1);
        ac_fixed<rbits,-ZF,false> zr = x;
        rem |= !! zr;
      }
      r2[0] =  rem ? 1 : 0;
    }
    ac_math::ac_shift_right(r2, RF, sqrt);
  }
  template<bool OR_TF = false,
           int TF_ = 32,
           ac_q_mode TQ = AC_TRN,
           int XW, int XI, int XE, ac_q_mode XQ,
           int OW, int OI, int OE, ac_q_mode OQ>
  void ac_sqrt(
    ac_float<XW,XI,XE,XQ> x,
    ac_float<OW,OI,OE,OQ> &sqrt
  )
  {
    #ifdef ASSERT_ON_INVALID_INPUT
    AC_ASSERT(x >= 0, "Negative input not supported.");
    #endif
    ac_fixed<XW, XI, false, XQ> x_mant = x.mantissa();
    x_mant <<= x.exp()[0];
    const int TF = OR_TF ? TF_ : OW - OI;
    const int TI = XI%2 == 0 ? XI/2 : (XI + 1)/2;
    ac_fixed<TF + TI, TI, false, TQ> sqrt_mant;
    ac_sqrt(x_mant, sqrt_mant);
    ac_float<OW, OI, OE, OQ> sqrt_temp(sqrt_mant, x.exp() >> 1, true);
    sqrt = sqrt_temp;
  }
  template<bool OR_TF = false,
           int TF_ = 32,
           ac_q_mode TQ = AC_TRN,
           int XW, int XE, int OW, int OE>
  void ac_sqrt(
    ac_std_float<XW, XE> x,
    ac_std_float<OW, OE> &sqrt
  )
  {
    ac_float<OW - OE + 1, 2, OE> sqrt_ac_fl;
    ac_sqrt<OR_TF, TF_, TQ>(x.to_ac_float(), sqrt_ac_fl);
    ac_std_float<OW, OE> sqrt_temp(sqrt_ac_fl);
    if (x == x.zero() && x.signbit()) {
      sqrt_temp.set_signbit(true);
    }
    #ifdef AC_SQRT_NAN_SUPPORTED
    else if (x.isnan() || x.signbit()) {
      sqrt_temp = sqrt_temp.nan();
      sqrt_temp.set_signbit(x.signbit());
    }
    #endif
    sqrt = sqrt_temp;
  }
  template<bool OR_TF = false,
           int TF_ = 32,
           ac_q_mode TQ = AC_TRN,
           ac_ieee_float_format Format,
           ac_ieee_float_format outFormat>
  void ac_sqrt(
    ac_ieee_float<Format> x,
    ac_ieee_float<outFormat> &sqrt
  )
  {
    typedef ac_ieee_float<outFormat> T_out;
    const int OW = T_out::width;
    const int OE = T_out::e_width;
    ac_float<OW - OE + 1, 2, OE> sqrt_ac_fl;
    ac_sqrt<OR_TF, TF_, TQ>(x.to_ac_float(), sqrt_ac_fl);
    ac_ieee_float<outFormat> sqrt_temp(sqrt_ac_fl);
    if (x == x.zero() && x.signbit()) {
      sqrt_temp.set_signbit(true);
    }
    #ifdef AC_SQRT_NAN_SUPPORTED
    else if (x.isnan() || x.signbit()) {
      sqrt_temp = sqrt_temp.nan();
      sqrt_temp.set_signbit(x.signbit());
    }
    #endif
    sqrt = sqrt_temp;
  }
}
#endif
