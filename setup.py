import re

from setuptools import setup, find_packages


def get_package_version(path):
    """Extracts the version"""
    with open(VERSION_FILE, "rt") as f:
        verstrline = f.read()

    version_pattern = r"^version = ['\"]([^'\"]*)['\"]"
    results = re.search(version_pattern, verstrline, re.M)

    if results:
        version = results.group(1)
    else:
        raise RuntimeError("Unable to find version string in {}.".format(path))

    return version


VERSION_FILE = "FlowCytometryTools/_version.py"
version = get_package_version(VERSION_FILE)

with open("README.rst", "r") as f:
    LONG_DESCRIPTION = f.read()

setup(
    name="FlowCytometryTools",
    packages=find_packages(),
    version=version,
    description="A python package for performing flow cytometry analysis",
    author="Jonathan Friedman, Eugene Yurtsev",
    author_email="eyurtsev@gmail.com",
    url="http://eyurtsev.github.io/FlowCytometryTools/",
    download_url="https://github.com/eyurtsev/FlowCytometryTools/archive/v{0}.zip".format(
        version
    ),
    keywords=["flow cytometry", "data analysis", "cytometry", "single cell"],
    license="MIT",
    setup_requires=["numpy"],  # Needed to install numpy
    install_requires=[
        "numpy",
        "scipy",
        "pandas>=0.19.0",
        "matplotlib>=1.5.3",
        "decorator",
        "fcsparser>=0.1.1",
    ],
    classifiers=[
        "Intended Audience :: Science/Research",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Scientific/Engineering :: Bio-Informatics",
        "Topic :: Scientific/Engineering :: Medical Science Apps.",
    ],
    long_description=LONG_DESCRIPTION,
    include_package_data=True,
)
