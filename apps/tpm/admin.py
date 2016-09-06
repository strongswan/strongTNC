# -*- coding: utf-8 -*-
from __future__ import print_function, division, absolute_import, unicode_literals

from django.contrib import admin

from . import models


class ComponentAdmin(admin.ModelAdmin):
    list_display = ('label', 'vendor_id', 'name', 'qualifier')


class ComponentHashAdmin(admin.ModelAdmin):
    list_display = ('component', 'seq_no', 'pcr', 'algorithm', 'hash', 'device')
    list_filter = ('device', 'component')


admin.site.register(models.Component, ComponentAdmin)
admin.site.register(models.ComponentHash, ComponentHashAdmin)
