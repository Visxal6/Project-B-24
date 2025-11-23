"""
URL configuration for main project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path, include
from users import views as user_views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [

    path('', include('app.urls')),
    path('accounts/', include('allauth.urls')),
    path('social/', include('social.urls')),
    path('admin/', admin.site.urls),

    path('login/', auth_views.LoginView.as_view(template_name='users/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='users/logout.html'), name='logout'),

    path('register/', user_views.register, name='register'),
    path('profile/', user_views.profile, name='profile'),
    path('profile-view/', user_views.profile_view, name='profile-view'),
    path('dashboard/', user_views.dashboard, name='dashboard'),
    path('forum/', include('forum.urls', namespace='forum')),

    path('complete-profile/', user_views.complete_profile, name='complete_profile'),
    path('post-login/', user_views.post_login_redirect,
         name='post_login_redirect'),

    path("leaderboard/", include("leaderboard.urls")),

    # Test
    path("", include("app_test.urls")),
]

if settings.DEBUG:
    # Serve media files during development
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
