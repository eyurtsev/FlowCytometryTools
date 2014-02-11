from setuptools import setup, find_packages
# from distutils.core import setup
## get version info
import re
VERSIONFILE="FlowCytometryTools/_version.py"
gore_utilities_version = '0.3.4'
verstrline = open(VERSIONFILE, "rt").read()
VSRE = r"^version = ['\"]([^'\"]*)['\"]"
mo = re.search(VSRE, verstrline, re.M)
if mo:
    version = mo.group(1)
else:
    raise RuntimeError("Unable to find version string in %s." % (VERSIONFILE,))

setup(
    name = 'FlowCytometryTools',
    packages=find_packages(),
    version = version,
    description = 'A python package for performing flow cytometry analysis',
    author = 'Jonathan Friedman, Eugene Yurtsev',
    author_email = 'eyurtsev@mit.edu',
    url = 'https://bitbucket.org/gorelab/goreutilities/',
    download_url = 'https://bitbucket.org/gorelab/flowcytometrytools/get/v{0}.zip'.format(version),
    keywords = ['flow cytometry', 'data analysis', 'cytometry', 'single cell'],
    license='MIT',
    dependency_links = ['https://bitbucket.org/gorelab/goreutilities/get/v{0}.zip#egg=GoreUtilities-{0}'.format(gore_utilities_version)],
    #dependency_links = ['https://bitbucket.org/gorelab/goreutilities/get/master.zip#egg=GoreUtilities-0.3.0'.format(version)],

    install_requires=[
          "setuptools",
          "GoreUtilities == {0}".format(gore_utilities_version),
      ],
    classifiers = [
        'Intended Audience :: Science/Research',
        'Programming Language :: Python :: 2',
        'Topic :: Scientific/Engineering :: Bio-Informatics',
        'Topic :: Scientific/Engineering :: Medical Science Apps.',
    ],

    #include_package_data = False,
    long_description=open('README.rst').read(),
    #package_data = {
        #'': ['*.fcs'],
    #},
)
