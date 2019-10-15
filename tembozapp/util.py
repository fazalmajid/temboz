from __future__ import print_function
import sys, traceback
import tembozapp.param as param

# Utility functions for debugging
# we have to be extra defensive in order not to erase the original exception
# with one generated in this function
# the argument 'black_list' is a list of variable names that we don't want
# to see when we display the local variable dictionary.
def print_stack(black_list=[]):
  e = sys.exc_info()
  print('#' * 10, 'BEGIN', '#' * 60, file=param.log)
  print(str(e[0]) +':', e[1], file=param.log)
  if e[1] != None:
    traceback.print_exc(None, param.log)
    t = e[2]
    # this should not be necessary as the tracback should have at least two
    # elements, one for print_stack and one for the caller function
    if t != None and t.tb_next != None:
      while t.tb_next.tb_next != None:
        t = t.tb_next
    if t != None:
      print('-' * 10, 'local variables:', '-' * 50, file=param.log)
      for var_name, var_value in list(t.tb_frame.f_locals.items()):
        if var_name not in black_list:
          print(var_name, ':', repr(var_value), file=param.log)
    del t
  # to help the garbage collector
  del e
  print('#' * 10, 'END', '#' * 63, file=param.log)
