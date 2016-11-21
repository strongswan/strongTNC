from django.conf.urls import patterns, url
from . import tpm_views, comphash_views

urlpatterns = patterns('',
    url(r'^tpm/(?P<deviceID>\d+)/evidence/?$', tpm_views.evidence, name='tpm_evidence'),
    url(r'^tpm/(?P<deviceID>\d+)/comphashes-delete/?$', tpm_views.comphashes_delete, name='comphashes_delete'),

    url(r'^comp_hashes/(?P<comp_hashID>\d+)/?$', comphash_views.comphash, name='comphash_detail'),
    url(r'^comp_hashes/save/?$', comphash_views.save, name='comphash_save'),
    url(r'^comp_hashes/(?P<comp_hashID>\d+)/delete/?$', comphash_views.delete, name='comphash_delete'),
)
