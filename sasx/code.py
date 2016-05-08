def sasx_preloop(result):

	#Create series for variables modified in python code (and kept)

	df_in = result['df_in']
	output_variables = result['output_variables']

	str_code=""
	if len(result['python_blocks'])==1:

		for var in [var for var in output_variables]:
			str_code = str_code + "series_" + var + "  = pd.Series(index=" + df_in + ".index,name='" + var + "')\n"
	
	elif len(result['python_blocks'])>1:

		for var in [var for var in output_variables]:
			str_code = str_code + "series_" + var + "  = pd.Series(name='" + var + "')\n"

		str_code = str_code + "series_sasx_index  = pd.Series(name='sasx_index')\n"
	
	return str_code


def sasx_loop(result):

	df_in = result['df_in']
	input_variables = result['input_variables']
	output_variables = result['output_variables']
	indent = " " * result['first_line_indent']
	str_code = "i = 0\n"
	str_code = str_code + "for c in " + df_in + ".itertuples():\n"
	#Variables already existing in the DataFrame
	for var in [var for var in input_variables]:
		str_code = str_code +  indent + var + " = c." + var + "\n"

	
	#variables modified in python code (and kept)
	if len(result['python_blocks'])==1:

		python_lines = result['python_blocks'][0]
		str_code = str_code + '\n'.join(python_lines) + "\n"
		for var in [var for var in output_variables]:
			str_code = str_code + indent + "series_" + var + "[c.Index] = " + var + "\n"  
    
	elif len(result['python_blocks'])>1:

		for python_lines in result['python_blocks']:
			indent = " " * result['indents'].pop(0)
			str_code = str_code + indent + "#---start of python block---\n"
			str_code = str_code + '\n'.join(python_lines) + "\n"	
			str_code = str_code + indent + "#---end of python block---\n"
			for var in [var for var in output_variables]:
				str_code = str_code + indent + "series_" + var + ".loc[i] =" + var + "\n"  
			str_code = str_code + indent + "series_sasx_index.loc[i] = c.Index\n"  
			str_code = str_code +  indent + "i = i + 1\n"
	    
	return str_code
 
def sasx_postloop(result):

	df_in = result['df_in']
	df_out = result['df_out']
	output_variables = result['output_variables']
	drop = result['drop']
	keep = result['keep']

	str_code = ""

	#If ouput keyword
	if len(result['python_blocks'])>1:
		str_code = str_code + "df_sasx_tmp = pd.DataFrame()\n"
		for var in [var for var in output_variables]:
			str_code = str_code + "df_sasx_tmp['" + var + "'] = series_" + var + "\n"  
		str_code = str_code + "df_sasx_tmp['sasx_index'] = series_sasx_index\n"
		str_code = str_code + df_in + " = df_sasx_tmp.merge(" + df_in + ", how='left', left_on='sasx_index', right_index=True)\n"  

	#Update target DataFrame
	if df_out <> df_in:
		str_code = str_code + df_out + " = " + df_in + ".copy()\n"
	
	for var in [var for var in output_variables]:
		str_code = str_code + df_out + "['" + var + "'] = series_" + var + "\n"  

	#Drop & keep
	if (len(drop))>0:
		str_code = str_code + df_out + ".drop(['" + "','".join(drop) + "'], axis=1, inplace=True)\n"
	elif (len(keep))>0:
		str_code = str_code + df_out + "=" + df_out + "[['" + "','".join(keep) + "']]\n"

	#Add df_out DataFrame to globals()
	str_code = str_code + "globals()['" +  df_out + "'] = " + df_out + "\n"
	return str_code