"""
Defines regular expressions for URL's that are served by the web app.
"""

from django.conf.urls import patterns, url, include
import policy_views, enforcement_views
import package_views, search_views, views

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

    url(r'^packages/?$', package_views.packages, name='packages'),
    url(r'^packages/(?P<packageID>\d+)/?$', package_views.package, name='package'),
    url(r'^packages/add/?$', package_views.add, name='add'),
    url(r'^packages/save/?$', package_views.save, name='save'),
    url(r'^packages/(?P<packageID>\d+)/delete/?$', package_views.delete, name='delete'),
    url(r'^packages/check/?$', package_views.check, name='check'),

    url(r'^versions/(?P<versionID>\d+)/toggle/?$', package_views.toggle_version, name='toggle_version'),

    url(r'^policies/?$', policy_views.policies, name='policies'),
    url(r'^policies/(?P<policyID>\d+)/?$', policy_views.policy, name='policy'),
    url(r'^policies/add/?$', policy_views.add, name='add'),
    url(r'^policies/save/?$', policy_views.save, name='save'),
    url(r'^policies/(?P<policyID>\d+)/delete/?$', policy_views.delete, name='delete'),
    url(r'^policies/check/?$', policy_views.check, name='check'),

    url(r'^enforcements/?$', enforcement_views.enforcements, name='enforcements'),
    url(r'^enforcements/(?P<enforcementID>\d+)/?$', enforcement_views.enforcement, name='enforcement'),
    url(r'^enforcements/add/?$', enforcement_views.add, name='add'),
    url(r'^enforcements/save/?$', enforcement_views.save, name='save'),
    url(r'^enforcements/(?P<enforcementID>\d+)/delete/?$', enforcement_views.delete, name='delete'),
    url(r'^enforcements/check/?$', enforcement_views.check, name='check'),

    # IMV API patterns
    url(r'^cmd/start_session/?$', views.start_session, name='start_session'),
    url(r'^cmd/end_session/?$', views.end_session, name='end_session'),

    url(dajaxice_config.dajaxice_url, include('dajaxice.urls')),
)

urlpatterns += staticfiles_urlpatterns()
