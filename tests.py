from time import time
from main import run
import multiprocessing
import os
from contextlib import redirect_stdout


def timer(start, end):
    hours, rem = divmod(end-start, 3600)
    minutes, seconds = divmod(rem, 60)
    return "{:0>2}:{:0>2}:{:05.2f}".format(int(hours),int(minutes),seconds)


def table_print_res(results_dict: dict, times_dict: dict):
    headers = ['Test name', 'Result', 'Time']
    row_format = "{:>25}" * (len(headers))
    with open("tests_results_table", 'w') as f:
        with redirect_stdout(f):
            print(row_format.format(*headers))
            for benchmark in results_dict.keys():
                for test in results_dict[benchmark].keys():
                    row = (results_dict[benchmark][test], times_dict[benchmark][test])
                    print(row_format.format(test.split('.')[0], *row))





def run_tests(directory='benchmarks\\',
              timeout=8):
    print("\n\n-------------------------Checking Files-------------------------")
    print("timeout=%f"%timeout)
    subdirs = [f.path for f in os.scandir(directory) if f.is_dir()]
    LOCAL_TIMEOUT = 60 * timeout
    startTime = time()
    grammar_file = "grammar"
    results_dictionary = {}
    times_dictionary = {}
    for subdir in subdirs:
        subdir_stripped = subdir.split('\\')[-1]
        # print("Starting Test Suit: %s" % subdir)
        print("Checking Suit: %s" % subdir_stripped)
        files: str = [f.name for f in os.scandir(subdir) if f.is_file()]
        if grammar_file not in files:
            print("'grammar' file was not found under {}".format(subdir_stripped))
        benchmarks: str =  [f.path for f in os.scandir(subdir) if f.is_dir()]
        for benchmark in benchmarks:
            files: str = [f.name for f in os.scandir(benchmark) if f.is_file()]
            test_files = [f for f in files if f.startswith("test") and f != "tests_results"]
            print("Test Files Found: %s\n\n" % test_files)
        # print("Test Files Found: %s\n\n" % test_files)
            for test_file in test_files:
                test_name = test_file.split(".")[0]
                cond_file = "conditions_" + test_name
                if cond_file not in files:
                    print("'{}' file was not found under {}".format(cond_file, subdir_stripped))

    print("\n\n                         Starting Tests                         ")

    for subdir in subdirs:
        subdir_wsep = subdir + "\\"
        benchmarks: str = [f.path for f in os.scandir(subdir) if f.is_dir()]
        if grammar_file not in [f.name for f in os.scandir(subdir) if f.is_file()]:
            print("'grammar' file was not found under {}".format(subdir))
        for benchmark in benchmarks:
            benchmark_wsep = benchmark + "\\"
            redirection_file = benchmark_wsep + 'tests_results'
            print("redirection file: %s"%redirection_file)
            with open(redirection_file, 'w') as f:
                with redirect_stdout(f):
                    print("Starting Test Suit: %s" % benchmark)
                    results_dictionary[benchmark] = {}
                    times_dictionary[benchmark] = {}
                    files: str = [f.name for f in os.scandir(benchmark) if f.is_file()]
                    test_files = [f for f in files if f.startswith("test") and f != "tests_results"]

                    for test_file in test_files:
                        print("-------------------------------")
                        print("Starting Test: %s" % test_file)
                        test_name = test_file.split(".")[0]
                        cond_file = "conditions_" + test_name
                        if cond_file not in files:
                            print("'{}' file was not found under {}".format(cond_file, benchmark))
                            print("*******Test Result: {}".format("Files Missing"))
                            print("-------------------------------")
                            results_dictionary[benchmark][test_file] = "Files Missing"
                            times_dictionary[benchmark][test_file] = -1.0
                            continue
                        examples_file_name = "examples_" + test_name
                        examples_file = benchmark_wsep + examples_file_name if examples_file_name in files else ''

                        manager = multiprocessing.Manager()
                        my_dict = {"result": "Before Start"}
                        res_dict = manager.dict(my_dict.copy())
                        test_start_time = time()
                        proc = multiprocessing.Process(target=run, kwargs={"program_file": benchmark_wsep + test_file,
                                                                           "grammar_file": subdir_wsep + grammar_file,
                                                                           "conds_file": benchmark_wsep + cond_file,
                                                                           "omit_print": True,
                                                                           "res_dict": res_dict,
                                                                           "timeout": LOCAL_TIMEOUT,
                                                                           "examples_file": examples_file})
                        proc.start()
                        # proc.join(LOCAL_TIMEOUT * 1.1)
                        # we should just wait for proc to terminate.. no need for timeout here
                        try:
                            proc.join(LOCAL_TIMEOUT * 1.5)
                        except Exception:
                            results_dictionary[benchmark][test_file] = "Terminated processes"
                            times_dictionary[benchmark][test_file] = timer(test_start_time, time())

                            print("Finished Test: {}\t\tTotal Time: {}".format(test_file,
                                                                               test_end_time - test_start_time))
                            print("*******Test Result: {}".format(res))
                            print("-------------------------------")
                            continue
                        # proc.join()
                        test_end_time = time()
                        res = res_dict["result"]
                        if res == "No Inv found or timed out" or (test_end_time - test_start_time) > LOCAL_TIMEOUT:
                            res = "Timed Out"
                        results_dictionary[benchmark][test_file] = res
                        times_dictionary[benchmark][test_file] = timer(test_start_time, test_end_time)
                        print("Finished Test: {}\t\tTotal Time: {}".format(test_file, test_end_time - test_start_time))
                        print("*******Test Result: {}".format(res))
                        print("-------------------------------")
            print("Benchmark {} Finished, redirected to {}.".format(benchmark, redirection_file))

    print("Finished All Suits, total time: {}".format(time() - startTime))
    table_print_res(results_dictionary, times_dictionary)

