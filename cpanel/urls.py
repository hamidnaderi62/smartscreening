from django.urls import path
from . import views, platform_views

app_name = "cpanel"

urlpatterns = [
    path('platform/', platform_views.platform_dashboard, name='platform_dashboard'),
    path('organization/', views.organization_dashboard, name='organization_dashboard'),
    path('organization/users/', views.admin_users_list, name='admin_users_list'),
    path('organization/users/<int:user_id>/toggle/', views.toggle_user_status_i18n, name='toggle_user_status_i18n'),
    path('organization/reports/', views.organization_reports, name='organization_reports'),
    path('organization_dashboard_fa', views.organization_dashboard_fa, name="organization_dashboard_fa"),
    path('admin_users_list_fa', views.admin_users_list_fa, name="admin_users_list_fa"),
    path('toggle_user_status/<int:user_id>', views.toggle_user_status, name="toggle_user_status"),
    path('organization_reports_fa', views.organization_reports_fa, name="organization_reports_fa"),

]

