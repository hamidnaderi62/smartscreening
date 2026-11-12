from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from persiantools.jdatetime import JalaliDate


User = get_user_model()

_PERSIAN_DIGITS = str.maketrans('۰۱۲۳۴۵۶۷۸۹', '0123456789')


class LocalizedBirthDateField(forms.DateField):
    """Parse Jalali dates for Persian forms and Gregorian dates otherwise."""

    def __init__(self, *args, calendar_language='fa', **kwargs):
        self.calendar_language = calendar_language
        super().__init__(*args, **kwargs)

    def to_python(self, value):
        if self.calendar_language == 'fa' and value:
            normalized = str(value).translate(_PERSIAN_DIGITS).replace('-', '/')
            parts = normalized.split('/')
            if len(parts) != 3:
                raise ValidationError(_('Enter a valid Persian date as YYYY/MM/DD.'))
            try:
                value = JalaliDate(
                    int(parts[0]), int(parts[1]), int(parts[2]),
                ).to_gregorian()
            except (TypeError, ValueError, OverflowError):
                raise ValidationError(_('Enter a valid Persian date as YYYY/MM/DD.'))
        return super().to_python(value)


class RegistrationForm(forms.Form):
    """Validate the common fields used by public and organization registration."""

    username = forms.CharField(max_length=150, strip=True, label=_('Username'))
    email = forms.EmailField(max_length=254, label=_('Email'))
    phone_number = forms.CharField(
        max_length=20,
        required=True,
        strip=True,
        label=_('Mobile number'),
        help_text=_('Used as your screening code and for follow-up SMS notifications.'),
    )
    gender = forms.ChoiceField(
        required=False,
        choices=(('Male', _('Male')), ('Female', _('Female'))),
        initial='Male',
        label=_('Gender'),
    )
    password1 = forms.CharField(min_length=8, widget=forms.PasswordInput, label=_('Password'))
    password2 = forms.CharField(min_length=8, widget=forms.PasswordInput, label=_('Confirm password'))

    def __init__(self, *args, calendar_language='fa', **kwargs):
        super().__init__(*args, **kwargs)
        self.calendar_language = calendar_language
        date_widget = (
            forms.TextInput(attrs={
                'inputmode': 'numeric',
                'autocomplete': 'bday',
                'placeholder': 'YYYY/MM/DD',
                'dir': 'ltr',
            })
            if calendar_language == 'fa'
            else forms.DateInput(attrs={'type': 'date', 'autocomplete': 'bday'})
        )
        self.fields['birth_date'] = LocalizedBirthDateField(
            required=False,
            calendar_language=calendar_language,
            widget=date_widget,
            label=_('Date of birth'),
        )

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

    def clean_phone_number(self):
        phone_number = ''.join(self.cleaned_data['phone_number'].split()).replace('-', '')
        if not phone_number:
            raise forms.ValidationError(_('Mobile number is required.'))
        if phone_number.startswith('+'):
            digits = phone_number[1:]
        else:
            digits = phone_number
        if not digits.isdigit() or not 8 <= len(digits) <= 19:
            raise forms.ValidationError(_('Enter a valid mobile number.'))
        return phone_number

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            self.add_error('password2', _('The passwords do not match.'))
        if password1:
            validate_password(password1)
        birth_date = cleaned_data.get('birth_date')
        if birth_date and birth_date > timezone.localdate():
            self.add_error('birth_date', _('Date of birth cannot be in the future.'))
        return cleaned_data

    def save(self):
        user = User.objects.create_user(
            username=self.cleaned_data['username'],
            email=self.cleaned_data['email'],
            password=self.cleaned_data['password1'],
        )
        return user
