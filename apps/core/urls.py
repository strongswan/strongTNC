from django.conf.urls import patterns, url
from . import views

urlpatterns = patterns('',
    # IMV API patterns
    url(r'^cmd/start_session/?$', views.start_session, name='start_session'),
    url(r'^cmd/end_session/?$', views.end_session, name='end_session'),
)
