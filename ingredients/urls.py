from django.urls import path

from . import views

app_name = 'ingredients'

urlpatterns = [
    path('', views.IngredientInputView.as_view(), name='input'),
]
