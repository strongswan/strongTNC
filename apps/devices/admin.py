# -*- coding: utf-8 -*-
from __future__ import print_function, division, absolute_import, unicode_literals

from django.contrib import admin

from . import models


class DeviceAdmin(admin.ModelAdmin):
    list_display = ('description', 'value', 'created')
    list_filter = ('product', 'trusted', 'inactive')


class GroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent')


admin.site.register(models.Device, DeviceAdmin)
admin.site.register(models.Group, GroupAdmin)
admin.site.register(models.Product)
