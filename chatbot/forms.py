from django import forms

from django.contrib.auth.forms import UserCreationForm
from .models import User, Upload, Holiday

class LoginForm(forms.Form):
    username = forms.CharField(
        widget= forms.TextInput(
            attrs={
                "class": "form-control"
            }
        )
    )
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control"
            }
        )
    )

class SignUpForm(UserCreationForm):
    username = forms.CharField(max_length=150)
    email = forms.EmailField(required=True)
    password1 = forms.CharField(widget=forms.PasswordInput)
    password2 = forms.CharField(widget=forms.PasswordInput)
    is_admin = forms.BooleanField(required=False)
    is_employee = forms.BooleanField(required=False)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'is_admin', 'is_employee']




class UploadForm(forms.Form):
    file_name = forms.FileField(label='Select a file')
    title = forms.CharField(max_length=100)
    description = forms.CharField(max_length=100)
    class Meta:
        model = Upload
        fields = ['file_name', 'title', 'description']


class HolidayForm(forms.ModelForm):
    class Meta:
        model = Holiday
        fields = ['name', 'date']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
        }