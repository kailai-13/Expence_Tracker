from django.urls import path,include
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('accounts/login/', views.login, name='login'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('accounts/signup/', views.signup, name='signup'),
]
