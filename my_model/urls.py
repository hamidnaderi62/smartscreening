
from django.urls import path
from . import views

app_name = "my_model"

urlpatterns = [
    path('screening_list_fa', views.screening_list_fa, name="screening_list_fa"),
    path('question_fa', views.question_fa, name="question_fa"),
    path('calculate_my_model', views.calculate_my_model, name="calculate_my_model"),
    path('dashboard_fa', views.dashboard_fa, name="dashboard_fa"),
    path('dashboard_detail_fa', views.dashboard_detail_fa, name="dashboard_detail_fa"),
]

