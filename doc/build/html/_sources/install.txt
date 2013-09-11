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

  pip install pysurvey


Python version support
~~~~~~~~~~~~~~~~~~~~~~

Python 2.6 to 2.7. 
Currently, Python 3 is not supported.


Dependencies
~~~~~~~~~~~~

  * `pandas <http://pandas.sourceforge.net/index.html>`__: 0.8.0 or higher.


Recommended Dependencies
~~~~~~~~~~~~~~~~~~~~~~~~
  * `matplotlib <http://matplotlib.sourceforge.net/>`__: required for plotting
  * `SciPy <http://www.scipy.org>`__: miscellaneous statistical functions. Required for distances and hierarchical clustering


Optional dependencies
~~~~~~~~~~~~~~~~~~~~~

  * `scikits-learn <http://scikit-learn.org/0.10/index.html>`__: machine learning tool such as: Gaussian mixture models, etc'
  * `pycognet <http://pycogent.sourceforge.net/>`__:  required for PCoA
  * `rpy2 <http://rpy.sourceforge.net/rpy2/doc-2.1/html/index.html/>`__: required for using R functions 

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




