from django.urls import path

from . import views

app_name = 'children'

urlpatterns = [
    path('', views.ChildListView.as_view(), name='list'),
    path('new/', views.ChildCreateView.as_view(), name='create'),
    path('<int:pk>/edit/', views.ChildUpdateView.as_view(), name='update'),
    path('<int:pk>/delete/', views.ChildDeleteView.as_view(), name='delete'),
]
