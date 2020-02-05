from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import CustomUser


class UserSignupForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'computing_id', 'email', 'phone_number', 'bio', 'username', 'password1',
                  'password2']
        widgets = {
            'bio': forms.Textarea(attrs={'cols': 10, 'rows': 4}),
        }

    phone_number = forms.CharField(required=False, widget=forms.TextInput(attrs={}))
    bio = forms.CharField(required=False, widget=forms.Textarea(attrs={'cols': 10, 'rows': 4}))
