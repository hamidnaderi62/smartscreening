from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from persiantools.jdatetime import JalaliDate


User = get_user_model()

_PERSIAN_DIGITS = str.maketrans('۰۱۲۳۴۵۶۷۸۹', '0123456789')
_ARABIC_DIGITS = str.maketrans('٠١٢٣٤٥٦٧٨٩', '0123456789')


class LocalizedBirthYearField(forms.IntegerField):
    """Validate a birth year in the calendar used by the registration page."""

    def __init__(self, *args, calendar_language='fa', **kwargs):
        self.calendar_language = calendar_language
        current_year = (
            JalaliDate.today().year
            if calendar_language == 'fa'
            else timezone.localdate().year
        )
        kwargs.setdefault('min_value', current_year - 115)
        kwargs.setdefault('max_value', current_year)
        super().__init__(*args, **kwargs)

    def to_python(self, value):
        if value:
            value = str(value).translate(_PERSIAN_DIGITS).translate(_ARABIC_DIGITS).strip()
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
        self.fields['birth_year'] = LocalizedBirthYearField(
            required=True,
            calendar_language=calendar_language,
            widget=forms.TextInput(attrs={
                'inputmode': 'numeric',
                'autocomplete': 'bday-year',
                'placeholder': 'YYYY',
                'dir': 'ltr',
                'maxlength': '4',
            }),
            label=_('Birth year'),
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
        return cleaned_data

    def save(self):
        user = User.objects.create_user(
            username=self.cleaned_data['username'],
            email=self.cleaned_data['email'],
            password=self.cleaned_data['password1'],
        )
        return user
