from django.urls import path
from . import views

app_name = "home"

urlpatterns = [
    path('', views.home_fa, name="home_fa"),
    path('home_fa', views.home_fa, name="home_fa"),
    path('blog_list_fa', views.blog_list_fa, name="blog_list_fa"),
    path('blog_detail_fa/<int:pk>', views.blog_detail_fa, name="blog_detail_fa"),
]

