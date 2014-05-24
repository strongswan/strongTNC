# -*- coding: utf-8 -*-
from __future__ import print_function, division, absolute_import, unicode_literals

from django.contrib import admin

from . import models


admin.site.register(models.Tag)
admin.site.register(models.Entity)
admin.site.register(models.EntityRole)
