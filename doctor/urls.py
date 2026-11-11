from django.urls import path

from . import views

app_name = 'doctor'

urlpatterns = [
    path('login/', views.doctor_login, name='login'),
    path('logout/', views.doctor_logout, name='logout'),
    path('dashboard/', views.doctor_dashboard, name='dashboard'),
    path('screenings/<int:screening_id>/recommendations/', views.recommendations, name='recommendations'),
    path('screenings/<int:screening_id>/doctor/<int:doctor_id>/refer/', views.create_screening_referral, name='create_screening_referral'),
    path('screenings/<int:screening_id>/doctors/<int:doctor_id>/assessments/<int:assessment_id>/refer/', views.create_referral, name='create_referral'),
    path('referrals/<int:referral_id>/', views.referral_detail, name='referral_detail'),
    path('referrals/<int:referral_id>/comment/', views.save_comment, name='save_comment'),
    path('referrals/<int:referral_id>/status/', views.update_status, name='update_status'),
]
