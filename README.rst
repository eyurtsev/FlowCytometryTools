FlowCytometryTools
-------------------

**Authors**: Jonathan Friedman and Eugene Yurtsev

FlowCytometryTools is a python package for visualization and analysis of high-throughput flow cytometry data.

* **Intuitive**: provides a simple programmatic interface to work with flow cytometry data.
* **Interactive**: makes use of the powerful `pandas <http://pandas.pydata.org/>`_ package to simplify analysis of large datasets.
* **Flexible**: can be used for analyzing individual measurements, measurement collections or plates.

Who is this for?
=====================

FlowCytometryTools is for researchers who want to use the python programming language to analyze flow cytometry data.

The package provides an interface that can directly work with collections of flow cytometry measurements (e.g., 96-well plates).

Basic familiarity with the python programming languages is recommended.

You can find a few example scripts that load and plot flow cytometry data in the `gallery <http://gorelab.bitbucket.org/flowcytometrytools/gallery.html>`_ page.

If you like what you see, then proceed to the `installation <http://gorelab.bitbucket.org/flowcytometrytools/install.html>`_ page and then
to the `tutorial <http://gorelab.bitbucket.org/flowcytometrytools/tutorial.html>`_.

Features
===================

- **Transformations**: hyperlog (hlog), truncated log (tlog)
- **Plotting**: 1D, 2D histograms for both single samples and collections (e.g., 96-well plates).
- **Gating**: threshold, interval, quad, polygon gates
- **GUI**: simple graphical user interface to draw gates
- **FCS Formats**: Supports FCS 2.0, 3.0, and 3.1

Note: Compensation matrices are not yet read from FCS files, so currently compensation needs to be done manually.

Resources
===================

- **Documentation:** http://gorelab.bitbucket.org/flowcytometrytools/
- **Source Repository:** https://bitbucket.org/gorelab/flowcytometrytools
- **Comments or questions:** https://bitbucket.org/gorelab/flowcytometrytools/issues

Dependencies
===================

For more information about how to obtain these, please see the `installation
<http://gorelab.bitbucket.org/flowcytometrytools/install.html>`_ page.

FlowCytometryTools may work with older versions of some of these dependencies, but if
you run into issues, please update the dependencies.

**Required Dependencies**

#. `python <http://www.python.org/getit/>`_ : 2.6 or 2.7 (note that python 3.0 or higher are not yet supported!)
#. `pandas <http://pandas.sourceforge.net/index.html>`__ (Recommended version: 0.12.0 or higher).
#. `matplotlib <http://matplotlib.org/>`__: (Recommended version: 1.13.1 or higher).
#. `scipy <http://www.scipy.org/>`__ 

**Optional Dependencies**

#. `wx-python <http://wiki.wxpython.org/How%20to%20install%20wxPython>`__ : Used for the FlowCytometryTools GUI.

Changes
=====================

v0.4.0, 2014-06-05

+ Updates in documentation
+ Added experimental view() function
+ Renamed old view() function into -> view_interactively()
+ Added queueing to help when dealing with large quantities of data.
+ Histogram plots should work with pandas (0.14.0) & matplotlib (1.3.1).

v0.3.6, 2014-02-11

+ Mostly updates in documentation

v0.3.5, 2014-01-19

+ Boost in speed for transformations on collections of measurements (like 96-well plates).
+ Much of the documentation has been updated and improved.
+ Improved GUI.

v0.3.0, 2013-10-27 Initial Release

LICENSE
===================

The MIT License (MIT)

Copyright (c) 2013-2014 Eugene Yurtsev and Jonathan Friedman

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
