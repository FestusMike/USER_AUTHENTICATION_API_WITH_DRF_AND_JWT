from django.urls import path
from . import views
from . import views



urlpatterns = [
    path('', views.getRoutes),
    path('projects/', views.getProjects),
    path('projects/<uuid:pk>/', views.getProjectById),
    path('projects/add/', views.createProject),
    path('projects/edit/<uuid:pk>/', views.editProject),
    path('projects/delete/<uuid:pk>/', views.deleteProject),
    
    path('users/', views.getUsers),
    path('users/<uuid:pk>/', views.getUserById),
    
    path('register/', views.register),
    path('login/', views.login),
    path('logout/', views.logout_user),
]