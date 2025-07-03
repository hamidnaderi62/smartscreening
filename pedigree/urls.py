from django.urls import path
from pedigree import views


app_name = "pedigree"



urlpatterns = [
    path('', views.index, name='index'),
    path('generate_pedigree', views.generate_pedigree, name='generate_pedigree'),
    path('clear_data', views.clear_data, name='clear_data'),
]