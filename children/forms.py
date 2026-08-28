from django import forms

from .models import Child


class ChildForm(forms.ModelForm):
    class Meta:
        model = Child
        fields = ['name', 'age', 'likes', 'dislikes', 'allergies']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'age': forms.NumberInput(attrs={'class': 'form-control'}),
            'likes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'dislikes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'allergies': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
