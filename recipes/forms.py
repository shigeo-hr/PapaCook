from django import forms


class RecipeConditionForm(forms.Form):
    for_kids = forms.BooleanField(required=False, label='子供向け')
    quick = forms.BooleanField(required=False, label='時短')
