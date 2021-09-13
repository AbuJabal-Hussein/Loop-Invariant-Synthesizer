

# Loop-Invariant-Synthesizer
This is the final project of the Software Synthesis and Automated Reasoning course

# Running Tests Benchmarks
The script for running the tests benchmarks can be invoked by running the main file and adding --tests to the script.

# Timeout Option
It is possible to provide a timeout for each input python program run, by adding "--time-out" (or '-t' for short), with default value of **8 minutes**.
This option can be added regardless of run mode, meaning it can be added whether you are running the test benchmarks or using the tool with your personal inputs for your own run.

    python main.py --tests [-t NUM]

# The Input Format
To successfully run the tool on a python code, you need to provide the python code you wish to synthesis, the grammar (which must be a sub Grammar of the grammar found in `syntax.py`), and conditions file, which can be used to prove properties. 
In addition, you may like to provide the synthesizer with extra examples (unreachable states) to narrow down the invariant search, the examples files serves for that.
To successfully run: 

    python main.py --program <input program file> --grammar <Grammar file> --conditions <conditions file> [-t NUM] [--examples-file <examples files>]
### The input program:
The input program needs to have at most 1 loop. A call to \___inv_\__() must be added, while the arguments are each variable used as follows:
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; _- Assuming a,b,c are the used variables in the code -_

    __inv__(a=a, b=b, c=c)
### The grammar:
As mentioned before, it must be a sub grammar of the grammar found in synatx.py.
_Make sure it isn't written as string (no quotes: ' or  "). Take a look at grammar.py for a clearer image._
### The Conditions File:
When writing tests (and run them using our script), the conditions file name should follow the convention:  `conditions_<test name>`  eg. `conditions_test1_ints`
The conditions file must follow the following format:

    pre_cond : <cond>
    post_cond : <cond>
Examples: 
```
1)
    pre_cond : True
    post_cond : isPalindrome == True
```
```
2)  
    pre_cond : True
    post_cond : all([myList[i] == str1[i] for i in range(10))
 ```

### The Examples File:
You can provide unreachable states to the synthesizer, to narrow down the invariant search. It can be done by writing states in the examples file.
The name convention to follow when using in **tests/benchmarks**: `examples_<test name>`  eg. `examples_test1_ints` 
While the states format (the 'syntax' inside the file) should follow the convention (please cover all the input python code's variables in each state(row)):
var_name type value\<unprintable character>var_name type value\<unprintable character>\<unprintable character>\<True or False> 

    i int 6x int 20y int 0False
    i int 0x int 16y int 0True
**Note**: Make sure you copy the examples from the code segment above, as there is unprintable separator between the tuples.
 
 

# Design and Implementation

Our tool can either be run in tests mode, or your own run mode, either case, when running a test case or your own run, we use a wrapper, which prepares the required data -such as the conditions and both the positive and negative examples-, and passes it to the two main parts of the tool Bottom up class, and VC_Generation class, where the magic happens and new invariant candidates are born and sent back to the wrapper. The wrapper is responsible for the final check of the invariant candidates before the true invariant that passes the Horn constraints is sent into the world.

## Bottom Up Class
Prior to the bottom up  enumeration on the grammar to find the invariant, the class extracts the used variables in the input python code, to minimize creation or irrelevant variant candidates in the grow stage of the bottom up enumeration.
In addition, the bottom up class is responsible for the timing out while creating and checking different variant candidates.
The Bottom up class parses the states created by the \_\_inv()__ function, and uses VC_Generation to translate string invariant candidates into z3 objects in different stages of the algorithm.

### Bottom Up Enumeration
A list of variables, operations, function names and different tokens and terminals is prepared which will be used in the grow step in every iteration.
Inside the loop, we start with the grow step, to produce more invariant candidates by iterating over each previously created candidate and placing it in a suitable terminal/non-terminal in the rhs of a rule to produce a lhs using other previously created candidates or starting terminal, etc.
Once a candidate is used in all possible slots, it is removed from further uses to prevent duplicates, as possible.
Afterwards, to reduce the size of the batch that eliminate will have to work on, the batch produced by grow is filtered, by trying to build ast of the variant candidate and then converting it to a z3 object, to drop meaningless code and trivial variants. This part is done in **parallel** using **multiprocessing**.
The remaining candidates are then passed to eliminate the equivalent pairs (or more) of them, this is also done in parallel, where for each element, we iterate on the batch and keep only the candidates unequal to the current element, and so on.
After all that, the remaining unique candidates are tested against the states, positive and the negative examples, if it produces sat and/or unsat as expected, it is tagged and yielding back (along with the tagged version) to the wrapper for the last check, and if it passes, then we found our invariant. 
Otherwise, we check the next candidate and so on until all of them failed the wrapper's checks, so we go to the next iteration, and so on.

## VC_Generation Class
The main purpose of this class is to generate Z3 verification conditions (VC) given a python program or statement. The python program/statement must be derivable from the standard python grammar, and also derivable from our custom sub-grammar, which is found in the file `syntax.py` in the `PythonParser` class. We will describe this sub-grammar in words in the following section.
####How does it work?
The VC_Generator uses a parser to decompose the python input code into statements and expressions, and then, it recursively converts these statements into Z3 verification conditions.  
The generator returns a 4-element-tuple which contains, in this order:  
1. VC of the code before the ‘while’ loop
2. VC of the loop condition
3. VC of the loop body
4. VC of the code after the loop

# Description of the used python grammar:
The grammar follows the following constraints:  
-	Supported types: int, str, bool, list  
-	Literal expressions for each type:  
    o&nbsp;&nbsp;int: numbers or signed numbers  
    o&nbsp;&nbsp;bool: *True*/*False*  
    o&nbsp;&nbsp;str: *'some text'* or *"some text"*  
    o&nbsp;&nbsp;list: *[element1, element2, ...]*  
-	Variable assignments: (=, +=, -=, \*=, /=, \*\*=)  
-	Relation operations: (<, >, <=, >=, ==, !=), (and, or, not) . It is recommended to wrap the operators’ sides with parenthesis, since the grammar does not fully support operators’ priorities.  
-	Basic integer arithmetic operations, i.e. (+, -, \*, /, %, \*\*)  
-	String concatenation operation using the ‘+’ operator.  
-	String indexing using brackets: *str1[i]*  
-	List element accessing using brackets: *lst[i]*  
-	Lists must be homogeneous, i.e., all its elements must be of the same type.  
-	List comprehension: *[exp1 for id1 in exp2]* s.t. exp1 is an expression, exp2 is a list, id1 is a temporary variable of the same type of the exp2 elements.  
-	The grammar accepts indentation up to 5 indents.  
-	Indents must be 'real' tabs and cannot be spaces.  
-	Conditions and loops: (while, if, elif, else)  
-	Variable names must not contain the name of any reserved name, including reserved keywords and function names. For instance, *'maxNum'* is not a valid variable name for it contains the function name *'max'*.  
-	The following are the supported functions:  
    o&nbsp;&nbsp;`len(arg1)`: arg1 is a list or a string. Returns the number of elements of arg1.  
    o&nbsp;&nbsp;`reverse(arg1)`: arg1 is a list. Returns a copy of arg1 in reversed order.  
    o&nbsp;&nbsp;`append(arg1, arg2)`: arg1 is a list, arg2 is an element of the same type as arg1 elements. Returns a new list that consists of arg1 elements and the arg2 appended to the end.  
    o&nbsp;&nbsp;`max(arg1, arg2)`: arg1 is a number, arg2 is a number. Returns the maximum between them.  
    o&nbsp;&nbsp;`max(arg1)`: arg1 is a list of numbers. Returns the maximal number in arg1.  
    o&nbsp;&nbsp;`min(arg1, arg2)`: arg1 is a number, arg2 is a number. Returns the minimum between them.  
    o&nbsp;&nbsp;`min(arg1)`: arg1 is a list of numbers. Returns the minimal number in arg1.  
    o&nbsp;&nbsp;`sum(arg1)`: arg1 is a list of numbers. Returns the sum of arg1 elements.  
    o&nbsp;&nbsp;`sum(arg_1, arg_2, …, arg_k)`: arg_i for each i in [1,k] is a number. Returns the sum of all the arguments.  
    o&nbsp;&nbsp;`index(arg1, arg2)`: arg1 is a list or a string, arg2 is an element. Returns the index of the first appearance of arg2 in arg1 if arg2 is found in arg1, otherwise returns -1.  
    o&nbsp;&nbsp;`charAt(arg1, arg2)`: arg1 is a string, arg2 is an index (a positive number). Returns *arg1[arg2]*.  
    o&nbsp;&nbsp;`substring(arg1, arg2, arg3)`: arg1 is a string, arg2 is a number, arg3 is a number. Returns *arg1[arg2 : arg3]*.  
    o&nbsp;&nbsp;`range(arg1)`: arg1 is a number (note: arg1 cannot be a variable). Returns a list *[0, 1, 2, …, arg1 - 1]*.  
    o&nbsp;&nbsp;`range(arg1, arg2)`: arg1 is a number, arg2 is a number (note: arg1 and arg2 cannot be a variable). Returns a list *[arg1, arg1 + 1, arg1 + 2, …, arg2 - 1]*.  
    o&nbsp;&nbsp;`all(arg1)`: arg1 is a list of Booleans. Returns *True* if all the elements of arg1 evaluates to True, otherwise returns *False*.  
    o&nbsp;&nbsp;`any(arg1)`: arg1 is a list of Booleans. Returns *True* if there exists an element in arg1 evaluates to True, otherwise returns *False*.  






<!--stackedit_data:
eyJoaXN0b3J5IjpbLTM5ODA5MTU5NCw1NTM5MDA0MTQsMTg2NT
M2OTMxNywtMTg0NDI5NzI2Niw4MjM1MTU1MzQsOTQ2MjE4NzA2
LDE0NTA1NDU5MTIsMTUzNTc3NzU5MiwxOTAyODI5ODI3LDE0OD
g5NzM5MDcsLTExMjc2MTM2OTgsLTExNzk2NTE3OCwtMTU0ODYw
NTg2NF19
-->