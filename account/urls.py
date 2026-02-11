from django.urls import path
from . import views

app_name = "account"

urlpatterns = [
    path('org_register_fa/<slug:org_slug>/', views.org_register_fa, name='org_register_fa'),
    path('org_login_fa/<slug:org_slug>/', views.org_login_fa, name='org_login_fa'),
    path('org_logout_fa', views.org_logout_fa, name='org_logout_fa'),
]

