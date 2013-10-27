from FlowCytometryTools._version import version
from distutils.core import setup

setup(
    name = 'FlowCytometryTools',
    packages = ['FlowCytometryTools', 'FlowCytometryTools.tests', ],
    version = version,
    description = 'A python package for performing flow cytometry analysis',
    author = 'Jonathan Friedman, Eugene Yurtsev',
    author_email = 'eyurtsev@mit.edu',
    url = 'https://bitbucket.org/gorelab/goreutilities/',
    download_url = 'https://bitbucket.org/gorelab/flowcytometrytools/get/v{0}.zip'.format(version),
    keywords = ['flow cytometry', 'data analysis', 'cytometry', 'single cell'],
    license='MIT',
    install_requires=[
          "pandas >= 0.8.0",
      ],

    classifiers = [
        'Intended Audience :: Science/Research',
        'Programming Language :: Python :: 2',
        'Topic :: Scientific/Engineering :: Bio-Informatics',
        'Topic :: Scientific/Engineering :: Medical Science Apps.',
    ]

)
