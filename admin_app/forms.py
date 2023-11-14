from django import forms
from cities_light.models import Country, City

class CountryCityForm(forms.Form):
    country = forms.ModelChoiceField(queryset=Country.objects.filter(name='India'), empty_label="Select a country", widget=forms.Select(attrs={'class': 'custom-select'}))
    
    city = forms.ModelChoiceField(queryset=City.objects.filter(country__name='India'), empty_label="Select a city", widget=forms.Select(attrs={'class': 'custom-select'}))

class CityFilterForm(forms.Form):
    city = forms.ModelChoiceField(queryset=City.objects.filter(country__name='India'), empty_label="All Cities")