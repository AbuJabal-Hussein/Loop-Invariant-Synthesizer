
# from LoopInvSynth import LoopInvSynth
from VC_Generation import VCGenerator, read_source_file





# def bottom_up(T, V, R, S, input, output):
#     """
#     :param T: terminals set
#     :param V: variables set
#     :param R: rules set (set of lists, eg: {[E1, E1, T], [T, a, 3]} ==> {E1 -> E1 T , T -> a 3})
#     :param S: starting variable
#     :param input:
#     :param output:
#     :return:
#     """
#
#     return None


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    # import z3Test
    # LoopInvSynth()
    # print('PyCharm')
    input_code = read_source_file("benchmarks/test_append.py")
    VCGenerator()(input_code)

