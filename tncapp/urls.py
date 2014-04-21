#
# Copyright (C) 2013 Marco Tanner
# Copyright (C) 2013 Stefan Rohner
# HSR University of Applied Sciences Rapperswil
#
# This file is part of strongTNC.  strongTNC is free software: you can
# redistribute it and/or modify it under the terms of the GNU Affero General
# Public License as published by the Free Software Foundation, either version 3
# of the License, or (at your option) any later version.
#
# strongTNC is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU Affero General Public License for more
# details.
#
# You should have received a copy of the GNU Affero General Public License
# along with strongTNC.  If not, see <http://www.gnu.org/licenses/>.
#

"""
Defines regular expressions for URL's that are served by the web app
"""

from django.conf.urls import patterns, url, include
import group_views, device_views, product_views, policy_views, enforcement_views
import package_views, directory_views, file_views, search_views, views
import regid_views, tag_views

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

    url(r'^groups/?$', group_views.groups, name='groups'),
    url(r'^groups/(?P<groupID>\d+)/?$', group_views.group, name='group'),
    url(r'^groups/add/?$', group_views.add, name='add'),
    url(r'^groups/save/?$', group_views.save, name='save'),
    url(r'^groups/(?P<groupID>\d+)/delete/?$', group_views.delete, name='delete'),
    url(r'^groups/check/?$', group_views.check, name='check'),

    url(r'^devices/?$', device_views.devices, name='devices'),
    url(r'^devices/(?P<deviceID>\d+)/?$', device_views.device, name='device'),
    url(r'^devices/add/?$', device_views.add, name='add'),
    url(r'^devices/save/?$', device_views.save, name='save'),
    url(r'^devices/(?P<deviceID>\d+)/delete/?$', device_views.delete, name='delete'),
    url(r'^devices/search/?$', device_views.search, name='search'),
    url(r'^devices/(?P<device_id>\d+)/toggle/?$', device_views.toggle_trusted, name='toggle_trusted'),

    url(r'^devices/(?P<deviceID>\d+)/report/?$', device_views.report, name='report'),

    url(r'^sessions/(?P<sessionID>\d+)/?$', device_views.session, name='session'),

    url(r'^directories/?$', directory_views.directories, name='directories'),
    url(r'^directories/(?P<directoryID>\d+)/?$', directory_views.directory, name='directory'),
    url(r'^directories/add/?$', directory_views.add, name='add'),
    url(r'^directories/save/?$', directory_views.save, name='save'),
    url(r'^directories/(?P<directoryID>\d+)/delete/?$', directory_views.delete, name='delete'),
    url(r'^directories/search/?$', directory_views.search, name='search'),

    url(r'^files/?$', file_views.files, name='files'),
    url(r'^files/(?P<fileID>\d+)/?$', file_views.file, name='file'),
    url(r'^files/save/?$', file_views.save, name='save'),
    url(r'^files/(?P<fileID>\d+)/delete/?$', file_views.delete, name='delete'),
    url(r'^files/search/?$', file_views.search, name='search'),

    url(r'^file_hashes/(?P<file_hashID>\d+)/delete/?$', file_views.delete_hash, name='delete'),

    url(r'^regids/add/?$', regid_views.add, name='add'),
    url(r'^regids/save/?$', regid_views.save, name='save'),
    url(r'^regids/(?P<regidID>\d+)/delete/?$', regid_views.delete, name='delete'),
    url(r'^regids/search/?$', regid_views.search, name='search'),

    url(r'^tags/?$', tag_views.tags, name='tags'),
    url(r'^tags/(?P<tagID>\d+)/?$', tag_views.tag, name='tag'),
    url(r'^tags/save/?$', tag_views.save, name='save'),
    url(r'^tags/(?P<tagID>\d+)/delete/?$', tag_views.delete, name='delete'),
    url(r'^tags/search/?$', tag_views.search, name='search'),

    url(r'^packages/?$', package_views.packages, name='packages'),
    url(r'^packages/(?P<packageID>\d+)/?$', package_views.package, name='package'),
    url(r'^packages/add/?$', package_views.add, name='add'),
    url(r'^packages/save/?$', package_views.save, name='save'),
    url(r'^packages/(?P<packageID>\d+)/delete/?$', package_views.delete, name='delete'),
    url(r'^packages/search/?$', package_views.search, name='search'),
    url(r'^packages/check/?$', package_views.check, name='check'),

    url(r'^versions/(?P<versionID>\d+)/toggle/?$', package_views.toggle_version, name='toggle_version'),

    url(r'^products/?$', product_views.products, name='products'),
    url(r'^products/(?P<productID>\d+)/?$', product_views.product, name='product'),
    url(r'^products/add/?$', product_views.add, name='product_add'),
    url(r'^products/save/?$', product_views.save, name='product_save'),
    url(r'^products/(?P<productID>\d+)/delete/?$', product_views.delete, name='delete'),
    url(r'^products/search/?$', product_views.search, name='search'),
    url(r'^products/check/?$', product_views.check, name='check'),

    url(r'^policies/?$', policy_views.policies, name='policies'),
    url(r'^policies/(?P<policyID>\d+)/?$', policy_views.policy, name='policy'),
    url(r'^policies/add/?$', policy_views.add, name='add'),
    url(r'^policies/save/?$', policy_views.save, name='save'),
    url(r'^policies/(?P<policyID>\d+)/delete/?$', policy_views.delete, name='delete'),
    url(r'^policies/search/?$', policy_views.search, name='search'),
    url(r'^policies/check/?$', policy_views.check, name='check'),

    url(r'^enforcements/?$', enforcement_views.enforcements, name='enforcements'),
    url(r'^enforcements/(?P<enforcementID>\d+)/?$', enforcement_views.enforcement, name='enforcement'),
    url(r'^enforcements/add/?$', enforcement_views.add, name='add'),
    url(r'^enforcements/save/?$', enforcement_views.save, name='save'),
    url(r'^enforcements/(?P<enforcementID>\d+)/delete/?$', enforcement_views.delete, name='delete'),
    url(r'^enforcements/search/?$', enforcement_views.search, name='search'),
    url(r'^enforcements/check/?$', enforcement_views.check, name='check'),

    # IMV API patterns
    url(r'^cmd/start_session/?$', views.start_session, name='start_session'),
    url(r'^cmd/end_session/?$', views.end_session, name='end_session'),

    url(dajaxice_config.dajaxice_url, include('dajaxice.urls')),
)

urlpatterns += staticfiles_urlpatterns()
