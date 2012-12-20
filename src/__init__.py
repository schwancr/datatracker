"""Need this file I think."""

import os
import warnings

# These are annoying warnings that MySQLdb throws when doing:
# > create database if not exists database_name;
warnings.filterwarnings('ignore', message='.*database exists', append=True)
warnings.filterwarnings('ignore', message='.*table .* already exists', append=True)

# Put default global variables in this file.
DEFAULT_STORAGE_LOCATION = os.path.join(os.environ['HOME'], 'tmp')
DB_NAME = 'datatracker'
