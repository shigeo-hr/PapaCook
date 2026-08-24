from django import forms

from .models import Ingredient


class IngredientInputForm(forms.Form):
    common_ingredients = forms.ModelMultipleChoiceField(
        queryset=Ingredient.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label='よく使う食材',
    )
    other_ingredients = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3}),
        required=False,
        label='その他の食材(カンマ区切りで入力)',
    )

    def clean(self):
        cleaned_data = super().clean()
        if not cleaned_data.get('common_ingredients') and not cleaned_data.get('other_ingredients', '').strip():
            raise forms.ValidationError('食材を1つ以上入力または選択してください。')
        return cleaned_data

    def get_ingredient_names(self):
        names = [ingredient.name for ingredient in self.cleaned_data['common_ingredients']]
        other = self.cleaned_data.get('other_ingredients', '')
        names += [name.strip() for name in other.split(',') if name.strip()]
        return names
