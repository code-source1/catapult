set sfd [file dirname [info script]]
set MGC_HOME [application get /SYSTEM/ENV_MGC_HOME]

options defaults
options set /Input/CppStandard c++11

project new

flow package require /SCVerify
flow package option set /SCVerify/USE_CCS_BLOCK true

flow package require /CCOV
flow package option set /CCOV/TB_INVOKE_ARGS [flow package option get /SCVerify/INVOKE_ARGS]
# Explicitly set up coverage measures for the IP block itself
flow package option set /CCOV/CCOV_INCLUDE_FILES "$MGC_HOME/shared/include/ac_comm/ac_turbo_encoder.h"
# Explicitly exclude the testbench itself from coverage measurement
flow package option set /CCOV/CCOV_EXCLUDE_FILES "$sfd/ac_turbo_encoder_tb.cpp $MGC_HOME/shared/ac_fixed.h $MGC_HOME/shared/include/ac_channel.h $MGC_HOME/shared/include/ac_int.h"

solution file add [file join $sfd ac_turbo_encoder_tb.cpp]

directive set -MEM_MAP_THRESHOLD 32

solution library add nangate-45nm_beh -- -rtlsyntool OasysRTL -vendor Nangate -technology 045nm
solution library add ram_nangate-45nm-singleport_beh
solution library add rom_nangate-45nm_beh

go libraries

directive set -CLOCKS {clk {-CLOCK_PERIOD 3.33 -CLOCK_EDGE rising -CLOCK_HIGH_TIME 1.665 -CLOCK_OFFSET 0.000000 -CLOCK_UNCERTAINTY 0.0 -RESET_KIND sync -RESET_SYNC_NAME rst -RESET_SYNC_ACTIVE high -RESET_ASYNC_NAME arst_n -RESET_ASYNC_ACTIVE low -ENABLE_NAME {} -ENABLE_ACTIVE high}}

go assembly
go architect
go allocate
go extract
