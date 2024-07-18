# Establish the location of this script and use it to reference all
# other files in this example
set sfd [file dirname [info script]]

# Reset the options to the factory defaults
options defaults

options set Input/CompilerFlags -DTEST_QRD_MATRIX_COMPLEX
options set Input/CppStandard c++11

# Start a new project to have the above change take effect
project new

flow package require /SCVerify
flow package option set /SCVerify/USE_CCS_BLOCK true

# Configure C++ testbench options
flow package option set /SCVerify/INVOKE_ARGS  {3.0, 1.00}

set MGC_HOME [application get /SYSTEM/ENV_MGC_HOME]
flow package require /CCOV
flow package option set /CCOV/CCOV_EXCLUDE_ROUTINES {std::signbit std::fpclassify std::isfinite std::isnormal std::isinf std::isnan}
flow package option set /CCOV/TB_INVOKE_ARGS [flow package option get /SCVerify/INVOKE_ARGS]
# Explicitly set up coverage measures for the IP block itself
flow package option set /CCOV/CCOV_INCLUDE_FILES "$MGC_HOME/shared/include/ac_math/ac_qrd.h"
# Explicitly exclude the testbench itself from coverage measurement
flow package option set /CCOV/CCOV_EXCLUDE_FILES "$sfd/ac_qrd_tb.cpp $MGC_HOME/shared/include/ac_complex.h $MGC_HOME/shared/include/ac_math/ac_inverse_sqrt_pwl.h $MGC_HOME/shared/include/ac_matrix.h $MGC_HOME/shared/include/ac_math/ac_normalize.h $MGC_HOME/shared/include/ac_math/ac_shift.h $MGC_HOME/shared/include/ac_channel.h $MGC_HOME/shared/include/ac_int.h $MGC_HOME/shared/include/ac_fixed.h $MGC_HOME/shared/include/ac_dsp_utils.h"


# Add input files
solution file add [file join $sfd ac_qrd_tb.cpp]
go compile

# Load technology libraries
solution library add nangate-45nm_beh -- -rtlsyntool OasysRTL -vendor Nangate -technology 045nm
go libraries

directive set -CLOCKS {clk {-CLOCK_PERIOD 3.33}}
go assembly

directive set /design/core/IDENT_ROW -UNROLL yes
directive set /design/core/IDENT_COLUMN -UNROLL yes
directive set /design/core/SEPARATE_ROW -UNROLL yes
directive set /design/core/SEPARATE_COLUMN -UNROLL yes

go architect

go extract
# Verify C++ design with testbench
flow run /SCVerify/launch_make ./scverify/Verify_orig_cxx_osci.mk {} SIMTOOL=osci sim
# Verify RTL

# Flag to indicate SCVerify readiness
set can_simulate 1
