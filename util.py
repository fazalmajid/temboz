import sys, traceback, param

# Utility functions for debugging
# we have to be extra defensive in order not to erase the original exception
# with one generated in this function
# the argument 'black_list' is a list of variable names that we don't want
# to see when we display the local variable dictionary.
def print_stack(black_list=[]):
  e = sys.exc_info()
  print >> param.log, '#' * 10, 'BEGIN', '#' * 60
  print >> param.log, str(e[0]) +':', e[1]
  if e[1] != None:
    traceback.print_exc(None, param.log)
    t = e[2]
    # this should not be necessary as the tracback should have at least two
    # elements, one for print_stack and one for the caller function
    if t != None and t.tb_next != None:
      while t.tb_next.tb_next != None:
        t = t.tb_next
    if t != None:
      print >> param.log, '-' * 10, 'local variables:', '-' * 50
      for var_name, var_value in t.tb_frame.f_locals.items():
        if var_name not in black_list:
          print >> param.log, var_name, ':', repr(var_value)
    del t
  # to help the garbage collector
  del e
  print >> param.log, '#' * 10, 'END', '#' * 63
