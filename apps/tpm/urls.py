from django.conf.urls import patterns, url
from . import tpm_views

urlpatterns = patterns('',
    url(r'^tpm/(?P<deviceID>\d+)/evidence/?$', tpm_views.evidence, name='tpm_evidence'),

    url(r'^comp_hashes/(?P<comp_hashID>\d+)/delete/?$', tpm_views.delete_hash, name='comphash_delete'),
)
