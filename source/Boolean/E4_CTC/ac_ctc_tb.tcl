
set sfd [file dirname [info script]]
set MGC_HOME [application get /SYSTEM/ENV_MGC_HOME]

# Reset the options to the factory defaults
options defaults

# Start a new project for option changes to take place
project new

options set Input/CppStandard c++11

flow package require /SCVerify
flow package option set /SCVerify/USE_CCS_BLOCK true
flow package option set /SCVerify/INVOKE_ARGS "4000 . [file join $sfd in_image_0.bmp] [file join $sfd in_image_1.bmp] [file join $sfd in_image_2.bmp] [file join $sfd in_image_3.bmp] [file join $sfd in_image_4.bmp] [file join $sfd in_image_5.bmp] [file join $sfd in_image_6.bmp] [file join $sfd in_image_7.bmp]"

flow package require /CCOV
flow package option set /CCOV/TB_INVOKE_ARGS [flow package option get /SCVerify/INVOKE_ARGS]
# Explicitly set up coverage measures for the IP block itself
flow package option set /CCOV/CCOV_INCLUDE_FILES "$MGC_HOME/shared/include/ac_ipl/ac_ctc.h"
# Explicitly exclude the testbench itself from coverage measurement
flow package option set /CCOV/CCOV_EXCLUDE_FILES "$sfd/ac_ctc_tb.cpp $MGC_HOME/shared/include/ac_ipl/ac_pixels.h $MGC_HOME/shared/include/ac_math/ac_shift.h $MGC_HOME/shared/include/ac_math/ac_div.h $MGC_HOME/shared/include/bmpUtil/bmp_io.cpp $MGC_HOME/shared/include/ac_channel.h $MGC_HOME/shared/include/ac_int.h $MGC_HOME/shared/include/ac_fixed.h"

solution file add [file join $sfd ac_ctc_tb.cpp] -type C++
solution file add [file join $MGC_HOME shared include bmpUtil bmp_io.cpp] -exclude true
go analyze
solution library add nangate-45nm_beh -- -rtlsyntool OasysRTL -vendor Nangate -technology 045nm
go compile
go libraries
directive set -CLOCKS {clk {-CLOCK_PERIOD 5 -CLOCK_EDGE rising -CLOCK_UNCERTAINTY 0.0 -CLOCK_HIGH_TIME 2.5 -RESET_SYNC_NAME rst -RESET_ASYNC_NAME arst_n -RESET_KIND sync -RESET_SYNC_ACTIVE high -RESET_ASYNC_ACTIVE low -ENABLE_NAME {} -ENABLE_ACTIVE high}}
directive set -CLOCK_NAME clk
go assembly
go architect
go allocate
go schedule
go extract

