from time import time
from main import run
import multiprocessing
import os


def run_tests(directory='benchmarks\\',
              timeout=8):
    print("\n\n-------------------------Checking Files-------------------------")
    print("timeout=%f"%timeout)
    subdirs = [f.path for f in os.scandir(directory) if f.is_dir()]
    LOCAL_TIMEOUT = 60 * timeout
    startTime = time()
    grammar_file = "grammar"
    for subdir in subdirs:
        subdir_stripped = subdir.split('\\')[-1]
        # print("Starting Test Suit: %s" % subdir)
        print("Checking Suit: %s" % subdir_stripped)
        files: str = [f.name for f in os.scandir(subdir) if f.is_file()]
        test_files = [f for f in files if f.startswith("test")]
        print("Test Files Found: %s\n\n" % test_files)
        # print("Test Files Found: %s\n\n" % test_files)
        if grammar_file not in files:
            print("'grammar' file was not found under {}".format(subdir_stripped))

        for test_file in test_files:
            test_num = test_file.split("_")[0]
            cond_file = "conditions_" + test_num
            if cond_file not in files:
                print("'{}' file was not found under {}".format(cond_file, subdir_stripped))

    print("\n\n                         Starting Tests                         ")

    for subdir in subdirs:
        subdir_stripped = subdir.split('\\')[:-1]
        print("Starting Test Suit: %s" % subdir_stripped)
        files: str = [f.name for f in os.scandir(subdir) if f.is_file()]
        test_files = [f for f in files if f.startswith("test")]

        for test_file in test_files:
            print("-------------------------------")
            print("Starting Test: %s" % test_file)
            test_num = test_file.split("_")[0]
            cond_file = "conditions_" + test_num
            if (cond_file not in files) or (grammar_file not in files):
                print("Either '{}' or 'grammar' file was not found under ".format(cond_file, subdir_stripped))
            manager = multiprocessing.Manager()
            my_dict = {"result": "Before Start"}
            res_dict = manager.dict(my_dict.copy())
            subdir_wsep = subdir + "\\"
            test_start_time = time()
            proc = multiprocessing.Process(target=run, kwargs={"program_file": subdir_wsep + test_file,
                                                               "grammar_file": subdir_wsep + grammar_file,
                                                               "conds_file": subdir_wsep + cond_file,
                                                               "omit_print": True,
                                                               "res_dict": res_dict,
                                                               "timeout": LOCAL_TIMEOUT})
            proc.start()
            proc.join(LOCAL_TIMEOUT * 1.1)

            test_end_time = time()
            res = res_dict["result"]
            if res == "No Inv found or timed out" and (test_end_time - test_start_time) > LOCAL_TIMEOUT:
                res = "Timed Out"

            print("Finished Test: {}\t\tTotal Time: {}".format(test_file, test_end_time - test_start_time))
            print("*******Test Result: {}".format(res))
            print("-------------------------------")

    print("Finished All Suits, total time: {}".format(time() - startTime))
