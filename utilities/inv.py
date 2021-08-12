import os

st_file = None


class StatesFile:

    @staticmethod
    def open():
        global st_file
        if os.path.exists("programStates.txt"):
            os.remove("programStates.txt")
        st_file = open("programStates.txt", "a+")

    @staticmethod
    def append(txt):
        st_file.write(txt)

    @staticmethod
    def close():
        st_file.close()
        if os.path.exists("programStates.txt"):
            os.remove("programStates.txt")


def __inv__(**kwargs):
    def get_type(var):
        if type(var) is str:
            return "str"
        if type(var) is int:
            return "int"
        if type(var) is list:
            return "list"

    st = ''
    for k, v in kwargs.items():
        if st is not '':
            st += '\x1F'
        st += (k + ' ' + get_type(v) + ' ' + str(v))
    StatesFile.append(st + "\n")



