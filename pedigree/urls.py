from django.urls import path
from pedigree import views


app_name = "pedigree"



urlpatterns = [
    path('index_en', views.index_en, name='index_en'),
    path('index_fa', views.index_fa, name='index_fa'),
    path('edit/<int:member_id>/', views.edit_member, name='edit_member'),
    path('delete/<int:member_id>/', views.delete_member, name='delete_member'),
    path('generate_pedigree_graphviz', views.generate_pedigree_graphviz, name='generate_pedigree_graphviz'),
    path('generate_pedigree_networkx', views.generate_pedigree_networkx, name='generate_pedigree_networkx'),
    path('clear_data', views.clear_data, name='clear_data'),


    path('pedigree-js/', views.pedigree_js_view, name='pedigree_js'),
    path('api/pedigree-data/', views.get_pedigree_data, name='get_pedigree_data'),
    path('api/save-pedigree/', views.save_pedigree_data, name='save_pedigree_data'),
]