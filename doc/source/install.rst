.. _install:

Required Dependencies
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The FlowCytometryTools is a python package. As such, it requires a python
interpreter to work. In addition, this package makes use of a few scientific
and data analysis libraries for python. All the dependencies are listed below,
followed by a section containing instructions on how to install all the
dependencies on the different operating systems.

**Required Dependencies**

#. `python <http://www.python.org/getit/>`_ : 2.6 or 2.7 (note that python 3.0 or higher are not yet supported!)
#. `pandas <http://pandas.sourceforge.net/index.html>`__ (Recommended version: 0.12.0 or higher).
#. `matplotlib <http://matplotlib.org/>`__: (Recommended version: 1.13.1 or higher).
#. `scipy <http://www.scipy.org/>`__ 

**Optional Dependencies**

#. `wx-python <http://wiki.wxpython.org/How%20to%20install%20wxPython>`__ : Used for the FlowCytometryTools GUI.

Installing the dependencies (Windows / MacOS / Linux)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A simple way of obtaining the dependencies is by installing either `canopy <https://www.enthought.com/products/canopy/>`_ or `anaconda <https://store.continuum.io/cshop/anaconda/>`_.

If you intend to use the Flow Cytometry Tools GUI for drawing gates you'll also need to install `wx-python <http://wiki.wxpython.org/How%20to%20install%20wxPython>`_.


Installing FlowCytometryTools
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**IMPORTANT** Make sure all required dependencies are installed before you proceed to install the package!

#. `Install pip <http://www.pip-installer.org/en/latest/installing.html>`_ if you do not already have it.

#. Go to your command terminal and enter the following:

   .. code-block:: bash

    sudo pip install flowcytometrytools

Congratulations! Proceed to the tutorial!
