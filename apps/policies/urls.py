from django.conf.urls import re_path
from . import policy_views, enforcement_views

urlpatterns = [
    re_path(r'^policies/?$', policy_views.policies, name='policy_list'),
    re_path(r'^policies/(?P<policyID>\d+)/?$', policy_views.policy, name='policy_detail'),
    re_path(r'^policies/add/?$', policy_views.add, name='policy_add'),
    re_path(r'^policies/save/?$', policy_views.save, name='policy_save'),
    re_path(r'^policies/(?P<policyID>\d+)/delete/?$', policy_views.delete, name='policy_delete'),
    re_path(r'^policies/check/?$', policy_views.check, name='policy_check'),

    re_path(r'^enforcements/?$', enforcement_views.enforcements, name='enforcement_list'),
    re_path(r'^enforcements/(?P<enforcementID>\d+)/?$', enforcement_views.enforcement, name='enforcement_detail'),
    re_path(r'^enforcements/add/?$', enforcement_views.add, name='enforcement_add'),
    re_path(r'^enforcements/save/?$', enforcement_views.save, name='enforcement_save'),
    re_path(r'^enforcements/(?P<enforcementID>\d+)/delete/?$', enforcement_views.delete, name='enforcement_delete'),
    re_path(r'^enforcements/check/?$', enforcement_views.check, name='enforcement_check'),
]
