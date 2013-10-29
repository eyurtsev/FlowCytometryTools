.. _install:

Supported Python versions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Python 2.6 to 2.7. 

Currently, Python 3 is not supported.

Installing dependencies
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Required
=========================

#. `pandas <http://pandas.sourceforge.net/index.html>`__: 0.8.0 or higher.
#. `matplotlib <http://matplotlib.org/>`__: required for plotting

**Note**
Mac and Windows users: A simple way of installing all of the dependencies is using a distribution like `canopy <https://www.enthought.com/products/canopy/>`_.
Ubuntu/Debian: Use pip or apt-get. Instructions will be available on the package websites.

Optional
=========================

#. `wx-python <http://wiki.wxpython.org/How%20to%20install%20wxPython>`__ : Used for the FlowCytometryTools GUI.

Installing the FlowCytometryTools package
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**IMPORTANT** The required dependencies are **required** for this package to work. Install them.

For programmers, the source code is hosted at bitbucket at the following URLs:
    * Required dependency: https://bitbucket.org/gorelab/goreutilities 
    * Package: https://bitbucket.org/gorelab/flowcytometrytools


Installing using pip (recommended)
====================================

#. `Install pip <http://www.pip-installer.org/en/latest/installing.html>`_ if you do not already have it.

#. Go to your command terminal and enter the following:

   .. code-block:: bash

    sudo pip install setuptools
    sudo pip install git+https://bitbucket.org/gorelab/flowcytometrytools.git

That should be it!

Installing using git
=========================

#. Install `git <http://git-scm.com/downloads>`_ on your machine.

    **STRONGLY RECOMMENDED** Give git access to the command line. 

    If you don't, the git commands below won't work. Instead you'll have to use the GUI interface with git (we don't have instructions for that).

#. Open your command terminal

#. In your command terminal enter:

    .. code-block:: bash

        ipython

#. Inside of ipython enter:

    .. ipython:: python

        import numpy, os
        print os.path.split(numpy.__path__[0])[0]

#. The printed path will be your site-packages path!

#. Quit ipython:

    .. sourcecode:: ipython

        In [3]: quit

#. In the command terminal navigate to that path:

    .. code-block:: bash

        cd (enter here the path you got above)

#. Enter the commands below:

    .. code-block:: bash

        git clone https://bitbucket.org/gorelab/goreutilities.git GoreUtilities
        git clone https://bitbucket.org/gorelab/flowcytometrytools.git FlowCytometryTools
        cd FlowCytometryTools
        git checkout v0.2.0


Updating using git
```````````````````````

If you've installed the package using git, you can also use git to update the package when new releases are available.

Do the following:

    .. code-block:: bash

        cd (enter here the path you got above)

        cd GoreUtilities
        git fetch origin
        git pull

        cd ..

        cd FlowCytometryTools
        git fetch origin
        git pull


.. does not work yet. 

    Running the test suite
    ===========================


    Running the test suite requires `nose <http://readthedocs.org/docs/nose/en/latest/>`__, and is done by:

    #. In the command terminal, go to the directory where the FlowCytometeryTools code is installed.

    #. Run the following command in the terminal:

        .. code-block:: bash

            nosetests FlowCytometeryTools

