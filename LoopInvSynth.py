from utilities.inv import StatesFile
import ast


class LoopInvSynth(object):
    StatesFile.open()
    import TestInv
    with open("TestInv.py", "r") as source:
        content = source.read()
        print(content)
        print("Now line by line")
        for line in content.split(sep='\n'):
            print(line)
        tree = ast.parse(source.read())


