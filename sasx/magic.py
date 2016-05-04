from __future__ import division
import ast
import re
import pandas
from IPython.core.magic import (Magics, magics_class, cell_magic)

from sasx.parse import sasx_parse

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

        print(cell_parsed)

        #Initialize variables
        df_in = cell_parsed['df_in']
        df_out = cell_parsed['df_out']
        drop = cell_parsed['drop']
        keep = cell_parsed['keep']
        input_variables = cell_parsed['input_variables']
        output_variables = cell_parsed['output_variables']
        python_lines = cell_parsed['python_blocks'][0]
        str_code = ""


        #Generate python code
        
        #Get base indent
        min_indent = min([len(line) - len(line.lstrip()) for line in python_lines])
        indent = min_indent * " "

        #Most of the code is generated in a function (called sasx_code) so created variables are local variables
        str_code = "def sasx_code():\n"
        
        #Create series for variables modified in python code (and kept)
        for var in [var for var in output_variables]:
            str_code = str_code + "    series_" + var + "  = pd.Series(index=" + df_in + ".index,name='" + var + "')\n"
        
        str_code = str_code + "    for c in " + df_in + ".itertuples():\n"
        #Variables already existing in the DataFrame
        for var in [var for var in input_variables]:
            str_code = str_code + "    " + indent + var + " = c." + var + "\n"
        #Pure python code
        str_code = str_code + "    " + ('\n'+ "    ").join(python_lines) + "\n"
        
        #variables modified in python code (and kept)
        for var in [var for var in output_variables]:
            str_code = str_code + "    " + indent + "series_" + var + "[c.Index] = " + var + "\n"  
        #Update target DataFrame
        if df_out <> df_in:
            str_code = str_code + "    " + df_out + " = " + df_in + ".copy()\n"
        for var in [var for var in output_variables]:
            str_code = str_code + "    " + df_out + "['" + var + "'] = series_" + var + "\n"  
        
        #Drop & keep
        if (len(drop))>0:
            str_code = str_code + "    " + df_out + ".drop(['" + "','".join(drop) + "'], axis=1, inplace=True)\n"
        elif (len(keep))>0:
            str_code = str_code + "    " + df_out + "=" + df_out + "[['" + "','".join(keep) + "']]\n"
        
        #Add df_out DataFrame to globals()
        str_code = str_code + "    globals()['" +  df_out + "'] = " + df_out + "\n"
        
        #Execute the code
        str_code = str_code + "sasx_code()" 
        ns = {}
        print("-----")
        print(str_code)
        print("-----")
        exec str_code in self.shell.user_ns, ns

# Register
ip = get_ipython() 
ip.register_magics(SasxMagics)
