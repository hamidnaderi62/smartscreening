from django import forms


class AssessmentSelectionForm(forms.Form):
    selected_assessments = forms.MultipleChoiceField(required=False)

    def __init__(self, *args, allowed_assessments=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.allowed_assessments = {
            str(assessment['id']): assessment
            for assessment in (allowed_assessments or ())
        }
        self.fields['selected_assessments'].choices = [
            (assessment_id, assessment['title_en'])
            for assessment_id, assessment in self.allowed_assessments.items()
        ]

    def clean_selected_assessments(self):
        selected = self.cleaned_data['selected_assessments']
        for value in selected:
            if value not in self.allowed_assessments:
                raise forms.ValidationError('Invalid assessment selection.')
        return [self.allowed_assessments[value] for value in selected]
