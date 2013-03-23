from django.contrib import admin
import cygapp.models as models

admin.site.register(models.File)
admin.site.register(models.FileHash)
admin.site.register(models.Device)
admin.site.register(models.Policy)
admin.site.register(models.Group)
admin.site.register(models.Product)
admin.site.register(models.Package)
admin.site.register(models.Enforcement)

