from django.conf import settings
from django.db import models

from ingredients.models import Ingredient


class Condition(models.Model):
    name = models.CharField('条件名', max_length=50, unique=True)
    created_at = models.DateTimeField('作成日時', auto_now_add=True)
    updated_at = models.DateTimeField('更新日時', auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Recipe(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='recipes', verbose_name='ユーザー',
    )
    title = models.CharField('タイトル', max_length=100)
    instructions = models.TextField('作り方')
    is_favorite = models.BooleanField('お気に入り', default=False)
    ingredients = models.ManyToManyField(
        Ingredient, through='RecipeIngredient', related_name='recipes', verbose_name='材料',
    )
    conditions = models.ManyToManyField(
        Condition, through='RecipeCondition', related_name='recipes', verbose_name='条件',
    )
    created_at = models.DateTimeField('作成日時', auto_now_add=True)
    updated_at = models.DateTimeField('更新日時', auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    created_at = models.DateTimeField('作成日時', auto_now_add=True)
    updated_at = models.DateTimeField('更新日時', auto_now=True)

    class Meta:
        unique_together = ('recipe', 'ingredient')


class RecipeCondition(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    condition = models.ForeignKey(Condition, on_delete=models.CASCADE)
    created_at = models.DateTimeField('作成日時', auto_now_add=True)
    updated_at = models.DateTimeField('更新日時', auto_now=True)

    class Meta:
        unique_together = ('recipe', 'condition')
