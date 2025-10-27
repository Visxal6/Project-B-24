from django.urls import path
from . import views   

# map app.urls to views
urlpatterns = [
    path('', views.home, name= 'app-home'),

]
