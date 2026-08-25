from django import forms

from .models import Child


class ChildForm(forms.ModelForm):
    class Meta:
        model = Child
        fields = ['name', 'age', 'likes', 'dislikes', 'allergies']
        widgets = {
            'likes': forms.Textarea(attrs={'rows': 3}),
            'dislikes': forms.Textarea(attrs={'rows': 3}),
            'allergies': forms.Textarea(attrs={'rows': 3}),
        }
