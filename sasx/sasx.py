from __future__ import division
import ast
import re
import pandas
from IPython.core.magic import (Magics, magics_class, cell_magic)

@magics_class
class SasxMagics(Magics):
    """Define Magic to run code in Simple dAta SyntaX (SASX).

      %%sasx  - Execute the code using Simple dAta SyntaX
      
      Special keywords recognised by SASX :
          - data
          - set
          - drop
          - keep
          - where ?
          - _n_ ?
          - merge ?
          - by ?
          - groupby
          - output ?
      
    """
    
          

    def __init__(self, shell):
        super(SasxMagics, self).__init__(shell)

    @cell_magic
    def sasx(self, line_param, cell):
        
        #Check if list of names are valid python names
        def invalid_names(names):
            for name in names:
                 try:
                    root=ast.parse(name)
                 except SyntaxError:
                    return name
                 if not isinstance(root.body[0], ast.Expr):
                    return name
                 if not isinstance(root.body[0].value, ast.Name):
                    return name
             
            #names are all valid names!
            return None
            
        #Initialize variables
        df_in = None
        df_out = None
        drop = []
        keep = []
        python_lines = []
        str_code = ""
        
        #Read all lines in cell
        lines = cell.split('\n')
        i = 0
        
        for line in lines:
            
            i = i + 1
            sline = line.strip()            
            
            #Keyword DATA
            if i == 1:
                if sline.upper().startswith('DATA ') and sline.endswith(':'):
                    words = [x for x in re.split(" +",sline[:-1]) if x]
                    if len(words) == 2 :
                        if invalid_names([words[1]]) is not None:
                            print("SASX syntax error on line 1 : '" + invalid_names([words[1]]) + "' is not a valid name") 
                            return
                        # words[1] is a valid name!
                        df_out=words[1]
                    elif len(words) ==  1:
                        print("SASX syntax error on line 1 : output name missing")
                        return    
                    else:
                        print("SASX syntax error on line 1 : only one output name expected")
                        return    
                elif sline.upper().startswith('DATA '):
                    print("SASX syntax error on line 1 : line should end with ':'")
                    return
                else:
                    print("SASX syntax error on line 1 : keyword DATA expected")
                    return
                
            elif sline.upper().startswith('DATA '):
                print("SASX syntax error on line " + str(i) + " : keyword DATA only allowed on first line") 
                return
            
            #Keyword SET
            elif sline.upper().startswith('SET '):
                words = [x for x in re.split(" +",sline) if x]
                if len(words) == 2 :
                    if invalid_names([words[1]]) is not None:
                        print("SASX syntax error on line " + str(i) + " : '" + invalid_names([words[1]]) + "' is not a valid name") 
                        return
                    # words[1] is a valid name!
                    if not isinstance(self.shell.user_ns.get(words[1]), pandas.core.frame.DataFrame):
                        print("SASX syntax error on line " + str(i) + " : '" + words[1] + "' is not a valid DataFrame")
                        return
                    df_in=words[1]
                elif len(words) ==  1:
                    print("SASX syntax error on line " + str(i) + " : input name missing")
                    return    
                else:
                    print("SASX syntax error on line " + str(i) + " : only one input name expected")
                    return
                
            #Keyword DROP
            elif sline.upper().startswith('DROP '):
                
                #if keyword KEEP before
                if len(keep) > 0:
                    print("SASX syntax error on line " + str(i) + " : keywords DROP and KEEP in the same data step")
                    return 
                
                words = [x for x in re.split(" +",sline) if x]
                if len(words) ==  1:
                    print("SASX syntax error on line " + str(i) + " : variable name missing")
                    return
                if invalid_names(words[1:]) is not None:
                    print("SASX syntax error on line " + str(i) + " : '" + invalid_names([words[1]]) + "' is not a valid name") 
                    return
                
                # words are all valid names!
                drop = words[1:]
                

            #Keyword KEEP
            elif sline.upper().startswith('KEEP '):
                
                #if keyword DROP before
                if len(drop) > 0:
                    print("SASX syntax error on line " + str(i) + " : keywords DROP and KEEP in the same data step")
                    return 
                
                words = [x for x in re.split(" +",sline) if x]
                if len(words) ==  1:
                    print("SASX syntax error on line " + str(i) + " : variable name missing")
                    return
                if invalid_names(words[1:]) is not None:
                    print("SASX syntax error on line " + str(i) + " : '" + invalid_names([words[1]]) + "' is not a valid name") 
                    return
                
                # words are all valid names!
                keep = words[1:]
                

            #If no keyword
            else:
                if (len(line.strip()) > 0) :
                    python_lines.append(line)        

        #Get names of exsting columns
        if df_in:
            df_name=df_in
            print("Reading rows from '" + df_name + "'...")
        else:
            df_name=df_out
            print("SET keyword missing => Reading rows from '" + df_name + "'...")
            if not isinstance(self.shell.user_ns.get(df_name), pandas.core.frame.DataFrame):
                print("SASX syntax error : '" + df_name + "' is not a valid DataFrame")
                return
        names_df=self.shell.user_ns.get(df_name).columns.values

        #At least 2 lines for correct syntax
        if len(lines)==1:
            print "Error: no line in the data step"
            return
    
        #Parse python lines
        root = ast.parse("def fake():\n" + "\n".join(python_lines))
        
        #Get variable names that are modified
        names_store_code = sorted({node.id for node in ast.walk(root) if isinstance(node, ast.Name) if isinstance(node.ctx, ast.Store)})
        
        #Get all variable names
        names_all_code = sorted({node.id for node in ast.walk(root) if isinstance(node, ast.Name) })
    
        #Generate python code
        
        #Get base indent
        min_indent = min([len(line) - len(line.lstrip()) for line in python_lines])
        indent = min_indent * " "

        #Most of the code is generated in a function (called sasx_code) so created variables are local variables
        str_code = "def sasx_code():\n"
        
        #Create series for variables modified in python code (and kept)
        for var in [var for var in names_store_code]:
            if (len(keep)==0 & (var not in drop)) or (len(drop)==0 & (var in keep)) :
                str_code = str_code + "    series_" + var + "  = pd.Series(index=" + df_name + ".index,name='" + var + "')\n"
        
        str_code = str_code + "    for c in " + df_name + ".itertuples():\n"
        #Variables already existing in the DataFrame
        for var in [var for var in names_all_code if var in names_df]:
            str_code = str_code + "    " + indent + var + " = c." + var + "\n"
        #Pure python code
        str_code = str_code + "    " + ('\n'+ "    ").join(python_lines) + "\n"
        
        #variables modified in python code (and kept)
        for var in [var for var in names_store_code]:
            if (len(keep)==0 & (var not in drop)) or (len(drop)==0 & (var in keep)) :
                str_code = str_code + "    " + indent + "series_" + var + "[c.Index] = " + var + "\n"  
        #Update target DataFrame
        if df_out <> df_name:
            str_code = str_code + "    " + df_out + " = " + df_name + ".copy()\n"
        for var in [var for var in names_store_code]:
            if (len(keep)==0 & (var not in drop)) or (len(drop)==0 & (var in keep)) :
                str_code = str_code + "    " + df_out + "['" + var + "'] = series_" + var + "\n"  
        
        #Add output DataFrame to globals()
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
