from django.conf.urls import url
from . import policy_views, enforcement_views

urlpatterns = [
    url(r'^policies/?$', policy_views.policies, name='policy_list'),
    url(r'^policies/(?P<policyID>\d+)/?$', policy_views.policy, name='policy_detail'),
    url(r'^policies/add/?$', policy_views.add, name='policy_add'),
    url(r'^policies/save/?$', policy_views.save, name='policy_save'),
    url(r'^policies/(?P<policyID>\d+)/delete/?$', policy_views.delete, name='policy_delete'),
    url(r'^policies/check/?$', policy_views.check, name='policy_check'),

    url(r'^enforcements/?$', enforcement_views.enforcements, name='enforcement_list'),
    url(r'^enforcements/(?P<enforcementID>\d+)/?$', enforcement_views.enforcement, name='enforcement_detail'),
    url(r'^enforcements/add/?$', enforcement_views.add, name='enforcement_add'),
    url(r'^enforcements/save/?$', enforcement_views.save, name='enforcement_save'),
    url(r'^enforcements/(?P<enforcementID>\d+)/delete/?$', enforcement_views.delete, name='enforcement_delete'),
    url(r'^enforcements/check/?$', enforcement_views.check, name='enforcement_check'),
]
