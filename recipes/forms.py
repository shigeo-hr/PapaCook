from django import forms


class RecipeConditionForm(forms.Form):
    for_kids = forms.BooleanField(
        required=False, label='子供向け', widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
    )
    quick = forms.BooleanField(
        required=False, label='時短', widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
    )
