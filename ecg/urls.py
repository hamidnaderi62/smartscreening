from django.urls import path
from . import views

app_name = "ecg"

urlpatterns = [
    path('ecg_questions_fa', views.ecg_questions_fa, name="ecg_questions_fa"),
    path('ecg_analyse_fa', views.ecg_analyse_fa, name="ecg_analyse_fa"),


    #path('upload', views.pneumonia_classification_upload, name="upload"),
    #path('prediction', views.pneumonia_classification_prediction, name="prediction"),


    # path('result', views.result),

]

