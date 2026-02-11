from django.shortcuts import render, get_object_or_404
from .models import Family, Individual
from .utils.pedigree_graph import generate_pedigree_graph, create_interactive_pedigree
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Family, Individual
from .forms import FamilyForm, IndividualForm

from django.contrib import messages
from django.http import HttpResponseRedirect
from django.urls import reverse

### family

def family_list(request):
    families = Family.objects.filter(created_by=request.user)
    return render(request, 'pedigree/family_list.html', {'families': families})


@login_required
def family_detail(request, family_id):
    family = get_object_or_404(Family, pk=family_id, created_by=request.user)

    try:
        graph = generate_pedigree_graph(family_id)
        graph_svg = graph.pipe().decode('utf-8') if graph else None
    except Exception as e:
        graph_svg = None
        print(f"Error generating graph: {e}")

    # Generate visualization
    graph = generate_pedigree_graph(family_id)
    interactive_graph = create_interactive_pedigree(family_id)

    return render(request, 'pedigree/family_detail.html', {
        'family': family,
        'graph_svg': graph.pipe().decode('utf-8'),
        'interactive_graph': interactive_graph
    })

@login_required
def create_family(request):
    if request.method == 'POST':
        form = FamilyForm(request.POST)
        if form.is_valid():
            family = form.save(commit=False)
            family.created_by = request.user
            family.save()
            return redirect('pedigree:family_detail', family_id=family.id)  # Updated redirect
    else:
        form = FamilyForm()

    return render(request, 'pedigree/family_form.html', {
        'form': form,
        'title': 'Create New Family'
    })

@login_required
def edit_family(request, family_id):
    family = get_object_or_404(Family, pk=family_id, created_by=request.user)

    if request.method == 'POST':
        form = FamilyForm(request.POST, instance=family)
        if form.is_valid():
            form.save()
            messages.success(request, 'Family updated successfully!')
            return redirect('pedigree:family_detail', family_id=family.id)
    else:
        form = FamilyForm(instance=family)

    return render(request, 'pedigree/family_form.html', {
        'form': form,
        'edit_mode': True,
        'family': family
    })


@login_required
def delete_family(request, family_id):
    family = get_object_or_404(Family, pk=family_id, created_by=request.user)

    if request.method == 'POST':
        family.delete()
        messages.success(request, 'Family deleted successfully!')
        return redirect('pedigree:family_list')

    return render(request, 'pedigree/family_confirm_delete.html', {'family': family})

############################################
### individual
############################################
@login_required
def individual_detail(request, individual_id):
    individual = get_object_or_404(Individual, pk=individual_id, family__created_by=request.user)
    return render(request, 'pedigree/individual_detail.html', {'individual': individual})

@login_required
def add_individual(request, family_id):
    family = get_object_or_404(Family, pk=family_id, created_by=request.user)

    if request.method == 'POST':
        form = IndividualForm(family, request.POST)
        if form.is_valid():
            individual = form.save(commit=False)
            individual.family = family
            individual.save()
            return redirect('family_detail', family_id=family.id)
    else:
        form = IndividualForm(family)

    return render(request, 'pedigree/individual_form.html', {
        'form': form,
        'family': family
    })


@login_required
def edit_individual(request, individual_id):
    individual = get_object_or_404(Individual, pk=individual_id, family__created_by=request.user)
    family = individual.family

    if request.method == 'POST':
        form = IndividualForm(family, request.POST, instance=individual)
        if form.is_valid():
            form.save()
            return redirect('family_detail', family_id=family.id)
    else:
        form = IndividualForm(family, instance=individual)

    return render(request, 'pedigree/individual_form.html', {
        'form': form,
        'family': family,
        'edit_mode': True
    })

@login_required
def delete_individual(request, individual_id):
    individual = get_object_or_404(Individual, pk=individual_id, family__created_by=request.user)
    family_id = individual.family.id

    if request.method == 'POST':
        individual.delete()
        messages.success(request, 'Individual deleted successfully!')
        return redirect('pedigree:family_detail', family_id=family_id)

    return render(request, 'pedigree/individual_confirm_delete.html', {
        'individual': individual
    })


############################################
### import & export
############################################

@login_required
def bulk_import(request, family_id):
    family = get_object_or_404(Family, pk=family_id, created_by=request.user)

    if request.method == 'POST':
        form = BulkImportForm(request.POST)
        if form.is_valid():
            # Process import data
            try:
                process_import_data(form.cleaned_data['data'], family)
                messages.success(request, 'Import completed successfully!')
                return redirect('pedigree:family_detail', family_id=family.id)
            except Exception as e:
                messages.error(request, f'Error during import: {str(e)}')
    else:
        form = BulkImportForm()

    return render(request, 'pedigree/bulk_import.html', {
        'form': form,
        'family': family
    })


@login_required
def export_family(request, family_id):
    family = get_object_or_404(Family, pk=family_id, created_by=request.user)
    # Implement your export logic here
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{family.name}_pedigree.csv"'
    # Add your CSV writing logic
    return response


@login_required
def family_graph(request, family_id):
    family = get_object_or_404(Family, pk=family_id, created_by=request.user)
    graph = generate_pedigree_graph(family_id)
    return render(request, 'pedigree/family_graph.html', {
        'family': family,
        'graph': graph
    })


@login_required
def family_graph_svg(request, family_id):
    family = get_object_or_404(Family, pk=family_id, created_by=request.user)
    graph = generate_pedigree_graph(family_id)
    return HttpResponse(graph.pipe(format='svg'), content_type='image/svg+xml')


@login_required
def family_graph_pdf(request, family_id):
    family = get_object_or_404(Family, pk=family_id, created_by=request.user)
    graph = generate_pedigree_graph(family_id)
    response = HttpResponse(graph.pipe(format='pdf'), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{family.name}_pedigree.pdf"'
    return response



############################################
### family_analysis
############################################

from django.db.models import Count, Q
from collections import defaultdict


@login_required
def family_analysis(request, family_id):
    family = get_object_or_404(Family, pk=family_id, created_by=request.user)
    individuals = Individual.objects.filter(family=family)

    # Basic statistics
    total_individuals = individuals.count()
    males = individuals.filter(gender='M').count()
    females = individuals.filter(gender='F').count()
    affected_count = individuals.filter(affected=True).count()

    # Generation analysis
    generations = defaultdict(list)
    for ind in individuals:
        generation = calculate_generation(ind)
        generations[generation].append(ind)

    # Inheritance pattern analysis
    inheritance_patterns = analyze_inheritance_patterns(individuals)

    # Risk calculation
    risk_analysis = calculate_family_risk(individuals)

    context = {
        'family': family,
        'total_individuals': total_individuals,
        'males': males,
        'females': females,
        'affected_count': affected_count,
        'affected_percentage': (affected_count / total_individuals) * 100 if total_individuals else 0,
        'generations': dict(generations),
        'inheritance_patterns': inheritance_patterns,
        'risk_analysis': risk_analysis,
    }

    return render(request, 'pedigree/family_analysis.html', context)


# Helper functions
def calculate_generation(individual):
    """Calculate generation level based on ancestry"""
    generation = 0
    current = individual
    while current.mother or current.father:
        generation += 1
        # Prefer mother's side if available
        current = current.mother if current.mother else current.father
    return generation


def analyze_inheritance_patterns(individuals):
    """Analyze potential inheritance patterns"""
    analysis = {
        'autosomal_dominant': False,
        'autosomal_recessive': False,
        'x_linked': False,
    }

    affected = individuals.filter(affected=True)

    # Check for autosomal dominant pattern
    parent_child_affected = False
    for ind in affected:
        if ind.mother and ind.mother.affected or ind.father and ind.father.affected:
            parent_child_affected = True
            break
    analysis['autosomal_dominant'] = parent_child_affected

    # Check for X-linked pattern
    x_linked = affected.filter(gender='M').count() > affected.filter(gender='F').count()
    analysis['x_linked'] = x_linked

    # Check for autosomal recessive (unaffected parents with affected children)
    if not parent_child_affected and affected.count() > 0:
        analysis['autosomal_recessive'] = True

    return analysis


def calculate_family_risk(individuals):
    """Calculate risk for unaffected individuals"""
    risks = {}
    unaffected = individuals.filter(affected=False)

    for person in unaffected:
        risk = 0.0
        # Simple risk calculation - can be enhanced
        if person.mother and person.mother.affected:
            risk += 0.5
        if person.father and person.father.affected:
            risk += 0.5
        risks[person.id] = min(risk, 1.0)  # Cap at 100%

    return risks



############################################
### inheritance_pattern_analysis
############################################

@login_required
def inheritance_pattern_analysis(request, family_id):
    family = get_object_or_404(Family, pk=family_id, created_by=request.user)
    individuals = Individual.objects.filter(family=family)

    # Detailed inheritance analysis
    analysis = {
        'autosomal_dominant': {
            'likely': False,
            'evidence': [],
            'confidence': 0
        },
        'autosomal_recessive': {
            'likely': False,
            'evidence': [],
            'confidence': 0
        },
        'x_linked': {
            'likely': False,
            'evidence': [],
            'confidence': 0
        },
        'mitochondrial': {
            'likely': False,
            'evidence': [],
            'confidence': 0
        }
    }

    affected = individuals.filter(affected=True)
    unaffected = individuals.filter(affected=False)

    # Autosomal Dominant Analysis
    vertical_transmission = False
    for ind in affected:
        if (ind.mother and ind.mother.affected) or (ind.father and ind.father.affected):
            vertical_transmission = True
            analysis['autosomal_dominant']['evidence'].append(
                f"Affected child {ind.name} has affected parent"
            )

    if vertical_transmission:
        analysis['autosomal_dominant']['likely'] = True
        analysis['autosomal_dominant']['confidence'] = min(90, len(analysis['autosomal_dominant']['evidence']) * 15)

    # Autosomal Recessive Analysis
    consanguinity = False  # Could be enhanced with actual family data
    multiple_affected_siblings = affected.filter(
        mother__in=affected.values_list('mother', flat=True)
    ).exists()

    if multiple_affected_siblings and not vertical_transmission:
        analysis['autosomal_recessive']['likely'] = True
        analysis['autosomal_recessive']['evidence'].append(
            "Multiple affected siblings with unaffected parents"
        )
        analysis['autosomal_recessive']['confidence'] = 70

    # X-Linked Analysis
    male_affected = affected.filter(gender='M').count()
    female_affected = affected.filter(gender='F').count()

    if male_affected > female_affected * 2:  # Significant male predominance
        analysis['x_linked']['likely'] = True
        analysis['x_linked']['evidence'].append(
            f"Male predominance ({male_affected} males vs {female_affected} females affected)"
        )
        analysis['x_linked']['confidence'] = min(80, male_affected * 15)

        # Check for no male-to-male transmission
        affected_males = affected.filter(gender='M')
        for male in affected_males:
            if male.father and male.father.affected:
                analysis['x_linked']['evidence'].append(
                    f"Male-to-male transmission present ({male.father.name} to {male.name})"
                )
                analysis['x_linked']['confidence'] *= 0.7  # Reduce confidence

    # Mitochondrial Analysis (all children of affected mothers affected)
    affected_mothers = affected.filter(gender='F')
    for mother in affected_mothers:
        children = individuals.filter(mother=mother)
        if children.exists() and all(child.affected for child in children):
            analysis['mitochondrial']['likely'] = True
            analysis['mitochondrial']['evidence'].append(
                f"All children of affected mother {mother.name} are affected"
            )
            analysis['mitochondrial']['confidence'] = max(
                analysis['mitochondrial']['confidence'],
                80
            )

    context = {
        'family': family,
        'analysis': analysis,
        'affected_count': affected.count(),
        'total_individuals': individuals.count(),
    }

    return render(request, 'pedigree/inheritance_patterns.html', context)

############################################
### dashboard
############################################

from django.db.models import Count, Q
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404


@login_required
def dashboard(request):
    # Initialize all variables at the start
    families = Family.objects.none()
    recent_families = []
    recent_individuals = []
    analysis_summary = {
        'total_families': 0,
        'total_individuals': 0,
        'total_affected': 0,
        'families_with_patterns': {
            'autosomal_dominant': 0,
            'autosomal_recessive': 0,
            'x_linked': 0
        }
    }

    try:
        # Get user's families with basic stats
        families = Family.objects.filter(created_by=request.user).annotate(
            total_individuals=Count('individuals'),
            affected_count=Count('individuals', filter=Q(individuals__affected=True))
        )

        # Recent activity
        recent_families = families.order_by('-created_at')[:5]
        recent_individuals = Individual.objects.filter(
            family__in=families
        ).order_by('-id')[:5]

        # Update analysis summary
        if families.exists():
            analysis_summary = {
                'total_families': families.count(),
                'total_individuals': sum(family.total_individuals for family in families),
                'total_affected': sum(family.affected_count for family in families),
                'families_with_patterns': {
                    'autosomal_dominant': 0,
                    'autosomal_recessive': 0,
                    'x_linked': 0
                }
            }

            # Pattern detection
            for family in families:
                individuals = family.individuals.all()  # Now properly defined
                affected = individuals.filter(affected=True)

                # Check for autosomal dominant
                if affected.exists() and any(
                        (ind.mother and ind.mother.affected) or
                        (ind.father and ind.father.affected)
                        for ind in affected
                ):
                    analysis_summary['families_with_patterns']['autosomal_dominant'] += 1

                # Check for possible x-linked
                male_affected = affected.filter(gender='M').count()
                female_affected = affected.filter(gender='F').count()
                if male_affected > female_affected * 1.5:
                    analysis_summary['families_with_patterns']['x_linked'] += 1

                # Check for autosomal recessive (simplified)
                if affected.count() >= 2 and not analysis_summary['families_with_patterns']['autosomal_dominant']:
                    analysis_summary['families_with_patterns']['autosomal_recessive'] += 1

    except Exception as e:
        # Log error but don't crash the dashboard
        print(f"Error in dashboard view: {str(e)}")

    context = {
        'recent_families': recent_families,
        'recent_individuals': recent_individuals,
        'analysis_summary': analysis_summary,
    }

    return render(request, 'pedigree/dashboard.html', context)