from __future__ import division
import pandas
from IPython.core.magic import (Magics, magics_class, cell_magic)

from sasx.parse import sasx_parse
from sasx.code import sasx_preloop
from sasx.code import sasx_loop
from sasx.code import sasx_postloop


@magics_class
class SasxMagics(Magics):
    """Define Magic to run code in Simple dAta SyntaX (SASX).

      %%sasx  - Transform SASX code into Python code and execute it.
      
      Special keywords recognised by SASX :
          - data
          - set
          - drop
          - keep
          - output
          - where ?
          - _n_ ?
          - groupby ?
      
    """

    def __init__(self, shell):
        super(SasxMagics, self).__init__(shell)

    @cell_magic
    def sasx(self, line_param, cell):

        cell_parsed = sasx_parse(cell, self)

        if cell_parsed['status']==0:
            print(cell_parsed['message'])
            return

        #Generate python code
        str_code = ""
        str_code = str_code + sasx_preloop(cell_parsed)
        str_code = str_code + sasx_loop(cell_parsed)
        str_code = str_code + sasx_postloop(cell_parsed)
        
        #Execute the code
        ns = {}
        print("-----")
        print(str_code)
        print("-----")
        exec str_code in self.shell.user_ns, ns

# Register
ip = get_ipython() 
ip.register_magics(SasxMagics)
