FlowCytometryTools
-------------------

The :mod:`FlowCytometryTools` package is a `Python <http://www.python.org>`__ package designed to perform quantitaive analysis of flow cytometry data. 

It is based on the powerful `pandas <http://pandas.pydata.org/>`__ package which is tailored and optimized for interactive analysis of large data tables.

**Authors**: Jonathan Friedman and Eugene Yurtsev

Key Features
===================

- Works with individual measurements, measurement collections, or plates of any shape.
- Transformation: hyperlog, truncated log
- Gating: Threshold, Interval, Quad, Poly
- Plotting: 1d, 2d histograms for both single samples and plates.
- Supports multiple FCS formats (2.0, 3.0, 3.1)
  + The package reads the data exactly as is stored in the FCS file; i.e., the user chooses how to treat their data (transform, compensate etc.)

Resources
===================

- **Documentation:** http://gorelab.bitbucket.org/flowcytometrytools/
- **Source Repository:** https://bitbucket.org/gorelab/flowcytometrytools
- **Comments or questions:** https://bitbucket.org/gorelab/flowcytometrytools/issues


LICENSE
===================

The MIT License (MIT)

Copyright (c) 2013 Eugene Yurtsev and Jonathan Friedman

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

