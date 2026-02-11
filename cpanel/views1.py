from django.shortcuts import render,get_object_or_404
from django.urls import reverse
from django.db.models import Count
from account.models import User,Profile,Organization
from django.core.paginator import Paginator
from django.http import HttpResponse,JsonResponse
from django.core import serializers

def admin_users_list_fa(request):
    context = {}
    organization = Organization.objects.get(id=request.session['organization_id'])
    org_users = User.objects.filter(profile__organization=organization,profile__user_type='Person').order_by('-date_joined')
    context['org_users'] = org_users
    return render(request, 'admin_users_list_fa.html', context)