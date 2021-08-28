# Loop-Invariant-Synthesizer
This is the final project of the Software Synthesis and Automated Reasoning course

# Running Tests Benchmarks
The script for running the tests benchmarks can be invoked by running the main file and adding --tests to the script.

# Timeout Option
It is possible to provide a timeout for each input python program run, by adding "--time-out" (or '-t' for short), with default value of 8 minutes.
This option can be added regardless of run mode, meaning it can be added whether you are running the test benchmarks or using the tool with your personal inputs for your own run.

    python main.py --tests [-t NUM]

# The Input Format
To successfully run the tool on a python code, you need to provide the python code you wish to synthesis, the grammar (which must be a sub Grammar of the grammar found in [syntax.py](https://github.com/AbuJabal-Hussein/Loop-Invariant-Synthesizer/blob/dev/syntax.py) [^1] ), and conditions file, which can be used to prove properties. 
To successfully run: 

    python main.py --program <input program file> --grammar <Grammar file> --conditions <conditions file> [-t NUM]


[^1]:  Make sure you are on the latest version
<!--stackedit_data:
eyJoaXN0b3J5IjpbLTE0MDA5ODEyNDksMTQ1MDU0NTkxMiwxNT
M1Nzc3NTkyLDE5MDI4Mjk4MjcsMTQ4ODk3MzkwNywtMTEyNzYx
MzY5OCwtMTE3OTY1MTc4LC0xNTQ4NjA1ODY0XX0=
-->