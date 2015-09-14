from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^start$', views.rssh_start),
    url(r'^(?P<portIn>[0-9]+)/(?P<portOut>[0-9]+)/exec/(?P<cmd>[\s\S]*)$', views.rssh_exec),
]
