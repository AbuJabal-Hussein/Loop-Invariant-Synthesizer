import os

st_file = None


class StatesFile:

    @staticmethod
    def open(file):
        print("------------Trying to open------------")
        global st_file
        if os.path.exists(file):
            os.remove(file)
        st_file = open(file, "a+")
        print("------------Opened------------")

    @staticmethod
    def append(txt):
        global st_file
        if st_file is not None:
            st_file.write(txt)
            print("------------appended------------")

    @staticmethod
    def close():
        global st_file
        if st_file is not None:
            st_file.close()
        # if os.path.exists(file):
        #     os.remove(file)

    @staticmethod
    def remove(file):
        if os.path.exists(file):
            os.remove(file)


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


def append(lst, x):
    mylist = lst[:]
    mylist.append(x)
    return mylist
