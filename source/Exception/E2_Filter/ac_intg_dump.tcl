#------------------------------------------------------------
# CIC load coeffs Filter Example C++ Design
#------------------------------------------------------------

# Establish the location of this script and use it to reference all
# other files in this example
set sfd [file dirname [info script]]
set tkd [file dirname $sfd]
set MGC_HOME [application get /SYSTEM/ENV_MGC_HOME]

# Reset the options to the factory defaults
options defaults

# Start a new project
project new

flow package require /SCVerify
flow package option set /SCVerify/USE_CCS_BLOCK true
flow package option set /SCVerify/INVOKE_ARGS $sfd 

flow package require /CCOV
flow package option set /CCOV/TB_INVOKE_ARGS [flow package option get /SCVerify/INVOKE_ARGS]
# Explicitly set up coverage measures for the IP block itself
set ip_files [file join [application get /SYSTEM/ENV_MGC_HOME] shared include ac_dsp ac_intg_dump.h]
flow package option set /CCOV/CCOV_INCLUDE_FILES "$ip_files"
# Explicitly exclude the testbench itself from coverage measurement
flow package option set /CCOV/CCOV_EXCLUDE_FILES "$sfd/ac_intg_dump_main_tb.cpp $MGC_HOME/shared/include/ac_channel.h $MGC_HOME/shared/include/ac_fixed.h $MGC_HOME/shared/include/ac_int.h"

solution file add [file join $sfd ac_intg_dump_main_tb.cpp] -type C++

directive set -REGISTER_IDLE_SIGNAL false
directive set -IDLE_SIGNAL {}
directive set -TRANSACTION_DONE_SIGNAL true
directive set -DONE_FLAG {}
directive set -START_FLAG {}
directive set -FSM_ENCODING none
directive set -REG_MAX_FANOUT 0
directive set -NO_X_ASSIGNMENTS true
directive set -SAFE_FSM false
directive set -RESET_CLEARS_ALL_REGS true
directive set -ASSIGN_OVERHEAD 0
directive set -DESIGN_GOAL area
directive set -CSA 0
directive set -TIMING_CHECKS true
directive set -REALLOC true
directive set -PIPELINE_RAMP_UP true
directive set -COMPGRADE fast
directive set -SPECULATE true
directive set -MERGEABLE true
directive set -REGISTER_THRESHOLD 256
directive set -MEM_MAP_THRESHOLD 32
directive set -UNROLL no
directive set -CLOCK_OVERHEAD 20.000000
directive set -OPT_CONST_MULTS -1
go analyze

solution library add nangate-45nm_beh
go libraries

directive set -CLOCK_NAME clk
directive set -CLOCKS {clk {-CLOCK_PERIOD 2.5 -CLOCK_EDGE rising -CLOCK_UNCERTAINTY 0.0 -CLOCK_HIGH_TIME 1.25 -RESET_SYNC_NAME rst -RESET_ASYNC_NAME arst_n -RESET_KIND sync -RESET_SYNC_ACTIVE high -RESET_ASYNC_ACTIVE low -ENABLE_NAME {} -ENABLE_ACTIVE high}}
go architect
go extract

# Flag to indicate SCVerify readiness
set can_simulate 1
