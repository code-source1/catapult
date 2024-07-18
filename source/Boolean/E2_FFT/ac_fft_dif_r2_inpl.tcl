#------------------------------------------------------------
# FFT Decimation in Frequency Radix-2  In-place Example C++ Design
#------------------------------------------------------------

# Establish the location of this script and use it to reference all
# other files in this example
set sfd [file dirname [info script]]
set MGC_HOME [application get /SYSTEM/ENV_MGC_HOME]

# Reset the options to the factory defaults
options defaults

# Start a new project for option changes to take place
project new

flow package require /SCVerify
flow package option set /SCVerify/USE_CCS_BLOCK true
flow package option set /SCVerify/INVOKE_ARGS "[file join $sfd FFTIN.TXT] [file join $sfd FFTOUT.TXT] [file join $sfd REFOUT.TXT]"

flow package require /CCOV
flow package option set /CCOV/TB_INVOKE_ARGS [flow package option get /SCVerify/INVOKE_ARGS]
# Explicitly set up coverage measures for the IP block itself
set ip_files [file join [application get /SYSTEM/ENV_MGC_HOME] shared include ac_dsp ac_fft_dif_r2_inpl.h]
flow package option set /CCOV/CCOV_INCLUDE_FILES "$ip_files"
# Explicitly exclude the testbench itself from coverage measurement
flow package option set /CCOV/CCOV_EXCLUDE_FILES "$sfd/ac_fft_dif_r2_inpl_main_tb.cpp $MGC_HOME/shared/include/ac_complex.h $MGC_HOME/shared/include/ac_channel.h $MGC_HOME/shared/include/ac_fixed.h $MGC_HOME/shared/include/ac_int.h"

solution file add [file join $sfd ac_fft_dif_r2_inpl_main_tb.cpp] -type C++

go analyze

solution library add nangate-45nm_beh
solution library add ram_nangate-45nm-separate_beh
solution library add rom_nangate-45nm-sync_regout_beh
go libraries

directive set -CLOCKS {clk {-CLOCK_PERIOD 3.3333}}
go architect

ignore_memory_precedences -from *read_mem* -to *write_mem*
ignore_memory_precedences -from *write_mem* -to *read_mem*
go extract

# Flag to indicate SCVerify readiness
set can_simulate 1
