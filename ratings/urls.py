"""
URL configuration for ratings.

"""
from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import RegisterView, LoginView, AuthToken, LogoutView, ListView, ViewView, AverageView, RateView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('token-auth/', AuthToken.as_view(), name='token-auth'),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'), 
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('list/', ListView.as_view(), name='list'),
    path('view/', ViewView.as_view(), name='view'),
    path('average/', AverageView.as_view(), name='average'),
    path('rate/', RateView.as_view(), name='rate')
]