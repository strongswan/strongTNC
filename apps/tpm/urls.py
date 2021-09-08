from django.conf.urls import re_path
from . import tpm_views, comphash_views

urlpatterns = [
    re_path(r'^tpm/(?P<deviceID>\d+)/evidence/?$', tpm_views.evidence, name='tpm_evidence'),
    re_path(r'^tpm/(?P<deviceID>\d+)/comphashes-delete/?$', tpm_views.comphashes_delete, name='comphashes_delete'),

    re_path(r'^comp_hashes/(?P<comp_hashID>\d+)/?$', comphash_views.comphash, name='comphash_detail'),
    re_path(r'^comp_hashes/save/?$', comphash_views.save, name='comphash_save'),
    re_path(r'^comp_hashes/(?P<comp_hashID>\d+)/delete/?$', comphash_views.delete, name='comphash_delete'),
]
