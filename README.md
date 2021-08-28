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
### The input program:
The input program needs to have at most 1 loop. A call to \___inv_\__() must be added, while the arguments are each variable used as follows:
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; _- Assuming a,b,c are the used variables in the code -_

    __inv__(a=a, b=b, c=c)
### The grammar:
As mentioned before, it must be a sub grammar of the grammar found in synatx.py.
_Make sure it isn't written as string (no quotes: ' or  "). Take a look at [grammar.py](https://github.com/AbuJabal-Hussein/Loop-Invariant-Synthesizer/blob/dev/benchmarks/integers_benchmark/grammar) [^1] for a clearer image._
### The Conditions File:
The conditions files must follow the following format:

    pre_cond : <cond>
    post_cond : <cond>
Examples: 

1) ```    
    pre_cond : True
    post_cond : all([myList[i] == str1[i] for i in [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]) and (myList[47] == 'program')
    ```

2)  ```    
    pre_cond : True
    post_cond : all([myList[i] == str1[i] for i in [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]) and (myList[47] == 'program')
    ```

[^1]:  Make sure you are on the latest version
<!--stackedit_data:
eyJoaXN0b3J5IjpbLTk2NTMwNjY3Miw4MjM1MTU1MzQsOTQ2Mj
E4NzA2LDE0NTA1NDU5MTIsMTUzNTc3NzU5MiwxOTAyODI5ODI3
LDE0ODg5NzM5MDcsLTExMjc2MTM2OTgsLTExNzk2NTE3OCwtMT
U0ODYwNTg2NF19
-->