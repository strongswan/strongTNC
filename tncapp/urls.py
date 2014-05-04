"""
Defines regular expressions for URL's that are served by the web app.
"""

from django.conf.urls import patterns, url, include
import search_views, views

from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from dajaxice.core import dajaxice_autodiscover, dajaxice_config

dajaxice_autodiscover()

urlpatterns = patterns('',
    url(r'^$', views.overview, name='overview'),
    url(r'^overview/?$', views.overview, name='overview'),
    url(r'^statistics/?$', views.statistics, name='statistics'),

    url(r'^login/?$', views.login, name='login'),
    url(r'^logout/?$', views.logout, name='logout'),

    url(r'^search/?$', search_views.search, name='search'),

    # IMV API patterns
    url(r'^cmd/start_session/?$', views.start_session, name='start_session'),
    url(r'^cmd/end_session/?$', views.end_session, name='end_session'),

    url(dajaxice_config.dajaxice_url, include('dajaxice.urls')),
)

urlpatterns += staticfiles_urlpatterns()
