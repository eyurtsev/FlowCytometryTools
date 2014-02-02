.. _install:

Installing dependencies
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The FlowCytometryTools is a python package. As such, it requires
a python interpreter to work. If you don't have python installed, then `get it here <http://www.python.org/getit/>`_. 
The package works with either python 2.6 or 2.7, but **not** with python 3.0 or higher.

This package makes use of a few scientific and data analysis libraries for python. The dependencies are listed below, followed
by instructions on how to install them on the various operation systems.

**Required Dependencies**

#. `pandas <http://pandas.sourceforge.net/index.html>`__ (Recommended version: 0.12.0 or higher).
#. `matplotlib <http://matplotlib.org/>`__: (Recommended version: 1.13.1 or higher).
#. `scipy <http://www.scipy.org/>`__: Required for hyperlog transformations.

**Optional Dependencies**

#. `wx-python <http://wiki.wxpython.org/How%20to%20install%20wxPython>`__ : Used for the FlowCytometryTools GUI.



Windows / MacOS users
=================================

A simple way of obtaining the dependencies is by installing either `canopy <https://www.enthought.com/products/canopy/>`_ or `anaconda <https://store.continuum.io/cshop/anaconda/>`_.

If you intend to use the GUI, you'll still need to install `wx-python <http://wiki.wxpython.org/How%20to%20install%20wxPython>`_.

Debian/Ubuntu users
=================================

You have at least two options:

#. Installing using the command line (this is the better option if you're comfortable with the command line). 

   Open a terminal window and enter the following:: 

        sudo apt-get build-dep python-matplotlib 
        sudo apt-get install python-pip python-dev
        sudo apt-get install python-wxgtk2.8
        sudo pip install --upgrade pip
        sudo pip install setuptools
        sudo pip install numpy scipy matplotlib ipython ipython-notebook pandas sympy 

   This should install both optional and required the dependencies.  Please shoot us an email if we forgot to include something. (Or if you have specific instructions for a different flavor of unix.)

#. Alternatively, you can install a distribution like `canopy <https://www.enthought.com/products/canopy/>`_ or `anaconda <https://store.continuum.io/cshop/anaconda/>`_.

   .. note:: 

        canopy/anaconda may not come with wx-python. In this case, in order to use the GUI, you'll still need to install wx-python.
        Also, after installing it make sure that canopy/anaconda know how to find your installation of wx-python.

Installing FlowCytometryTools
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**IMPORTANT** Make sure all required dependencies are installed before you proceed to install the package!

Using pip (recommended)
====================================

#. `Install pip <http://www.pip-installer.org/en/latest/installing.html>`_ if you do not already have it.

#. Go to your command terminal and enter the following:

   .. code-block:: bash

    sudo pip install setuptools
    sudo pip install git+https://bitbucket.org/gorelab/flowcytometrytools.git

You should be all set.

Using git
========================================

This option is recommended if you intend to contribute to developing the FlowCytometryTools library.

.. note:

    The source code is hosted at bitbucket at the following URLs:
    * Required dependency: https://bitbucket.org/gorelab/goreutilities 
    * Package: https://bitbucket.org/gorelab/flowcytometrytools

#. Install `git <http://git-scm.com/downloads>`_ on your machine. Please give git access to the command line. If you don't, the git commands below won't work.

#. Open your command terminal

#. In your command terminal enter::
    
    ipython -c 'import os, matplotlib; print os.path.split(matplotlib.__path__[0])[0];'

#. The printed path will be your site-packages path!

#. In the command terminal navigate to that path::

    cd (enter here the path you got above)

#. Enter the commands below::

    git clone https://bitbucket.org/gorelab/goreutilities.git GoreUtilities
    git clone https://bitbucket.org/gorelab/flowcytometrytools.git FlowCytometryTools
    cd FlowCytometryTools
    git checkout [version number]


**Updating using git**

If you've installed the package using git, you can also use git to update the package when new releases are available. To update::

    cd (enter here the path you got above)

    cd GoreUtilities
    git fetch origin
    git pull
    git checkout [needed version/branch]

    cd ..

    cd FlowCytometryTools
    git fetch origin
    git pull
    git checkout [needed version/branch]
