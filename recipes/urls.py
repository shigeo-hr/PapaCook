from django.urls import path

from . import views

app_name = 'recipes'

urlpatterns = [
    path('conditions/', views.RecipeConditionView.as_view(), name='conditions'),
    path('<int:pk>/', views.RecipeDetailView.as_view(), name='detail'),
    path('', views.RecipeListView.as_view(), name='list'),
]
