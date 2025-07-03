from django.shortcuts import render, redirect
from .forms import FamilyMemberForm
from .models import FamilyMember
import graphviz
import tempfile
import os
from django.http import FileResponse
from django.conf import settings


def index(request):
    if request.method == 'POST':
        form = FamilyMemberForm(request.POST)
        if form.is_valid():
            member = form.save()
            member.parents.set(form.cleaned_data['parents'])
            return redirect('index')
    else:
        form = FamilyMemberForm()

    members = FamilyMember.objects.all()
    return render(request, 'pedigree/index.html', {
        'form': form,
        'members': members,
    })


def generate_pedigree(request):
    members = FamilyMember.objects.all()

    dot = graphviz.Digraph(comment='Advanced Pedigree')
    dot.attr(rankdir='TB', fontsize='12')

    for member in members:
        shape = 'circle' if member.gender == 'F' else 'box'

        if member.affected == 'C':
            color = 'red'
            style = 'filled'
            fillcolor = 'pink'
        elif member.genes:
            color = 'blue'
            style = 'filled'
            fillcolor = 'lightblue'
        else:
            color = 'black'
            style = ''
            fillcolor = ''

        label = f"{member.name} (ID:{member.id})\nسن: {member.age}\n"
        if member.status == 'D':
            label = f"<s>{label}</s>"
        if member.affected == 'C':
            label += f"سرطان: {member.cancer_type} (تشخیص: {member.age_diagnosis})\n"
        if member.genes:
            label += f"ژن: {member.genes}\n"
        label += f"وضعیت: {member.get_status_display()}"

        dot.node(str(member.id), label=label, shape=shape,
                 color=color, style=style, fillcolor=fillcolor)

    for member in members:
        for p in member.parents.all():
            dot.edge(str(p.id), str(member.id))

    # Save to temporary file
    temp_dir = os.path.join(settings.MEDIA_ROOT, 'temp')
    os.makedirs(temp_dir, exist_ok=True)
    temp_path = os.path.join(temp_dir, 'pedigree')

    dot.render(temp_path, format='png')

    # Return the image
    with open(temp_path + '.png', 'rb') as f:
        return FileResponse(f, content_type='image/png')


def clear_data(request):
    FamilyMember.objects.all().delete()
    return redirect('index')