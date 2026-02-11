from django.urls import path
from . import views

app_name = "cpanel"

urlpatterns = [
    path('admin_users_list_fa', views.admin_users_list_fa, name="admin_users_list_fa"),

]

