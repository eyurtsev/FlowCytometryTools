import fnmatch
import re
from setuptools import setup, find_packages
import os

def get_package_version(path):
    '''Extracts the version'''
    with open(VERSION_FILE, "rt") as f:
        verstrline = f.read()

    VERSION = r"^version = ['\"]([^'\"]*)['\"]"
    results = re.search(VERSION, verstrline, re.M)

    if results:
        version = results.group(1)
    else:
        raise RuntimeError("Unable to find version string in {}.".format(path))

    return version

def get_fcs_files():
    matches = []
    for root, dirnames, filenames in os.walk('FlowCytometryTools'):
      for filename in fnmatch.filter(filenames, '*.fcs'):
        matches.append(os.path.join(root, filename))
    return matches

VERSION_FILE = "FlowCytometryTools/_version.py"
gore_utilities_version = '0.5.0'
version = get_package_version(VERSION_FILE)

with open('README.rst', 'r') as f:
    README_content = f.read()

setup(
    name='FlowCytometryTools',
    packages=find_packages(),
    version=version,
    description='A python package for performing flow cytometry analysis',
    author='Jonathan Friedman, Eugene Yurtsev',
    author_email='eyurtsev@gmail.com',
    url='https://gorelab.bitbucket.org/flowcytometrytools',
    download_url='https://github.com/eyurtsev/FlowCytometryTools/archive/v{0}.zip'.format(version),
    keywords=['flow cytometry', 'data analysis', 'cytometry', 'single cell'],
    license='MIT',

    install_requires=[
        "pandas",
        "matplotlib",
        "scipy",
        "numpy",
        "setuptools",
        "fcsparser>=0.1.1",
        "decorator",
        "GoreUtilities == {0}".format(gore_utilities_version),
    ],

    classifiers=[
        'Intended Audience :: Science/Research',
        'Programming Language :: Python :: 2',
        'Topic :: Scientific/Engineering :: Bio-Informatics',
        'Topic :: Scientific/Engineering :: Medical Science Apps.',
    ],

    long_description=README_content,
    include_package_data = True,

    package_data={
        'FlowCytometryTools': get_fcs_files(),
    },
)
