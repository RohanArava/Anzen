from pickle import NEXT_BUFFER
from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView
from .views import add_totp_view, current_totps_view, home_view, signup_view, totps_ui_view, unlock_view

urlpatterns = [
    path('', home_view, name='home'),
    path('signup/', signup_view, name='signup'),
    path('login/', LoginView.as_view(template_name='core/login.html', next_page='home'), name='login'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
    path('unlock/', unlock_view, name='unlock'),
    path('add_totp/', add_totp_view, name='add_totp'),
    path('totps/', current_totps_view, name='totps'),
    path('totps-ui/', totps_ui_view, name='totps-ui')
]
