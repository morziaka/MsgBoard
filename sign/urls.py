from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path, include
from .views import *

urlpatterns = [
    path('signup/', register, name='signup'),
    path('login/', LoginView.as_view(template_name = 'sign/login.html'), name = 'login'),
    path('logout/', LogoutView.as_view(template_name = 'sign/logout.html'), name = 'logout'),
    path('confirm/logout', confirm_logout, name = 'confirm_logout'),
    path('profile/', user_profile, name = 'user_profile'),
    path('verify_code/<int:user_id>/', verify_code, name='verify_code'),

]