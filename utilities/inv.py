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
    st = ''
    for k, v in kwargs:
        st += (k + ' ' + v + ',')
    StatesFile.append(st)



