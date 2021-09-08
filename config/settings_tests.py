# -*- coding: utf-8 -*-
# Django settings for strongTNC during tests

# Import base settings
from .settings import *

# Ignore migrations in the auth module as our virtual permission model can't
# have any
MIGRATION_MODULES = {
    'auth': None,
}
