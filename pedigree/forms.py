# pedigree/forms.py
from django import forms
from .models import FamilyMember


class FamilyMemberForm(forms.ModelForm):
    parents = forms.ModelMultipleChoiceField(
        queryset=FamilyMember.objects.none(),
        required=False,
        widget=forms.CheckboxSelectMultiple,
        label="والدین"
    )

    class Meta:
        model = FamilyMember
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'instance' in kwargs:
            self.fields['parents'].queryset = FamilyMember.objects.exclude(id=kwargs['instance'].id)
        else:
            self.fields['parents'].queryset = FamilyMember.objects.all()