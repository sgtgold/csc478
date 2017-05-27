from django import forms

class SelectMovieForm(forms.ModelForm):
    movies = forms.ModelChoiceField(queryset=Movies.objects.all())