def sasx_preloop(result):

	df_in = result['df_in']
	output_variables = result['output_variables']

	#Create series for variables modified in python code (and kept)
	str_code=""
	for var in [var for var in output_variables]:
		str_code = str_code + "series_" + var + "  = pd.Series(index=" + df_in + ".index,name='" + var + "')\n"
	return str_code


def sasx_loop(result):

	df_in = result['df_in']
	input_variables = result['input_variables']
	output_variables = result['output_variables']
	python_lines = result['python_blocks'][0]

	#Get base indent
	min_indent = min([len(line) - len(line.lstrip()) for line in python_lines])
	indent = min_indent * " "

	str_code = "for c in " + df_in + ".itertuples():\n"
	#Variables already existing in the DataFrame
	for var in [var for var in input_variables]:
		str_code = str_code +  indent + var + " = c." + var + "\n"

	#Pure python code
	str_code = str_code + '\n'.join(python_lines) + "\n"
	
	#variables modified in python code (and kept)
	for var in [var for var in output_variables]:
		str_code = str_code + indent + "series_" + var + "[c.Index] = " + var + "\n"  
        
	return str_code
 
def sasx_postloop(result):

	df_in = result['df_in']
	df_out = result['df_out']
	output_variables = result['output_variables']
	drop = result['drop']
	keep = result['keep']

	str_code = ""

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