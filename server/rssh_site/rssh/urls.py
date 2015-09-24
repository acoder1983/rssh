from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^start$', views.rssh_start),
    url(r'^(?P<port>[0-9]+)/exec/(?P<cmd>[\s\S]*)$', views.rssh_exec),
    url(r'^(?P<port>[0-9]+)/query$', views.rssh_query),
    url(r'^(?P<rfile>[0-9]+)/md5$', views.rssh_file_md5),
    url(r'^(?P<rfile>[0-9]+)/put/(?P<content>[a-f0-9]+)$', views.rssh_put_file),
]
