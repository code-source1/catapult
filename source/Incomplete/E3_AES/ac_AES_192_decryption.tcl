# Establish the location of this script and use it to reference all
# other files in this example
set sfd [file dirname [info script]]

options defaults
options set /Input/CppStandard c++11
options set Input/CompilerFlags {-D AES_192}

project new

flow package require /SCVerify
flow package option set /SCVerify/USE_CCS_BLOCK true
flow package option set /SCVerify/INVOKE_ARGS [file join $sfd message.txt]
flow package option set /SCVerify/INVOKE_ARGS [file join $sfd message.txt]

# CCOV settings
set MGC_HOME [application get /SYSTEM/ENV_MGC_HOME]
flow package require /CCOV
# Explicitly set up coverage measures for the IP block itself
flow package option set /CCOV/CCOV_INCLUDE_FILES $MGC_HOME/shared/include/ac_comm/ac_aes.h
# Explicitly exclude the testbench itself from coverage measurement
flow package option set /CCOV/CCOV_EXCLUDE_FILES [list $sfd/ac_aes_tb.cpp $MGC_HOME/shared/include/ac_fixed.h $MGC_HOME/shared/include/ac_channel.h $MGC_HOME/shared/include/ac_int.h]
flow package option set /CCOV/TB_INVOKE_ARGS [flow package option get /SCVerify/INVOKE_ARGS]

solution file add [file join $sfd ac_aes_tb.cpp] -type C++
solution design set ac_aes_decrypt<192> -top

solution library add nangate-45nm_beh -- -rtlsyntool OasysRTL -vendor Nangate -technology 045nm
solution library add rom_nangate-45nm_beh

go libraries
directive set -CLOCKS {clk {-CLOCK_PERIOD 4.0 -CLOCK_EDGE rising -CLOCK_UNCERTAINTY 0.0 -CLOCK_HIGH_TIME 2.0 -RESET_SYNC_NAME rst -RESET_ASYNC_NAME arst_n -RESET_KIND sync -RESET_SYNC_ACTIVE high -RESET_ASYNC_ACTIVE low -ENABLE_ACTIVE high}}
go assembly
go architect
go extract
#flow run /SCVerify/launch_make ./scverify/Verify_concat_sim_rtl_v_msim.mk {} SIMTOOL=msim sim
