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
In addition, you may like to provide the synthesizer with extra examples (unreachable states) to narrow down the invariant search, the examples files serves for that.
To successfully run: 

    python main.py --program <input program file> --grammar <Grammar file> --conditions <conditions file> [-t NUM] [--examples-file <examples files>]
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

1)

    pre_cond : True
    post_cond : isPalindrome == True

2)  
``` 
    pre_cond : True
    post_cond : all([myList[i] == str1[i] for i in [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]) and (myList[47] == 'program')
 ```

### The Examples File:
You can provide unreachable states to the synthesizer, to narrow down the invariant search. It can be done by writing states in the examples file.
The name convention to follow when using in **tests/benchmarks**: `examples_test<number>`  eg. `examples_test1` 
While the states format (the 'syntax' inside the file) should follow the convention (please cover all the input python code's variables in each state(row)):
var_name type value\<unprintable character>var_name type value\<unprintable character>\<unprintable character>\<True or False> 

    i int 6x int 20y int 0False
    i int 0x int 16y int 0True
**Note**: Make sure you copy the examples from the code segment above, as there is unprintable separator between the tuples.
_You can take a look at [benchmarks/integers_benchmarks/examples_test2](https://github.com/AbuJabal-Hussein/Loop-Invariant-Synthesizer/blob/dev/benchmarks/integers_benchmarks/examples_test2)_  <= 
[^1]:  Make sure you are on the latest version


# Design and Implementation

Our tool can either be run in tests mode, or your own run mode, either case, when running a test case or your own run, we use a wrapper, which prepares the required data -such as the conditions and both the positive and negative examples-, and passes it to the two main parts of the tool Bottom up class, and VC_Generation class, where the magic happens and new invariant candidates are born and sent back to the wrapper. The wrapper is responsible for the final check of the invariant candidates before the true invariant that passes the Horn constraints is sent into the world.

## Bottom Up Class
Prior to the bottom up  enumeration on the grammar to find the invariant, the class extracts the used variables in the input python code, to minimize creation or irrelevant variant candidates in the grow stage of the bottom up enumeration.
In addition, the bottom up class is responsible for the timing out while creating and checking different variant candidates.
In addition, the Bottom up class parses the states created by the \_\_inv()__ function.
The Bottom up class uses VC_Generation to translate string invariant candidates into z3 objects.

### Bottom Up Enumeration
A list of variables, operations, function names and different tokens and terminals is prepared which will be used in every iteration of grow added to what was created before 
<!--stackedit_data:
eyJoaXN0b3J5IjpbMTg2NTM2OTMxNywtMTg0NDI5NzI2Niw4Mj
M1MTU1MzQsOTQ2MjE4NzA2LDE0NTA1NDU5MTIsMTUzNTc3NzU5
MiwxOTAyODI5ODI3LDE0ODg5NzM5MDcsLTExMjc2MTM2OTgsLT
ExNzk2NTE3OCwtMTU0ODYwNTg2NF19
-->