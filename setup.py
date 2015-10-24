from setuptools import setup, find_packages
import re

VERSIONFILE = "FlowCytometryTools/_version.py"
gore_utilities_version = '0.5.0'

verstrline = open(VERSIONFILE, "rt").read()
VSRE = r"^version = ['\"]([^'\"]*)['\"]"
mo = re.search(VSRE, verstrline, re.M)

if mo:
    version = mo.group(1)
else:
    raise RuntimeError("Unable to find version string in %s." % (VERSIONFILE,))

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
        "setuptools",
        "decorator",
        "GoreUtilities == {0}".format(gore_utilities_version),
    ],

    classifiers=[
        'Intended Audience :: Science/Research',
        'Programming Language :: Python :: 2',
        'Topic :: Scientific/Engineering :: Bio-Informatics',
        'Topic :: Scientific/Engineering :: Medical Science Apps.',
    ],

    long_description=open('README.rst').read(),
)
