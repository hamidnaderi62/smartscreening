from django.urls import path
from pedigreejs import views

app_name = "pedigreejs"

urlpatterns = [
    path('pedigreejs_index_fa/', views.pedigreejs_index_fa, name='pedigreejs_index_fa'),
    path('pedigree-form/', views.pedigree_form_view, name='pedigree_form'),
    path('save-pedigree/', views.save_pedigree_from_form, name='save_pedigree'),
    path('load-pedigree/', views.load_pedigree, name='load_pedigree'),


    path('pedigreejs_tree_fa/', views.pedigreejs_tree_fa, name='pedigreejs_tree_fa'),
    path('pedigreejs_tree_save/', views.pedigreejs_tree_save, name='pedigreejs_tree_save'),
    path('pedigreejs_tree_load/', views.pedigreejs_tree_load, name='pedigreejs_tree_load'),

    path('get-risk-data/', views.get_risk_data, name='get_risk_data'),

]