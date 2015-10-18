"""Fabric file."""
import base64
import os
import json
import urllib2

from contextlib import contextmanager

from fabric.api import local, lcd, abort, settings
from fabric.decorators import task

from FlowCytometryTools import __version__

DL_DIR = "doc/source/_static/downloads"

BUILD_DIRS = (
    "dist",
    "doc/build",
    "build",
    "FlowCytometryTools.egg-info",
)

SDIST_RST_FILES = (
    "README.rst",
    #"HISTORY.rst",
)

SDIST_TXT_FILES = [os.path.splitext(x)[0] + ".txt" for x in SDIST_RST_FILES]


###############################################################################
# Misc.
###############################################################################
@task
def clean():
    """Clean build files."""
    for build_dir in list(BUILD_DIRS):
        local("rm -rf %s" % build_dir)

@task
def html():
    """Make html files."""
    base_path = os.path.abspath(os.path.dirname(__file__))
    with lcd(os.path.join(base_path, 'doc')):
        local("make html")
        local("touch build/html/.nojekyll")

@task
def upload_doc():
    with lcd(os.path.abspath(os.path.dirname(__file__))): 
        local('git branch -D gh-pages')
        local('git checkout -b gh-pages')
        local('git add -f doc/build/html')
        local('git commit -m "version {}"'.format(__version__))
        local('git push origin `git subtree split --prefix doc/build/html`:gh-pages --force')

@task
def serve(port="8000"):
    """
    Serve website from localhost.
    @param port  Port to run server on.
    """
    with lcd("doc/build/html"):
        local("python -m SimpleHTTPServer %s" % port)


###############################################################################
# PyPI
###############################################################################
@contextmanager
def _dist_wrapper():
    """Add temporary distribution build files (and then clean up)."""
    try:
        # Copy select *.rst files to *.txt for build.
        for rst_file, txt_file in zip(SDIST_RST_FILES, SDIST_TXT_FILES):
            local("cp %s %s" % (rst_file, txt_file))

        # Perform action.
        yield
    finally:
        # Clean up temp *.txt files.
        for rst_file in SDIST_TXT_FILES:
            local("rm -f %s" % rst_file, capture=False)


@task
def sdist():
    """Package into distribution."""
    with _dist_wrapper():
        local("python setup.py sdist", capture=False)


@task
def pypi_register():
    """Register and prep user for PyPi upload.

    .. note:: May need to weak ~/.pypirc file per issue:
        http://stackoverflow.com/questions/1569315
    """
    with _dist_wrapper():
        local("python setup.py register", capture=False)


@task
def pypi_upload():
    """Upload package."""
    with _dist_wrapper():
        local("python setup.py sdist upload", capture=False)


###############################################################################
# Downloads
###############################################################################
#def get_rev(tag=True):
    #"""Get build revision.
#
    #@param tag  Use git tag instead of hash?
    #"""
    #rev_cmd = "git describe --always --tag" if tag in (True, "True") else \
              #"git rev-parse HEAD"
    #return local(rev_cmd, capture=True).strip()
#
#
#@task
#def zip_bundle(tag=True):
    #"""Create zip file upload bundles.
#
    #@param tag  Use git tag instead of hash?
    #"""
    ##rev = get_rev(tag)
    #rev = __version__
#
    #print("Cleaning old build files.")
    #clean()
#
    #local("mkdir -p build")
#
    #print("Bundling new files.")
    #with lcd("sphinx_bootstrap_theme/bootstrap"):
        #local("zip -r ../../build/bootstrap.zip .")
#
    #dest = os.path.abspath(os.path.join(DL_DIR, rev))
    #with lcd("build"):
        #local("mkdir -p %s" % dest)
        #local("cp bootstrap.zip %s" % dest)
#
        #print("Verifying contents.")
        #local("unzip -l bootstrap.zip")
