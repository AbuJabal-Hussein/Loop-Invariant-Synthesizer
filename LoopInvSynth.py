from utilities.inv import StatesFile


class LoopInvSynth(object):
    def __call__(self, states_file, input_code):
        StatesFile.open(states_file)
        exec(input_code)
        StatesFile.close()
