from django.urls import path, include
from . import views   

# map app.urls to views
urlpatterns = [
    path('', views.home, name= 'app-home'),
    path('users/', include('users.urls')),
]
