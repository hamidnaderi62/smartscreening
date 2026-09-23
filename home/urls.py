from django.urls import path
from . import views

app_name = "home"

urlpatterns = [
    path('', views.home, name="home"),
    path('home_fa', views.home_fa, name="home_fa"),
    path('home_en', views.home_en, name="home_en"),
    path('home_ar', views.home_ar, name="home_ar"),
    path('blog/', views.blog_list, name="blog_list"),
    path('blog/<int:pk>/', views.blog_detail, name="blog_detail"),

    path('blog_list_fa', views.blog_list_fa, name="blog_list_fa"),
    path('blog_detail_fa/<int:pk>', views.blog_detail_fa, name="blog_detail_fa"),

    path('team_list', views.team_list, name="team_list"),
]

