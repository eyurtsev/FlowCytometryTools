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
As a result, users can significantly reduce the amount of effort required to perform data analysis.

Basic familiarity with the python programming languages is recommended.

Features
===================

- **Transformations**: hyperlog (hlog), truncated log (tlog)
- **Plotting**: 1D, 2D histograms for both single samples and collections (e.g., 96-well plates).
- **Gating**: threshold, interval, quad, polygon gates
- **GUI**: simple graphical user interface to draw gates
- **FCS Formats**: Supports FCS 2.0, 3.0, and 3.1

Resources
===================

- **Documentation:** http://gorelab.bitbucket.org/flowcytometrytools/
- **Source Repository:** https://bitbucket.org/gorelab/flowcytometrytools
- **Comments or questions:** https://bitbucket.org/gorelab/flowcytometrytools/issues

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
