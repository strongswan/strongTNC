# -*- coding: utf-8 -*-
from __future__ import print_function, division, absolute_import, unicode_literals

from django.contrib import admin

from . import models


class IdentityAdmin(admin.ModelAdmin):
    list_display = ('data', 'type')
    list_filter = ('type',)


class ResultAdmin(admin.ModelAdmin):
    list_display = ('id', 'result', 'recommendation')
    list_filter = ('recommendation',)


class SessionAdmin(admin.ModelAdmin):
    list_display = ('time', 'recommendation', 'device', 'connection_id')
    list_filter = ('recommendation', 'device', 'identity')


class WorkItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'type', 'session', 'enforcement')
    list_filter = ('type', 'session')


admin.site.register(models.Identity, IdentityAdmin)
admin.site.register(models.Result, ResultAdmin)
admin.site.register(models.Session, SessionAdmin)
admin.site.register(models.WorkItem, WorkItemAdmin)
