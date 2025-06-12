from django.shortcuts import render,get_object_or_404
from django.urls import reverse
from django.core.paginator import Paginator

def home(request):
    return render(request, 'home.html', context={})

def home_fa(request):
    return render(request, 'home_fa.html', context={})
