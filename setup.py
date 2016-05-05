"""A setuptools based setup module.

See:
https://packaging.python.org/en/latest/distributing.html
https://github.com/pypa/sampleproject
"""

# Always prefer setuptools over distutils
from setuptools import setup, find_packages
# To use a consistent encoding
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

version = '0.2'

install_requires = [
	'ipython',
	'pandas',
]

long_description = """
Data manipulation in Python for SAS users

SASX
----

Data manipulation in Python for SAS users, with the %%sasx magic command.

SASX (Simple dAta SyntaX) has the best of both worlds:
- Classic python syntax with access to python, numpy, pandas (like Python)
- A few extra keywords to allow easy row-by-row operations (like SAS)

Install the lastest release with:
pip install sasx

More info:  https://github.com/python-sasx/sasx
"""

setup(
    name='sasx',
    version=version,
    description='Data manipulation in Python for SAS users',
    long_description=long_description,
    url='https://github.com/python-sasx/sasx',
    author='python-sasx',
    author_email='python.sasx@gmail.com',
    license='MIT',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Framework :: IPython',
        'Intended Audience :: End Users/Desktop',
        'Topic :: Database',
        'Topic :: Scientific/Engineering :: Information Analysis',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
    ],

    keywords='data manipulation sas python pandas sasx ipython',
    packages=find_packages(exclude=['contrib', 'docs', 'tests']),
    install_requires=install_requires,

)
