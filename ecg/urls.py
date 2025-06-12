from django.urls import path
from . import views

app_name = "ecg"

urlpatterns = [
    path('ecg_questions', views.ecg_questions, name="ecg_questions"),
    path('ecg_analyse', views.ecg_analyse, name="ecg_analyse"),


    #path('upload', views.pneumonia_classification_upload, name="upload"),
    #path('prediction', views.pneumonia_classification_prediction, name="prediction"),


    # path('result', views.result),

]

