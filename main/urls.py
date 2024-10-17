from django.contrib import admin
from django.urls import path, include
from . import views
from django.urls import path
from .views import *


urlpatterns = [
    path('', HomeView.as_view(), name="home"),
    path('login/', LoginUserView.as_view(), name ='login'),
    path('logout/', LogoutUserView.as_view(), name='logout'),
    path('register/', RegisterUserView.as_view(), name='register'),
    path('edit_profile/', EditProfileView.as_view(), name='edit_profile'),
    path('change_password/', ChangePasswordView.as_view(), name='change_password'),

    path('kabinet/', KabinetView.as_view(), name='kabinet'),
    path('history_range/', ShowHistoryRangeView.as_view(), name='history_range'),
    path('show_all_users/', ShowAllUsersView.as_view(), name='show_all_users'),
    path('enter_kupon/', EnterKuponView.as_view(), name='enter_kupon'),
    path('payment/', PaymentView.as_view(), name='payment'),
    path('take_credit_page/', TakeCreditPageView.as_view(), name='take_credit_page'),
    path('payoff_page/', PayoffPageView.as_view(), name='payoff_page'),
    path('payoff_history/<int:id>/', PayoffHistory.as_view(), name='payoff_history'),
    path('show_exchange_rates/', ShowExchangeRatesView.as_view(), name='show_exchange_rates'),
    path('take_card/', TakeCardView.as_view(), name='take_card'),
    path('phone_balance/', PhoneBalanceView.as_view(), name='phone_balance'),

]