"""untitled1 URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.conf.urls import url
from django.contrib import admin
from django.views.static import serve
from CTFweb import views
from untitled1 import settings

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^$', views.home),
    url(r'^help/$', views.help),
    url(r'^regist/$', views.regist),
    url(r'^login/$', views.login),
    url(r'^logout/$', views.logout),
    url(r'^forget/$', views.forget),
    url(r'^reset/$', views.reset),
    url(r'^info/$', views.info),
    url(r'^team/$', views.team),
    url(r'^rank/$', views.rank),
    url(r'^teamCreate/$', views.teamCreate),
    url(r'^teamJoin/$', views.teamJoin),
    url(r'^problems/(?P<pro_type>.*)$', views.problems),
    url(r'^team_name_rewrite/$', views.team_name_rewrite),
    url(r'^team_motto_rewrite/$', views.team_motto_rewrite),
    url(r'^dismiss/$', views.dismiss),
    url(r'^quit_team/$', views.quit_team),
    url(r'^name_rewrite/$', views.name_rewrite),
    url(r'^motto_rewrite/$', views.motto_rewrite),
    url(r'^problem/$', views.problem),
    url(r'^pro_answer/$', views.pro_answer),
    url(r'^wp_upload/(?P<pro_id>.*)$', views.wp_upload),
    url(r'^wp_download/(?P<wp_id>.*)$', views.wp_download),
    url(r'^kick/$', views.kick_out),
    url(r'^agree/$', views.agree),
    url(r'^deny/$', views.deny),
    url(r'^wp/(?P<path>.*)$', serve, {'document_root': settings.WP_ROOT}),
    url(r'^agree_wp/$', views.agree_wp),
    url(r'^wp_list/$', views.wp),
    url(r'^pro_source_download/(?P<name>.*)', views.pro_source_download),

    url(r'^web1/$', views.web1),
    url(r'^web2/$', views.web2),
]

