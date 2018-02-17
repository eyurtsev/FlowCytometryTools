import fnmatch
import re
import os

from setuptools import setup, find_packages

# Taken from seaborn's setup file
# temporarily redirect config directory to prevent matplotlib importing
# testing that for writeable directory which results in sandbox error in
# certain easy_install versions
os.environ["MPLCONFIGDIR"] = "."

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

##
# Function was taken from seaborn's setup function.
# This should help when running pip install FlowCytometryTools --upgrade
# To avoid forcing an upgrade of pandas/matplotlib/scipy/numpy
def check_dependencies():
    install_requires = []

    try:
        import numpy
    except ImportError:
        install_requires.append('numpy')
    try:
        import scipy
    except ImportError:
        install_requires.append('scipy')
    try:
        import matplotlib
    except ImportError:
        install_requires.append('matplotlib>=1.5.3')
    try:
        import pandas
    except ImportError:
        install_requires.append('pandas>=0.19.0')

    return install_requires

VERSION_FILE = "FlowCytometryTools/_version.py"
version = get_package_version(VERSION_FILE)

with open('README.rst', 'r') as f:
    README_content = f.read()

install_requires = check_dependencies()
install_requires.extend(["setuptools",
                         "decorator",
                         "fcsparser>=0.1.1"])

setup(
    name='FlowCytometryTools',
    packages=find_packages(),
    version=version,
    description='A python package for performing flow cytometry analysis',
    author='Jonathan Friedman, Eugene Yurtsev',
    author_email='eyurtsev@gmail.com',
    url='http://eyurtsev.github.io/FlowCytometryTools/',
    download_url='https://github.com/eyurtsev/FlowCytometryTools/archive/v{0}.zip'.format(version),
    keywords=['flow cytometry', 'data analysis', 'cytometry', 'single cell'],
    license='MIT',
    setup_requires=["numpy"],  # Needed to install numpy
    install_requires=install_requires,
    classifiers=[
        'Intended Audience :: Science/Research',
        'Programming Language :: Python :: 2.7',
        'Topic :: Scientific/Engineering :: Bio-Informatics',
        'Topic :: Scientific/Engineering :: Medical Science Apps.',
    ],

    long_description=README_content,
    include_package_data = True,

    package_data={
        'FlowCytometryTools': get_fcs_files(),
    },
)
