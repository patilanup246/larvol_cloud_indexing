from django.urls import path, re_path
from dashboard import views
app_name = 'dashboard'

urlpatterns = [
    re_path(r'^$', views.login, name='login'),
    re_path(r'homepage/$', views.homepage, name='homepage'),
    re_path(r'schedule/$', views.schedule, name='schedule'),
    re_path(r'schedule-start/$', views.schedule_start, name='schedule_start'),
    re_path(r'view-data/(?P<string>[\w\-]+)/$', views.view_data, name='view_data'),
    re_path(r'export-data/(?P<string>[\w\-]+)/$', views.export_data, name='export_data'),
    re_path('logout/',views.logout,name='logout'),
    # re_path(r'view-data/$', views.view_data, name='view_data'),
]