"""
URL configuration for profrates project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
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
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django.urls import path, include
from ratings.views import RegisterView, AuthToken, LogoutView, ListView, ViewView, AverageView, RateView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('ratings.urls')),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token-auth/', AuthToken.as_view(), name='token-auth'),
    path('register/', RegisterView.as_view(), name='register'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('list/', ListView.as_view(), name='list'),
    path('view/', ViewView.as_view(), name='view'),
    path('average/', AverageView.as_view(), name='average'),
    path('rate/', RateView.as_view(), name='rate')
]