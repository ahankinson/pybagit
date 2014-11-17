import os
import timeit

pyb_statement = """
    import os
    os.system("~/Documents/code/git/pybagit/pybagit/multichecksum.py ~/Documents/code/git/edsu-bagit/newbag/data")
"""

t = timeit.Timer(pyb_statement)
print "pybagit took %.2f seconds" % (10 * t.timeit(number=10) / 10)
