from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^start$', views.rssh_start),
    url(r'^(?P<port>[0-9]+)/exec/(?P<cmd>[\s\S]*)$', views.rssh_exec),
    url(r'^(?P<port>[0-9]+)/query$', views.rssh_query),
]
