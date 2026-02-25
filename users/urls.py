from django.urls import path
from django.contrib.auth.views import LogoutView
from . import views
from .views import CustomLoginView

urlpatterns = [

    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
    path('register/', views.register, name='register'),
]