from django.shortcuts import render,get_object_or_404
from django.urls import reverse
from django.db.models import Count
from .models import Blog,Team
from django.core.paginator import Paginator
from django.http import HttpResponse,JsonResponse
from django.core import serializers

def home(request):
    return render(request, 'home.html', context={})

def home_fa(request):
    all_blogs = Blog.objects.filter(is_active= True).all().order_by('-created')
    blogs = all_blogs[:4]

    main_teams = Team.objects.filter(is_active=True, team_type='Main').all()
    advisor_teams = Team.objects.filter(is_active=True, team_type='Advisor').all()

    return render(request, 'home_fa.html', context={'blogs':blogs, 'main_teams':main_teams, 'advisor_teams':advisor_teams})


def blog_list_fa(request):
    all_blogs = Blog.objects.filter(is_active=True).all()
    page_number = request.GET.get('page')
    paginator = Paginator(all_blogs, 4)
    blogs = paginator.get_page(page_number)

    return render(request, 'blog_list_fa.html', context={'blogs':blogs})

def blog_detail_fa(request, pk=None):
    blog = get_object_or_404(Blog, id=pk)
    return render(request, 'blog_detail_fa.html', context={'blog':blog})



def team_list(request):
    teams = Team.objects.filter(is_active=True).all()
    data = list(teams.values())
    return JsonResponse(data, safe=False)