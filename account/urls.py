
from django.urls import path
from . import auth_views, views, views_org

app_name = "account"

urlpatterns = [
    path('login/', auth_views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('register/', views.user_register, name='register'),
    path('org/<slug:org_slug>/', views_org.organization_home, name='organization_home'),
    path('org/<slug:org_slug>/register/', views_org.org_register, name='org_register'),
    path('org/<slug:org_slug>/login/', views_org.org_login, name='org_login'),
    path('org/logout/', views_org.org_logout, name='org_logout'),
    path('login_fa', auth_views.user_login_fa, name="login_fa"),
    path('login_en', auth_views.user_login_en, name="login_en"),
    path('login_ar', auth_views.user_login_ar, name="login_ar"),

    path('logout_fa', views.user_logout_fa, name="logout_fa"),
    path('logout_en', views.user_logout_en, name="logout_en"),
    path('logout_ar', views.user_logout_ar, name="logout_ar"),

    path('register_fa', views.user_register_fa, name="register_fa"),
    path('register_en', views.user_register_en, name="register_en"),
    path('register_ar', views.user_register_ar, name="register_ar"),

    path('org/<slug:org_slug>/', views_org.organization_home_fa, name='organization_home_fa'),
    path('org_register_fa/<slug:org_slug>/', views_org.org_register_fa, name='org_register_fa'),
    path('org_login_fa/<slug:org_slug>/', views_org.org_login_fa, name='org_login_fa'),
    path('org_logout_fa', views_org.org_logout_fa, name='org_logout_fa'),

]

