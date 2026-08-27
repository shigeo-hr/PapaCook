from django.contrib import admin

from .models import Condition, Recipe


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'is_favorite', 'created_at')
    list_filter = ('is_favorite',)
    search_fields = ('title',)


@admin.register(Condition)
class ConditionAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
