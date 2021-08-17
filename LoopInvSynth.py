from utilities.inv import StatesFile


class LoopInvSynth(object):
    def __call__(self, states_file, input_code):
        StatesFile.open(states_file)
        exec(input_code)
        StatesFile.close(states_file)
        # StatesFile.close(states_file)




    # with open("TestInv.py", "r") as source:
    #     content = source.read()
    #     print(content)
    #     print("Now line by line")
    #     for line in content.split(sep='\n'):
    #         print(line)
    #     tree = ast.parse(source.read())
