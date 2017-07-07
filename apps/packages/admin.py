# -*- coding: utf-8 -*-
from __future__ import print_function, division, absolute_import, unicode_literals

from django.contrib import admin

from . import models


class VersionAdmin(admin.ModelAdmin):
    list_display = ('package', 'release', 'product', 'time')
    list_filter = ('security', 'product')


admin.site.register(models.Package)
admin.site.register(models.Version, VersionAdmin)
