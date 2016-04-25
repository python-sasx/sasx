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

version = '0.1.1'

install_requires = [
	'ipython',
	'pandas',
]

# Get the long description from the README file
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

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
        'Development Status :: 3 - Alpha',
        'Intended Audience :: End Users/Desktop',
        'Topic :: Database',
        'Topic :: Database :: Front-Ends',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
    ],

    keywords='data manipulation sas python pandas sasx',
    packages=find_packages(exclude=['contrib', 'docs', 'tests']),
    install_requires=install_requires,

)
