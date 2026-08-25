from django.contrib import admin

from .models import Child


@admin.register(Child)
class ChildAdmin(admin.ModelAdmin):
    list_display = ('name', 'age', 'user')
    list_filter = ('age',)
    search_fields = ('name',)
