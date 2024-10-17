from .services import *
from .models import *
import requests
import xmltodict
from django.contrib import messages
from django.views import View
from django.views.generic import TemplateView, ListView
from django.urls import reverse_lazy

from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm

from .forms import SignUpForm, EditProfileForm

#
# class MainView(View):
#     template_name = 'main/main.html'
#
#     def get(self, request):
#         return render(request, self.template_name)
#
#     def post(self, request):
#         if request.method == 'POST':
#             name = request.POST.get('name')
#             password = request.POST.get('password')
#             try:
#                 user = MyUser.objects.get(name=name, password=password)
#                 if user:
#                     return redirect('kabinet', id=user.id)
#             except:
#                 messages.warning(request, 'Нету такого полбзователя или неправильный пароль')
#                 return redirect('main')
#
#
# # def main(request):
# #     if request.method == 'POST':
# #         name = request.POST.get('name')
# #         password = request.POST.get('password')
# #         try:
# #             user = MyUser.objects.get(name=name, password=password)
# #             if user:
# #                 return redirect('kabinet', id=user.id)
# #         except:
# #             messages.warning(request, 'Нету такого полбзователя или неправильный пароль')
# #             return redirect('main')
# #
# #     return render(request, 'main/main.html')
#
#
# class RegistrationView(View):
#     def get(self, request):
#         form = Registration()
#         return render(request, 'main/registration.html', {'form': form})
#
#     def post(self, request):
#         form = Registration(request.POST)
#
#         if form.is_valid():
#             users = MyUser.objects.all()
#             name = form.cleaned_data['name']
#             for user in users:
#                 if user.name == name:
#                     messages.warning(request, 'Уже сушествует такой пользователь с таким именем!')
#                     return redirect('registration')
#                 else:
#                     form.save()
#                     return redirect('main')
#         return render(request, 'main/registration.html', {'form': form})
#


class KabinetView(View):
    def get(self, request):
        user = request.user
        notifications = Notification.objects.filter(user_id=user.id).order_by('-created_at')[:10]
        return render(request, 'main/kabinet.html', context={'user': user, 'notifications': notifications})


class TakeCardView(View):
    def get(self, request):


        return redirect('home')


class ShowHistoryRangeView(View):
    def get(self, request):
        user = request.user
        transactions = Transaction.objects.filter(user=user).order_by('-time')
        return render(request, 'main/history_range.html', context={'transactions': transactions, 'user': user})

    def post(self, request):
        user = request.user
        start = request.POST.get('start')
        end = request.POST.get('end')

        if start and end:
            transactions = Transaction.objects.filter(user=user, time__range=(start, end)).order_by('-time')
            return render(request, 'main/history_range.html', context={'transactions': transactions, 'user': user})

        # Если не были переданы даты, отобразите все транзакции
        transactions = Transaction.objects.filter(user=user).order_by('-time')
        return render(request, 'main/history_range.html', context={'transactions': transactions, 'user': user})


class ShowAllUsersView(View):
    def get(self, request):
        current_user = request.user
        users = User.objects.filter(~Q(id=current_user.id))
        return render(request, 'main/show_all_users.html', context={'users': users, 'user': current_user})

    def post(self, request):
        current_user = request.user
        res_id = request.POST.get('res_id')
        recipient = get_object_or_404(User, id=res_id)

        return render(request, 'main/payment.html', context={'recipient': recipient, 'user': current_user})


class PaymentView(View):
    def post(self, request):
        current_user = request.user
        money = request.POST.get('money')

        if money:
            money = int(money)
        else:
            messages.warning(request, 'Введите сумму')
            return redirect('payment')

        if money > 0 and money <= current_user.profile.wallet:
            recipient_id = request.POST.get('recipient_id')
            if recipient_id:
                recipient = get_object_or_404(User, id=recipient_id)
            else:
                recipient_name = request.POST.get('recipient_name')
                recipient = get_object_or_404(User, username=recipient_name)

            kupon_n = request.POST.get('kupon_n')

            transaction(user=current_user, amount=money, recipient=recipient, kupon_n=kupon_n)
            return redirect('payment')
        else:
            messages.warning(request, 'Нехватка денег!')
            return redirect('payment')

    def get(self, request):

        return render(request, 'main/payment.html', context={'user_id': request.user.id})


class EnterKuponView(View):
    def get(self, request):
        kupons = Kupon.objects.filter(active=True)
        user = request.user
        return render(request, 'main/enter_kupon.html', context={'kupons': kupons, 'user': user})

    def post(self, request):
        user = request.user
        kupon_n = request.POST.get('kupon')

        if kupon_n:
            try:
                kupon_n = int(kupon_n)
                kupon = Kupon.objects.filter(active=True, number=kupon_n).first()

                if kupon:
                    user.wallet += kupon.value
                    user.save()
                    kupon.active = False
                    kupon.save()
                    return redirect('kabinet')
            except ValueError:
                pass  # Обработка некорректного ввода

        return redirect('kabinet')


class TakeCreditPageView(View):
    def get(self, request):
        user = request.user
        form = MathCreditForm()
        return render(request, 'main/take_credit_page.html', context={'form': form, 'user': user})

    def post(self, request):
        user = request.user
        form = MathCreditForm(request.POST)

        if form.is_valid():
            value = form.cleaned_data['value']
            how_many_months = form.cleaned_data['how_many_months']
            payoff_dates, money_back_in_month, procent_stavka = math_payoff_dates(value, how_many_months)

            if 'confirm_credit' in request.POST:
                take_credit(
                    user=user,
                    value=value,
                    payoff_date=payoff_dates,
                    how_many_months=how_many_months,
                    money_back_month=money_back_in_month,
                    procent_stavka=procent_stavka
                )
                return redirect('kabinet')

            text = f'На сумму {value} вы должны платить {25}%, тоесть: {money_back_in_month} в течении {how_many_months} месяцев'
            return render(request, 'main/take_credit_page.html', context={'form': form, 'text': text, 'user': user})

        return render(request, 'main/take_credit_page.html', context={'form': form, 'user': user})


class PayoffPageView(View):
    def get(self, request):
        user = request.user
        credits = Credit.objects.filter(user=user)

        for credit in credits:
            payoff_date = json.loads(credit.payoff_date)

            if not payoff_date:
                credit.delete()
            prosrochka(credit=credit, request=request)


        return render(request, 'main/payoff_page.html', context={'credits': credits, 'user': user})

    def post(self, request):
        user = request.user
        credit_id = request.POST.get('credit_id')

        if 'for_month' in request.POST:
            p = payoff_month(user, credit_id)
            if p:
                messages.warning(request, 'Нехватка денег на счету для кредита!')
            else:
                return redirect('payoff_page')

        else:
            p = payoff(user, credit_id)
            if p:
                messages.warning(request, 'Нехватка денег на счету для кредита!')
            else:
                return redirect('kabinet')

        credits = Credit.objects.filter(user=user)  # Обновляем список кредитов после POST-запроса
        return render(request, 'main/payoff_page.html', context={'credits': credits, 'user': user})


class PayoffHistory(View):
    def get(self, request, id):
        payoffs = CreditPayment.objects.filter(credit_id=id)

        return render(request, 'main/payoff_history.html', context={'payoffs': payoffs})


class PhoneBalanceView(View):
    def get(self, request):
        form = PhoneBalanceForm()
        return render(request, 'main/phone_balance.html', context={'form': form})

    # def post(self, request):



class ShowExchangeRatesView(View):
    def get(self, request):
        r = requests.get('https://www.nbkr.kg/XML/daily.xml')
        data_dict = xmltodict.parse(r.content)

        rates = [
            f"{i['Nominal']}{i['@ISOCode']} = {i['Value']}"
            for i in data_dict['CurrencyRates']['Currency']
        ]
        form = CurrencyConverterForm()
        return render(request, 'main/show_exchange_rates.html', context={'rates': rates, 'form': form, 'conversion_result': None})

    def post(self, request):
        r = requests.get('https://www.nbkr.kg/XML/daily.xml')
        data_dict = xmltodict.parse(r.content)

        rates = [
            f"{i['Nominal']}{i['@ISOCode']} = {i['Value']}"
            for i in data_dict['CurrencyRates']['Currency']
        ]

        form = CurrencyConverterForm(request.POST)
        conversion_result = None

        if form.is_valid():
            from_currency = form.cleaned_data['from_currency']
            amount = form.cleaned_data['amount']
            amount = float(amount)
            conversion_result = currency_converter(data_dict, from_currency, amount)

        return render(request, 'main/show_exchange_rates.html', context={'rates': rates, 'form': form, 'conversion_result': conversion_result})


class HomeView(TemplateView):
    template_name = 'authenticate/home.html'


class LoginUserView(View):
    def get(self, request):
        return render(request, 'authenticate/login.html', {})

    def post(self, request):
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, 'You\'re logged in')
            return redirect('home')
        else:
            messages.error(request, 'Error logging in')
            return redirect('login')


class LogoutUserView(View):
    def get(self, request):
        logout(request)
        messages.success(request, 'You\'re now logged out')
        return redirect('home')

class RegisterUserView(View):
    def get(self, request):
        form = SignUpForm()
        context = {'form': form}
        return render(request, 'authenticate/register.html', context)

    def post(self, request):
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data['username']
            password = form.cleaned_data['password1']
            user = authenticate(username=username, password=password)
            login(request, user)
            messages.success(request, 'You\'re now registered')
            return redirect('home')
        context = {'form': form}
        return render(request, 'authenticate/register.html', context)


class EditProfileView(View):
    def get(self, request):
        form = EditProfileForm(instance=request.user)
        context = {'form': form}
        return render(request, 'authenticate/edit_profile.html', context)

    def post(self, request):
        form = EditProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'You have edited your profile')
            return redirect('home')
        context = {'form': form}
        return render(request, 'authenticate/edit_profile.html', context)


class ChangePasswordView(View):
    def get(self, request):
        form = PasswordChangeForm(user=request.user)
        context = {'form': form}
        return render(request, 'authenticate/change_password.html', context)

    def post(self, request):
        form = PasswordChangeForm(data=request.POST, user=request.user)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # обновляем сессию, чтобы не разлогинить пользователя
            messages.success(request, 'You have edited your password')
            return redirect('home')
        context = {'form': form}
        return render(request, 'authenticate/change_password.html', context)




