from django import forms
from .models import *
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth.models import User
from django import forms
from django.core.exceptions import ValidationError

#
# class Registration(forms.ModelForm):
#     password = forms.CharField(widget=forms.PasswordInput, help_text="Введите пароль (не менее 8 символов)", min_length=8)
#
#     class Meta:
#         model = MyUser
#         fields = ['name', 'password']



class MathCreditForm(forms.ModelForm):
    class Meta:
        model = Credit
        fields = ['value', 'how_many_months']
        widgets = {
            'value': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Введите сумму кредита',
                'min': '0',
                'step': '0.01',
            }),
            'how_many_months': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Введите количество месяцев',
                'min': '1',
            }),
        }

    def clean_value(self):
        value = self.cleaned_data.get('value')
        if value <= 0:
            raise forms.ValidationError("Сумма кредита должна быть больше нуля.")
        return value

    def clean_how_many_months(self):
        months = self.cleaned_data.get('how_many_months')
        if months < 1:
            raise forms.ValidationError("Количество месяцев должно быть хотя бы 1.")
        return months


class PhoneBalanceForm(forms.ModelForm):
    phone_number = forms.IntegerField()

    class Meta:
        model = BillPayment
        fields = ['amount']


class CurrencyConverterForm(forms.Form):
    from_currency = forms.CharField(label='Валюта', max_length=10)
    amount = forms.DecimalField(label='Сумма', min_value=0)


class EditProfileForm(UserChangeForm):
    password = forms.CharField(label="", widget=forms.TextInput(attrs={'type': 'hidden'}))

    class Meta:
        model = User
        # excludes private information from User
        fields = ('username', 'first_name', 'last_name', 'email', 'password',)


class SignUpForm(UserCreationForm):
    email = forms.EmailField(label="",
                             widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Email Address'}), )
    first_name = forms.CharField(label="", max_length=100,
                                 widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'}))
    last_name = forms.CharField(label="", max_length=100,
                                widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'}))

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2',)

    def __init__(self, *args, **kwargs):
        super(SignUpForm, self).__init__(*args, **kwargs)

        self.fields['username'].widget.attrs['class'] = 'form-control'
        self.fields['username'].widget.attrs['placeholder'] = 'User Name'
        self.fields['username'].label = ''
        self.fields[
            'username'].help_text = '<span class="form-text text-muted"><small>Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.</small></span>'

        self.fields['password1'].widget.attrs['class'] = 'form-control'
        self.fields['password1'].widget.attrs['placeholder'] = 'Password'
        self.fields['password1'].label = ''
        self.fields[
            'password1'].help_text = '<ul class="form-text text-muted small"><li>Your password can\'t be too similar to your other personal information.</li><li>Your password must contain at least 8 characters.</li><li>Your password can\'t be a commonly used password.</li><li>Your password can\'t be entirely numeric.</li></ul>'

        self.fields['password2'].widget.attrs['class'] = 'form-control'
        self.fields['password2'].widget.attrs['placeholder'] = 'Confirm Password'
        self.fields['password2'].label = ''
        self.fields[
            'password2'].help_text = '<span class="form-text text-muted"><small>Enter the same password as before, for verification.</small></span>'

        def save(self, commit=True):
            user = super().save(commit=False)
            if commit:
                user.save()
                Profile.objects.create(user=user)
                return user