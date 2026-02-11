from django import forms
from .models import Family, Individual
from django.contrib.auth.decorators import login_required

class FamilyForm(forms.ModelForm):
    class Meta:
        model = Family
        fields = ['name', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }


class IndividualForm(forms.ModelForm):
    class Meta:
        model = Individual
        fields = ['name', 'gender', 'date_of_birth', 'date_of_death', 'affected', 'mother', 'father', 'notes']
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
            'date_of_death': forms.DateInput(attrs={'type': 'date'}),
            'notes': forms.Textarea(attrs={'rows': 2}),
        }

    def __init__(self, family, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Limit parent choices to individuals in the same family
        self.fields['mother'].queryset = Individual.objects.filter(family=family)
        self.fields['father'].queryset = Individual.objects.filter(family=family)


# In forms.py
class BulkImportForm(forms.Form):
    data = forms.CharField(widget=forms.Textarea(attrs={'rows': 10}),
                           help_text="Enter one individual per line in format: Name,Gender(M/F/U),Birthdate(YYYY-MM-DD),Affected(Y/N),MotherName,FatherName")


# In views.py
@login_required
def bulk_import(request, family_id):
    family = get_object_or_404(Family, pk=family_id, created_by=request.user)

    if request.method == 'POST':
        form = BulkImportForm(request.POST)
        if form.is_valid():
            # Process each line
            for line in form.cleaned_data['data'].split('\n'):
                parts = [part.strip() for part in line.split(',')]
                if len(parts) >= 4:
                    # Create individual
                    individual = Individual(
                        family=family,
                        name=parts[0],
                        gender=parts[1].upper(),
                        date_of_birth=parts[2] if parts[2] else None,
                        affected=parts[3].upper() == 'Y',
                    )
                    individual.save()

                    # Add parents later (need their IDs)
                    # This would require more complex handling
            return redirect('family_detail', family_id=family.id)
    else:
        form = BulkImportForm()

    return render(request, 'pedigree/bulk_import.html', {
        'form': form,
        'family': family
    })