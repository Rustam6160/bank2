from django.contrib import admin
from django.urls import path, include
from . import views
from django.urls import path
from .views import *


urlpatterns = [
    # path('', views.home, name ="home"),
    path('', MainView.as_view(), name='main'),
    path('registration/', RegistrationView.as_view(), name='registration'),
    path('kabinet/<int:id>/', views.kabinet, name='kabinet'),
    path('history_range/<int:id>/', views.history_range, name='history_range'),
    path('show_all_users/<int:id>/', views.show_all_users, name='show_all_users'),
    path('enter_kupon/<int:id>/', views.enter_kupon, name='enter_kupon'),
    path('payment/<int:id>/', views.payment, name='payment'),
    path('take_credit_page/<int:id>/', views.take_credit_page, name='take_credit_page'),
    path('payoff_page/<int:id>/', views.payoff_page, name='payoff_page'),
    path('show_exchange_rates/', views.show_exchange_rates, name='show_exchange_rates'),

    # path('login/', views.login_user, name ='login'),
    # path('logout/', views.logout_user, name='logout'),
    # path('register/', views.register_user, name='register'),
    # path('edit_profile/', views.edit_profile, name='edit_profile'),
    # path('change_password/', views.change_password, name='change_password'),
]