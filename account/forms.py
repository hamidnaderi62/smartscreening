from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.utils.translation import gettext_lazy as _


User = get_user_model()


class RegistrationForm(forms.Form):
    """Validate the common fields used by public and organization registration."""

    username = forms.CharField(max_length=150, strip=True, label=_('Username'))
    email = forms.EmailField(max_length=254, label=_('Email'))
    phone_number = forms.CharField(
        max_length=20,
        required=False,
        strip=True,
        label=_('Mobile number'),
        help_text=_('Optional; used for follow-up SMS notifications.'),
    )
    password1 = forms.CharField(min_length=8, widget=forms.PasswordInput, label=_('Password'))
    password2 = forms.CharField(min_length=8, widget=forms.PasswordInput, label=_('Confirm password'))

    def clean_username(self):
        username = self.cleaned_data['username']
        if User.objects.filter(username__iexact=username).exists():
            raise forms.ValidationError(_('This username is already registered.'))
        return username

    def clean_email(self):
        email = self.cleaned_data['email'].lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError(_('This email is already registered.'))
        return email

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            self.add_error('password2', _('The passwords do not match.'))
        if password1:
            validate_password(password1)
        return cleaned_data

    def save(self):
        user = User.objects.create_user(
            username=self.cleaned_data['username'],
            email=self.cleaned_data['email'],
            password=self.cleaned_data['password1'],
        )
        return user
