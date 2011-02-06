import os
import timeit

pyb_statement = """
    import os
    os.system("/Users/ahankins/Documents/code/git/pybagit/pybagit/multichecksum.py /Users/ahankins/Documents/code/git/edsu-bagit/newbag/manifest-sha1.txt /Users/ahankins/Documents/code/git/edsu-bagit/newbag/data")
"""

t = timeit.Timer(pyb_statement)
print "pybagit took %.2f seconds" % (10 * t.timeit(number=10) / 10)

