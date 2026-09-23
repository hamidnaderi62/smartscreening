
from django.urls import path
from . import views
from . import report_views

app_name = "my_model"

urlpatterns = [
    path('screenings/', views.screening_list, name='screening_list'),
    # Compatibility URL used by existing bookmarks and older page links.
    path('screening_list', views.screening_list, name='screening_list_compat'),
    path('screening_list/', views.screening_list, name='screening_list_compat_slash'),
    path('screenings/questions/', views.question, name='question'),
    path('screenings/calculate/', views.calculate_my_model, name='calculate'),
    path('dashboard/', report_views.dashboard, name='dashboard'),
    path('dashboard/assessment/<int:assessment_id>/', report_views.dashboard_detail, name='dashboard_detail'),
    path('dashboard/report/<str:code>/', report_views.dashboard_comprehensive, name='dashboard_comprehensive'),
    path('reports/pdf/<int:model_id>/', views.download_pdf_report, name='pdf_report'),
    path('reports/pdf/', views.download_pdf_report, name='pdf_report_latest'),
    path('screening_list_fa', views.screening_list_fa, name="screening_list_fa"),
    path('screening_list_en', views.screening_list_en, name="screening_list_en"),
    path('screening_list_ar', views.screening_list_ar, name="screening_list_ar"),


    path('question_fa', views.question_fa, name="question_fa"),
    path('question_en', views.question_en, name="question_en"),
    path('question_ar', views.question_ar, name="question_ar"),

    path('calculate_my_model/', views.calculate_my_model, name="calculate_my_model"),

    path('dashboard_fa', report_views.dashboard_fa, name="dashboard_fa"),
    path('dashboard_en', report_views.dashboard_en, name="dashboard_en"),
    path('dashboard_ar', report_views.dashboard_ar, name="dashboard_ar"),


    path('dashboard_detail_fa/<int:assessment_id>', report_views.dashboard_detail_fa, name="dashboard_detail_fa"),
    path('dashboard_detail_en/<int:assessment_id>', report_views.dashboard_detail_en, name="dashboard_detail_en"),
    path('dashboard_detail_ar/<int:assessment_id>', report_views.dashboard_detail_ar, name="dashboard_detail_ar"),

    path('dashboard_comprehensive_fa/<str:code>', report_views.dashboard_comprehensive_fa, name="dashboard_comprehensive_fa"),
    path('dashboard_comprehensive_en/<str:code>', report_views.dashboard_comprehensive_en, name="dashboard_comprehensive_en"),
    path('dashboard_comprehensive_ar/<str:code>', report_views.dashboard_comprehensive_ar, name="dashboard_comprehensive_ar"),

    path('save_doctor_comment', views.save_doctor_comment, name="save_doctor_comment"),

    path('download_pdf_report/<int:model_id>', views.download_pdf_report, name="download_pdf_report"),
    path('download_pdf_report/', views.download_pdf_report, name="download_pdf_report_latest"),

]

