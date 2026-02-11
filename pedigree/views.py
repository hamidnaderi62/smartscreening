from django.shortcuts import render, redirect
from .forms import FamilyMemberForm
from .models import FamilyMember
import graphviz
import tempfile
import os
from django.http import FileResponse
from django.conf import settings
from django.shortcuts import render
import base64
import io
import matplotlib.pyplot as plt
import networkx as nx

from collections import defaultdict


def calculate_family_risk1(members):
    """Calculate cancer risk factors for the family"""
    risk_factors = {
        'total_members': 0,
        'affected_count': 0,
        'average_diagnosis_age': 0,
        'gene_mutations': defaultdict(int),
        'cancer_types': defaultdict(int),
        'generations': defaultdict(set)
    }

    # Calculate basic statistics
    diagnosis_ages = []
    for member in members:
        risk_factors['total_members'] += 1
        if member.affected == 'C':
            risk_factors['affected_count'] += 1
            diagnosis_ages.append(member.age_diagnosis)
            risk_factors['cancer_types'][member.cancer_type] += 1

        if member.genes:
            for gene in member.genes.split(','):
                cleaned_gene = gene.strip().upper()
                if cleaned_gene:
                    risk_factors['gene_mutations'][cleaned_gene] += 1

        # Track generations by finding the longest parent chain
        generation = 0
        if member.parents.exists():
            generation = max(p.generation for p in member.parents.all()) + 1
        member.generation = generation
        risk_factors['generations'][generation].add(member.id)

    # Calculate averages
    if diagnosis_ages:
        risk_factors['average_diagnosis_age'] = sum(diagnosis_ages) / len(diagnosis_ages)

    # Add this to your calculate_family_risk function
    # Calculate risk by generation
    risk_factors['generation_risks'] = {}
    for gen, members in risk_factors['generations'].items():
        total = len(members)
        affected = sum(1 for m in members if m.affected == 'C')
        risk_factors['generation_risks'][gen] = {
            'total': total,
            'affected': affected,
            'percentage': (affected / total) * 100 if total > 0 else 0
        }

    # Check for known high-risk genes
    known_high_risk_genes = {'BRCA1', 'BRCA2', 'TP53', 'PTEN', 'APC'}
    for gene in risk_factors['gene_mutations']:
        if gene in known_high_risk_genes:
            risk_factors['risk_level'] = "خیلی بالا"
            break

    # Calculate risk level
    affected_percentage = (risk_factors['affected_count'] / risk_factors['total_members']) * 100
    if affected_percentage > 30:
        risk_factors['risk_level'] = "بالا"
    elif affected_percentage > 15:
        risk_factors['risk_level'] = "متوسط"
    else:
        risk_factors['risk_level'] = "پایین"

    return risk_factors


from collections import defaultdict
from django.db.models import Avg
def calculate_family_risk(members):
    """Calculate cancer risk factors for the family"""
    risk_factors = {
        'total_members': members.count(),
        'affected_count': members.filter(affected='C').count(),
        'average_diagnosis_age': 0,
        'gene_mutations': defaultdict(int),
        'cancer_types': defaultdict(int),  # Ensure this is a defaultdict
        'generation_risks': defaultdict(lambda: {'total': 0, 'affected': 0})
    }

    # Calculate average diagnosis age
    affected_members = members.filter(affected='C').exclude(age_diagnosis__isnull=True)
    risk_factors['average_diagnosis_age'] = affected_members.aggregate(
        avg_age=Avg('age_diagnosis')
    )['avg_age'] or 0

    # Count cancer types and gene mutations
    for member in members.filter(affected='C'):
        if member.cancer_type:  # Only count if cancer_type exists
            risk_factors['cancer_types'][member.cancer_type] += 1

        if member.genes:
            for gene in member.genes.split(','):
                cleaned_gene = gene.strip().upper()
                if cleaned_gene:
                    risk_factors['gene_mutations'][cleaned_gene] += 1

    # Convert defaultdicts to regular dicts for template
    risk_factors['cancer_types'] = dict(risk_factors['cancer_types'])
    risk_factors['gene_mutations'] = dict(risk_factors['gene_mutations'])
    risk_factors['generation_risks'] = dict(risk_factors['generation_risks'])

    # Calculate risk level
    if risk_factors['total_members'] > 0:
        affected_percentage = (risk_factors['affected_count'] / risk_factors['total_members']) * 100
    else:
        affected_percentage = 0

    if affected_percentage > 30:
        risk_factors['risk_level'] = "بالا"
    elif affected_percentage > 15:
        risk_factors['risk_level'] = "متوسط"
    else:
        risk_factors['risk_level'] = "پایین"

    return risk_factors


def index_en(request):
    if request.method == 'POST':
        form = FamilyMemberForm(request.POST)
        if form.is_valid():
            member = form.save()
            member.parents.set(form.cleaned_data['parents'])
            return redirect('pedigree:index_en')
    else:
        form = FamilyMemberForm()

    members = FamilyMember.objects.all()
    risk_factors = calculate_family_risk(members)

    return render(request, 'pedigree/index_en.html', {
        'form': form,
        'members': members,
        'risk_factors': risk_factors
    })


def index_fa(request):
    if request.method == 'POST':
        form = FamilyMemberForm(request.POST)
        if form.is_valid():
            member = form.save()
            member.parents.set(form.cleaned_data['parents'])
            return redirect('pedigree:index_fa')
    else:
        form = FamilyMemberForm()

    members = FamilyMember.objects.all()
    risk_factors = calculate_family_risk(members)

    return render(request, 'pedigree/index_fa.html', {
        'form': form,
        'members': members,
        'risk_factors': risk_factors
    })




def generate_pedigree_graphviz(request):
    members = FamilyMember.objects.all()

    # Create Graphviz digraph
    dot = graphviz.Digraph(comment='Advanced Pedigree')
    dot.attr(rankdir='TB', fontsize='12', fontname='Arial')

    # Add nodes
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

    # Add edges
    for member in members:
        for parent in member.parents.all():
            dot.edge(str(parent.id), str(member.id))

    # Render the graph to PNG bytes
    png_bytes = dot.pipe(format='png')

    # Convert to base64 for embedding in HTML
    image_base64 = base64.b64encode(png_bytes).decode('utf-8')

    # Pass to template
    return render(request, 'pedigree/pedigree_display.html', {
        'pedigree_image': image_base64
    })




def generate_pedigree_networkx(request):
    members = FamilyMember.objects.all()
    G = nx.DiGraph()

    # Add nodes with attributes
    for member in members:
        node_color = 'pink' if member.gender == 'F' else 'lightblue'
        if member.affected == 'C':
            node_color = 'red'

        G.add_node(
            member.id,
            label=f"{member.name}\nAge: {member.age}",
            gender=member.gender,
            affected=member.affected,
            color=node_color
        )

    # Add edges
    for member in members:
        for parent in member.parents.all():
            G.add_edge(parent.id, member.id)

    # Draw the graph
    plt.figure(figsize=(12, 8))
    pos = nx.spring_layout(G)  # You can try different layouts

    # Draw nodes with colors
    node_colors = [G.nodes[node]['color'] for node in G.nodes()]
    nx.draw_networkx_nodes(G, pos, node_color=node_colors, node_size=2000)
    nx.draw_networkx_edges(G, pos, arrowstyle='-|>', arrowsize=20)

    # Add labels
    labels = {node: G.nodes[node]['label'] for node in G.nodes()}
    nx.draw_networkx_labels(G, pos, labels, font_size=10)

    plt.title("Family Pedigree Tree")
    plt.axis('off')

    # Save to a bytes buffer
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png', bbox_inches='tight')
    plt.close()

    # Convert to base64 for HTML
    image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
    buffer.close()

    return render(request, 'pedigree/pedigree_result.html', {
        'pedigree_image': image_base64
    })


# pedigree/views.py
from django.shortcuts import get_object_or_404, redirect


def edit_member(request, member_id):
    member = get_object_or_404(FamilyMember, id=member_id)
    if request.method == 'POST':
        form = FamilyMemberForm(request.POST, instance=member)
        if form.is_valid():
            form.save()
            return redirect('pedigree:index')
    else:
        form = FamilyMemberForm(instance=member)

    return render(request, 'pedigree/edit_member.html', {
        'form': form,
        'member': member,
    })


def delete_member(request, member_id):
    member = get_object_or_404(FamilyMember, id=member_id)
    if request.method == 'POST':
        member.delete()
        return redirect('pedigree:index')
    return render(request, 'pedigree/confirm_delete.html', {'member': member})

def clear_data(request):
    FamilyMember.objects.all().delete()
    return redirect('pedigree:index')


# pedigree/views.py
import json
from django.http import JsonResponse
from django.shortcuts import render
from .models import FamilyMember


def pedigree_js_view(request):
    """View for pedigreejs interactive editor"""
    members = FamilyMember.objects.all()
    return render(request, 'pedigree/pedigree_js_last.html', {
        'members': members
    })


def get_pedigree_data(request):
    """API endpoint to get pedigree data in pedigreejs format"""
    members = FamilyMember.objects.all().prefetch_related('parents')
    print('***************')
    print(members)

    pedigree_data = []
    member_map = {}  # Map member IDs to their data

    # First pass: create basic member data
    for member in members:
        individual = {
            "name": str(member.id),
            "display_name": member.name,
            "sex": "M" if member.gender == 'M' else "F",
            "top_level": not member.parents.exists(),
            "proband": False,  # You can set this based on your logic
        }

        # Add cancer information based on affected status
        if member.affected == 'C' and member.cancer_type:
            cancer_type = member.cancer_type.lower()
            if 'breast' in cancer_type or 'پستان' in cancer_type:
                individual["breast_cancer"] = True
            elif 'ovarian' in cancer_type or 'تخمدان' in cancer_type:
                individual["ovarian_cancer"] = True
            elif 'pancreatic' in cancer_type or 'لوزالمعده' in cancer_type:
                individual["pancreatic_cancer"] = True
            elif 'prostate' in cancer_type or 'پروستات' in cancer_type:
                individual["prostate_cancer"] = True
            else:
                individual["other_cancer"] = True

        # Add labels for additional information
        labels = []
        if member.age:
            labels.append(f"سن: {member.age}")
        if member.status == 'D':
            labels.append("فوت شده")
        if member.affected == 'C' and member.cancer_type:
            labels.append(f"سرطان: {member.cancer_type}")
            if member.age_diagnosis:
                labels.append(f"تشخیص: {member.age_diagnosis} سالگی")
        if member.genes:
            labels.append(f"ژن‌ها: {member.genes}")

        individual["labels"] = labels
        pedigree_data.append(individual)
        member_map[member.id] = individual

    # Second pass: add parent relationships
    for member in members:
        if member.parents.exists():
            parents = list(member.parents.all())
            individual = member_map[member.id]

            # Find mother and father
            mother = None
            father = None

            for parent in parents:
                if parent.gender == 'F':
                    mother = str(parent.id)
                elif parent.gender == 'M':
                    father = str(parent.id)

            if mother:
                individual["mother"] = mother
            if father:
                individual["father"] = father

    return JsonResponse(pedigree_data, safe=False)


def save_pedigree_data(request):
    """API endpoint to save pedigree data (if you want editing functionality)"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            # Process and save pedigree data
            # This would need custom logic based on your data structure
            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})

    return JsonResponse({'status': 'error', 'message': 'Invalid method'})