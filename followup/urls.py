from django.urls import path

from . import views

app_name = 'followup'

urlpatterns = [
    path('', views.follow_up_list, name='list'),
]
