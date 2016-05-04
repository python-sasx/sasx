import ast
import re
import pandas

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

def sasx_parse(str_code, self):
    
    result = {}
    result['status'] = 0 # 1: OK; 0:Error
    result['message'] = "" # Error message
    result['df_out'] = None
    result['df_in'] = None
    result['drop'] = []
    result['keep'] = []
    result['first_line_indent'] = None
    result['python_blocks'] = []
    result['indents'] = []
    result['input_variables'] = [] #variables from input DataFrame used in the code
    result['output_variables'] = [] #variables modified in code (kept or not dropped)

    python_block = []

    #Read all lines in cell
    lines = str_code.split('\n')
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
                        result['message'] = "SASX syntax error on line 1 : '" + invalid_names([words[1]]) + "' is not a valid name" 
                        return result
                    # words[1] is a valid name!
                    result['df_out'] = words[1]
                elif len(words) ==  1:
                    result['message'] = "SASX syntax error on line 1 : output name missing"
                    return result
                else:
                    result['message'] = "SASX syntax error on line 1 : only one output name expected"
                    return result   
            elif sline.upper().startswith('DATA '):
                result['message'] = "SASX syntax error on line 1 : line should end with ':'"
                return result
            else:
                result['message'] = "SASX syntax error on line 1 : keyword DATA expected"
                return result
            
        elif sline.upper().startswith('DATA '):
            result['message'] = "SASX syntax error on line " + str(i) + " : keyword DATA only allowed on first line"
            return result
        
        #Keyword SET
        elif sline.upper().startswith('SET '):
            words = [x for x in re.split(" +",sline) if x]
            if len(words) == 2 :
                if invalid_names([words[1]]) is not None:
                    result['message'] = "SASX syntax error on line " + str(i) + " : '" + invalid_names([words[1]]) + "' is not a valid name"
                    return result
                # words[1] is a valid name!
                if not isinstance(self.shell.user_ns.get(words[1]), pandas.core.frame.DataFrame):
                    result['message'] = "SASX syntax error on line " + str(i) + " : '" + words[1] + "' is not a valid DataFrame"
                    return result
                result['df_in'] = words[1]
            elif len(words) ==  1:
                result['message'] = "SASX syntax error on line " + str(i) + " : input name missing"
                return result    
            else:
                result['message'] = "SASX syntax error on line " + str(i) + " : only one input name expected"
                return result
            
        #Keyword DROP
        elif sline.upper().startswith('DROP '):
            
            #if keyword KEEP before
            if len(result['keep']) > 0:
                result['message'] = "SASX syntax error on line " + str(i) + " : keywords DROP and KEEP in the same data step"
                return result
            
            words = [x for x in re.split(" +",sline) if x]
            if len(words) ==  1:
                result['message'] = "SASX syntax error on line " + str(i) + " : variable name missing"
                return result
            if invalid_names(words[1:]) is not None:
                result['message'] = "SASX syntax error on line " + str(i) + " : '" + invalid_names([words[1]]) + "' is not a valid name"
                return result
            
            # words are all valid names!
            result['drop'] = words[1:]
            

        #Keyword KEEP
        elif sline.upper().startswith('KEEP '):
            
            #if keyword DROP before
            if len(result['drop']) > 0:
                result['message'] = "SASX syntax error on line " + str(i) + " : keywords DROP and KEEP in the same data step"
                return result 
            
            words = [x for x in re.split(" +",sline) if x]
            if len(words) ==  1:
                result['message'] = "SASX syntax error on line " + str(i) + " : variable name missing"
                return result
            if invalid_names(words[1:]) is not None:
                result['message'] = "SASX syntax error on line " + str(i) + " : '" + invalid_names([words[1]]) + "' is not a valid name"
                return result
            
            # words are all valid names!
            result['keep'] = words[1:]
            
        #Keyword OUTPUT
        elif sline.upper()=='OUTPUT':
            indent = len(line) - len(line.lstrip())
            #New block
            if len(python_block)>0:
                result['python_blocks'].append(python_block)
                result['indents'].append(indent)
            python_block = []


        #Python line (no SASX keyword)
        else:
            if (len(sline) > 0) :

                #Get indent if first python line
                if (len(python_block)==0) & (len(result['python_blocks'])==0):
                    indent = len(line) - len(line.lstrip())
                    result['first_line_indent'] = indent

                #Append line to current python block
                python_block.append(line)


    #Append last block to python_blocks only if no OUTPUT keyword before
    if (len(python_block)>0):
        if (len(result['python_blocks'])==0):
            result['python_blocks'].append(python_block)
        else:
            result['message'] = "SASX syntax error on line " + str(i) + " : keyword OUTPUT missing"
            return result
             
    #Parsing finished - doing some extra checks

    #At least 1 python line for correct syntax
    if len(result['python_blocks'])==0:
        result['message'] = "Error: no python line in the data step"
        return result

    #If df_in missing: df_out is used as the input DataFrame
    if (result['df_in']) == None:
        #Before assigning check that df_out is a DataFrame
        if not isinstance(self.shell.user_ns.get(result['df_out']), pandas.core.frame.DataFrame):
            result['message'] = "SASX syntax error on line 1 : '" + result['df_out'] + "' is not a valid DataFrame"
            return result
        result['df_in'] = result['df_out']

    #Parsing finished - get variables from input DataFrame and from the code

    #Get all variables from input Dataframe
    df_in_variables = self.shell.user_ns.get(result['df_in']).columns.values

    #Parse python lines
    python_lines = [item for sublist in result['python_blocks'] for item in sublist]
    root = ast.parse("def fake():\n" + "\n".join(python_lines))
    code_modified_variables = sorted({node.id for node in ast.walk(root) if isinstance(node, ast.Name) if isinstance(node.ctx, ast.Store)})
    code_variables = sorted({node.id for node in ast.walk(root) if isinstance(node, ast.Name) })

    #variables from input DataFrame used in the code
    result['input_variables'] = [var for var in code_variables if var in df_in_variables]

    #variables modified in code (not dropped or kept)
    if (len(result['keep'])==0):
        result['output_variables'] = [var for var in code_modified_variables if var not in result['drop'] ]
    elif (len(result['drop'])==0):
        result['output_variables'] = [var for var in code_modified_variables if var in result['keep'] ]

    #Parsing finished without errors
    result['status'] = 1
    return result

