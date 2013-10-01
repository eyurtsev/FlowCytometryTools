.. _install:

.. currentmodule:: pysurvey

************
Installation
************

The latest stable version is available on `PyPI <https://pypi.python.org/pypi/PySurvey>`__.
Alternatively, you can build the `development version <https://bitbucket.org/yonatanf/pysurvey>`__. 

Quick install
~~~~~~~~~~~~~

To get the latest stable release and required dependencies, run the following as root:

:: 
    Skip for now



Python version support
~~~~~~~~~~~~~~~~~~~~~~

Python 2.6 to 2.7. 
Currently, Python 3 is not supported.


Dependencies
~~~~~~~~~~~~

  * `GoreUtilities <https://bitbucket.org/gorelab/goreutilities/>`__: required for plotting and misc.
  * `pandas <http://pandas.sourceforge.net/index.html>`__: 0.8.0 or higher.
  * `matplotlib <http://matplotlib.org/>`__: required for plotting

Optional dependencies
~~~~~~~~~~~~~~~~~~~~~

  * wx-python: ://scikit-learn.org/0.10/index.html>`__: machine learning tool such as: Gaussian mixture models, etc'

.. note::

   While it is possible to install :mod:`PySurvey` with only the required dependency, many useful features
   require the recommended/optional dependencies. Hence, it is highly recommended that you install these. 
   Since installing these packages (as well as `pandas dependecies <http://pandas.pydata.org/pandas-docs/stable/install.html/>`__) 
   can become challenging, a distribution such as the `Enthought Python Distribution
   <http://enthought.com/products/epd_free.php>`__ may be worth considering.


Installing from source
~~~~~~~~~~~~~~~~~~~~~~
The source code is hosted at <https://bitbucket.org/yonatanf/pysurvey.
To retrieve the package and install it locally do (root permissions may be required): 

::

  hg clone https://bitbucket.org/yonatanf/pysurvey
  cd pysurvey
  python setup.py install


Running the test suite
~~~~~~~~~~~~~~~~~~~~~~

Though the test suite is not currently provide exhaustive coverage, most of the common 
operations are coverage. 
Running the test suite requires `nose <http://readthedocs.org/docs/nose/en/latest/>`__, and is done by running:

::

    $ nosetests pysurvey




