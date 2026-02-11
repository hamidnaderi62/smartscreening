from django.urls import path
from . import views

app_name = 'pedigree'

urlpatterns = [
    # Dashboard and base URLs
    path('', views.dashboard, name='dashboard'),

    # Family CRUD URLs
    path('families/', views.family_list, name='family_list'),
    path('family/create/', views.create_family, name='create_family'),
    path('family/<int:family_id>/', views.family_detail, name='family_detail'),
    path('family/<int:family_id>/edit/', views.edit_family, name='edit_family'),
    path('family/<int:family_id>/delete/', views.delete_family, name='delete_family'),

    # Individual CRUD URLs
    path('family/<int:family_id>/add-individual/', views.add_individual, name='add_individual'),
    path('individual/<int:individual_id>/', views.individual_detail, name='individual_detail'),
    path('individual/<int:individual_id>/edit/', views.edit_individual, name='edit_individual'),
    path('individual/<int:individual_id>/delete/', views.delete_individual, name='delete_individual'),

    # Analysis URLs
    path('family/<int:family_id>/analysis/', views.family_analysis, name='family_analysis'),
    path('family/<int:family_id>/inheritance-patterns/', views.inheritance_pattern_analysis,
         name='inheritance_patterns'),

    # Visualization URLs
    path('family/<int:family_id>/graph/', views.family_graph, name='family_graph'),
    path('family/<int:family_id>/graph/svg/', views.family_graph_svg, name='family_graph_svg'),
    path('family/<int:family_id>/graph/pdf/', views.family_graph_pdf, name='family_graph_pdf'),

    # Import/Export URLs
    path('family/<int:family_id>/import/', views.bulk_import, name='bulk_import'),
    path('family/<int:family_id>/export/', views.export_family, name='export_family'),
]