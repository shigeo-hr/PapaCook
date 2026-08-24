from django.db import models


class Ingredient(models.Model):
    name = models.CharField('食材名', max_length=100, unique=True)
    category = models.CharField('カテゴリ', max_length=50)
    created_at = models.DateTimeField('作成日時', auto_now_add=True)
    updated_at = models.DateTimeField('更新日時', auto_now=True)

    class Meta:
        ordering = ['category', 'name']

    def __str__(self):
        return self.name
