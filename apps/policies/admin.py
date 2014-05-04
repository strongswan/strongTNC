# -*- coding: utf-8 -*-
from __future__ import print_function, division, absolute_import, unicode_literals

from django.contrib import admin

from . import models


class EnforcementAdmin(admin.ModelAdmin):
    list_display = ('policy', 'group', 'fail', 'noresult')
    list_filter = ('group', 'fail', 'noresult')


class PolicyAdmin(admin.ModelAdmin):
    list_display = ('name', 'type', 'fail', 'noresult')
    list_filter = ('type', 'fail', 'noresult')


admin.site.register(models.Enforcement, EnforcementAdmin)
admin.site.register(models.Policy, PolicyAdmin)
