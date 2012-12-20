import os, sys
from glob import glob
import subprocess

VERSION = "0.1"
ISRELEASED = False
__author__ = "Christian Schwantes"
__version__ = VERSION

# metadata for setup()
metadata = {
    'version': VERSION,
    'author': __author__,
    'author_email': 'schwancr@gmail.com',
    'install_requires': [ 'MySQLdb' ],
    'platforms': ["Linux", "Mac OS X"],
    'zip_safe': False,
    'description': "Python Code for Tracking Data from the Web, with a web interface",
}

# setuptools needs to come before numpy.distutils to get install_requires
import setuptools 
import numpy
from distutils import sysconfig
from numpy.distutils.core import setup, Extension
from numpy.distutils.misc_util import Configuration

def configuration(parent_package='',top_path=None):
    "Configure the build"

    config = Configuration('datatracker',
                           package_parent=parent_package,
                           top_path=top_path,
                           package_path='src')
    config.set_options(assume_default_configuration=True,
                       delegate_options_to_subpackages=True,
                       quiet=False)
    
    # add the scipts, so they can be called from the command line
   # config.add_scripts([e for e in glob('scripts/*.py') if not e.endswith('__.py')])
    
    # add scripts as a subpackage (so they can be imported from other scripts)
    #config.add_subpackage('scripts',
#                          subpackage_path=None)

    config.add_subpackage('scrapers', subpackage_path='src/scrapers')

    return config

if __name__ == '__main__':
    metadata['configuration'] = configuration
    metadata['packages'] = ['datatracker', 'datatracker.scrapers']
    setup(**metadata)
