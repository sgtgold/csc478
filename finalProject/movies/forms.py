from django import forms
from django.forms import ModelMultipleChoiceField
from movies.models import Movies

class UserForm(forms.Form):
    user_name = forms.CharField(label='Your name', max_length=100)