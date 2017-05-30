from django import forms

class UserForm(forms.Form):
    user_name = forms.CharField(label='Your name', max_length=100)