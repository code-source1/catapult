# LLM-Driven Program Repair Framework for High-Level Synthesis

## Introduction
In High-Level Synthesis (HLS), converting a standard C/C++ program into an HLS-compatible version (HLS-C) requires significant manual effort. Our LLM-driven program repair framework aims to automate this process by taking regular C/C++ code as input and generating its corresponding HLS-C code ready for synthesis.

## Setup
To utilize this framework, you need to add specific Python scripts to your directory containing the regular C/C++ program. These scripts facilitate the repair and interaction between the LLM and the Catapult HLS tool.

### Scripts Description
- `emb.py`: Matches repair templates in the repair library.
- `compile.py`: Use this script to run your program as usual.
- `inter_compile.py`: Automates the interaction for repairing regular C code using the LLM.
- `run.py`: Uses the LLM to attempt multiple repairs on the C code.

## Usage
Execute the following commands in your terminal to interact with the system:
- To run your program normally:  

- To initiate LLM-driven repair on the C code:  

## Configuration
Modify the following paths in the scripts according to your environment setup:
- `tcl_script_path`: Path to your TCL script for running Catapult HLS.  
Example: `/path/to/your/run_catapult.tcl`
- `log_file_path`: Path where the Catapult log will be stored.  
Example: `/path/to/your/catapult.log`
- `base_dir`: Base directory for different HLS design instances.  
Example: `/path/to/your/E3_BFS`
- `command`: Command to invoke your installed design compiler.  
Example: `/path/to/synopsys/syn/J-2014.09-SP3/bin/dc_shell -f /path/to/your/tcl_script`
- `catapult_bin`: Directory path to your installed Catapult HLS tool.  
Example: `/path/to/catapult/2022.2-1008433/Mgc_home/bin`

Ensure these paths are correctly set to match your local environment.

## Conclusion
This framework leverages LLMs to simplify the conversion of C/C++ code to HLS-compatible code, thereby enhancing the efficiency of HLS workflows.
