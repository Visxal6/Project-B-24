from django.urls import path
from . import views   #import view functionalities 

# map app.urls to views
urlpatterns = [
    path('', views.home, name= 'app-home'),
]
