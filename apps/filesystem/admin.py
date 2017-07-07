# -*- coding: utf-8 -*-
from __future__ import print_function, division, absolute_import, unicode_literals

from django.contrib import admin

from . import models


class AlgorithmAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')


class FileHashAdmin(admin.ModelAdmin):
    list_display = ('file', 'algorithm', 'hash')
    list_filter = ('algorithm', 'version__product')


class FileAdmin(admin.ModelAdmin):
    search_fields = ('directory__path', 'name')


admin.site.register(models.Algorithm, AlgorithmAdmin)
admin.site.register(models.Directory)
admin.site.register(models.File, FileAdmin)
admin.site.register(models.FileHash, FileHashAdmin)
