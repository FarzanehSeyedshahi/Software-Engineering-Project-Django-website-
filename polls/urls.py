from . import views
from django.urls import path
from django.conf.urls import include
from django.conf.urls import url
from django.contrib.auth.views import auth_login

app_name = 'polls'
urlpatterns = [

    url(r'^$', views.main, name='main'),
    url(r'^event/$', views.event, name='event'),
    url(r'^new_event/$', views.create_new_event, name='create_new_event'),
    url(r'^new_event/addoption/$', views.add_option, name='add_option'),
    url(r'^login$', auth_login ,{'template_name':'accounts/login.html'}),
    # url('^(?P<pk>[0-9]+)/', )
    path('<int:id>/', views.detail, name='detail'),
    path('<int:id>/results/', views.results, name='results'),
    # path('<int:id>/vote/', views.vote, name='vote'),
    #url(r'^api-auth/', include('rest_framework.urls')),
    #path('login/', include('django.contrib.auth.urls'),name='login'),
    url(r'^signup/$', views.signup_view, name='signup'),

]