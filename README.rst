======
 SASX
======
Data manipulation in Python for SAS users, with the %%sasx magic command.

SASX (Simple dAta SyntaX) has the best of both worlds:

- Full access to python, numpy, pandas (like Python)
- A few extra keywords to allow row-by-row operations (like SAS)

Example 1
----------

SAS:
::
	data tips;
		set tips;
		total_bill = total_bill - 2;
		new_bill = total_bill / 2;
	run;

SASX (Simple dAta SyntaX):
::
	%%sasx
	data tips:
		set tips
		total_bill = total_bill - 2
		new_bill = total_bill / 2

Python:
::
	tips['total_bill'] = tips['total_bill'] - 2
	tips['new_bill'] = tips['total_bill'] / 2.0

http://pandas.pydata.org/pandas-docs/stable/comparison_with_sas.html

Example 2
----------

SAS:
::
	data tips;
		set tips;
		if total_bill < 10 then bucket = 'low';
		else bucket = 'high';
		keep sex bucket tip;
	run;

SASX (Simple dAta SyntaX):
::
	%%sasx
	data tips:
		set tips
		if total_bill < 10:
			bucket = 'low'
		else:
			bucket = 'high'
		keep sex bucket tip

Python:
::
	tips['bucket'] = np.where(tips['total_bill'] < 10, 'low', 'high')
	tips = tips[['sex', 'bucket', 'tip']]


Installing
----------

Install the lastest release with:
::
	pip install sasx
