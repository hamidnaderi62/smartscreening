from django import forms

from .models import DoctorReferral


class DoctorReferralForm(forms.ModelForm):
    class Meta:
        model = DoctorReferral
        fields = ('patient_message',)
        widgets = {
            'patient_message': forms.Textarea(attrs={'rows': 3}),
        }

class DoctorCommentForm(forms.ModelForm):
    class Meta:
        model = DoctorReferral
        fields = ('doctor_comment',)
        widgets = {
            'doctor_comment': forms.Textarea(attrs={'rows': 6}),
        }
