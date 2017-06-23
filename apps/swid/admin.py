# -*- coding: utf-8 -*-
from __future__ import print_function, division, absolute_import, unicode_literals

from django.contrib import admin

from . import models


class EventAdmin(admin.ModelAdmin):
    list_display = ('device', 'epoch', 'eid', 'timestamp')
    list_filter = ('device', )


class TagEventAdmin(admin.ModelAdmin):
    list_display = ('tag', 'event', 'record_id', 'action')


admin.site.register(models.Tag)
admin.site.register(models.TagStats)
admin.site.register(models.TagEvent, TagEventAdmin)
admin.site.register(models.Entity)
admin.site.register(models.EntityRole)
admin.site.register(models.Event, EventAdmin)
