from .services import *
from .models import *
import requests
import xmltodict
from django.contrib import messages
from django.views import View
from django.urls import reverse_lazy


class MainView(View):
    template_name = 'main/main.html'

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        if request.method == 'POST':
            name = request.POST.get('name')
            password = request.POST.get('password')
            try:
                user = MyUser.objects.get(name=name, password=password)
                if user:
                    return redirect('kabinet', id=user.id)
            except:
                messages.warning(request, 'Нету такого полбзователя или неправильный пароль')
                return redirect('main')


# def main(request):
#     if request.method == 'POST':
#         name = request.POST.get('name')
#         password = request.POST.get('password')
#         try:
#             user = MyUser.objects.get(name=name, password=password)
#             if user:
#                 return redirect('kabinet', id=user.id)
#         except:
#             messages.warning(request, 'Нету такого полбзователя или неправильный пароль')
#             return redirect('main')
#+-
#     return render(request, 'main/main.html')


class RegistrationView(View):
    def get(self, request):
        form = Registration()
        return render(request, 'main/registration.html', {'form': form})

    def post(self, request):
        form = Registration(request.POST)
        if form.is_valid():
            form.save()
            return redirect('main')
        return render(request, 'main/registration.html', {'form': form})

# def registration(request):
#     if request.method == "POST":
#         form = Registration(request.POST)
#         if form.is_valid():
#             name = form.cleaned_data['name']
#             password = form.cleaned_data['password']
#             user = MyUser.objects.create(name=name, password= password)
#             return redirect('kabinet', id=user.id)
#     else:
#         form = Registration()
#
#     return render(request, 'main/registration.html', context={'form': form})


def kabinet(request, id):
    # user = get_object_or_404(User, id=id)
    # transactions = Transaction.objects.all()  # Возможно, стоит фильтровать транзакции по пользователю
    #
    # if request.method == 'POST':
    #     name = request.POST.get('name')
    #     money = request.POST.get('money')
    #
    #     # Проверяем, что money не пустое и может быть преобразовано в int
    #     if money and name:
    #         try:
    #             money = int(money)
    #
    #             # Получаем получателя и проверяем условия
    #             recipient = User.objects.get(name=name)
    #
    #             if user.wallet >= money >= 0:
    #                 transaction(user, money, recipient)
    #                 return redirect('kabinet', id=id)
    #             else:
    #                 error_message = "Недостаточно средств или некорректная сумма."
    #         except ValueError:
    #             error_message = "Некорректная сумма."
    #         except User.DoesNotExist:
    #             error_message = "Получатель не найден."
    #         except Exception as e:
    #             error_message = str(e)  # Логируем или обрабатываем другую ошибку
    #
    #         # Если возникла ошибка, возвращаемся с сообщением
    #         return render(request, 'main/kabinet.html',
    #                       {'user': user, 'transactions': transactions, 'error_message': error_message})
    #
    # return render(request, 'main/kabinet.html', {'user': user, 'transactions': transactions})

    user = get_object_or_404(MyUser, id=id)
    trs = Transaction.objects.all()
    if request.method == 'POST':
        print(00)
        name = request.POST.get('name')
        money = request.POST.get('money')
        if money:
            money = int(money)
            print(00)
            try:
                recipient = get_object_or_404(MyUser, name=name)
                if user.wallet >= money and money >= 0:
                    transaction(user, money, recipient)
                    return redirect('kabinet', id=id)
            except:
                messages.warning(request, 'Нету такого полбзователя или неправильный пароль')
                return redirect('kabinet', id=id)
        else:
            messages.warning(request, 'Введите сумму')

        return redirect('kabinet', id=id)
    return render(request, 'main/kabinet.html', context={'user': user, 'transactions': trs})


def history_range(request, id):
    user = get_object_or_404(MyUser, id=id)
    if request.method == 'POST':
        start = request.POST.get('start')
        end = request.POST.get('end')

        if start and end:
            transactions = Transaction.objects.filter(user__id=user.id, time__range=(start, end)).order_by('-time')
            return render(request, 'main/history_range.html', context={'transactions': transactions})

    transactions = Transaction.objects.filter(user__id=user.id).order_by('-time')
    return render(request, 'main/history_range.html', context={'transactions': transactions, 'user': user})


def show_all_users(request, id):
    current_user = get_object_or_404(MyUser, id=id)
    if request.method == 'POST':
        res_id = request.POST.get('res_id')
        recipient = get_object_or_404(MyUser, id=res_id)

        return render(request, 'main/payment.html', context={'recipient': recipient, 'current_user': current_user})

    users = MyUser.objects.filter(~Q(id=current_user.id))

    return render(request, 'main/show_all_users.html', context={'users': users, 'user': current_user})


def payment(request, id):
    if request.method == 'POST':
        money = request.POST.get('money')
        if money: money = int(money)

        kupon_n = request.POST.get('kupon_n')

        recipient_id = request.POST.get('recipient_id')
        recipient = get_object_or_404(MyUser, id=recipient_id)
        current_user = get_object_or_404(MyUser, id=id)
        transaction(current_user, money, recipient, kupon_n)
        return redirect('kabinet', id=id)


def enter_kupon(request, id):
    kupons = Kupon.objects.filter(active=True)
    user = MyUser.objects.get(id=id)

    if request.method == 'POST':
        kupon_n = request.POST.get('kupon')
        if kupon_n:
            kupon_n = int(kupon_n)
            if kupons and kupon_n:
                for kupon in kupons:
                    if kupon.number == kupon_n:
                        user.wallet += kupon.value
                        user.save()
                        kupon.active = False
                        kupon.save()
                        return redirect('kabinet', id=id)
            return redirect('kabinet', id=id)
        return redirect('kabinet', id=id)


def take_credit_page(request, id):
    user = get_object_or_404(MyUser, id=id)

    if request.method == 'POST':
        form = MathCreditForm(request.POST)
        if form.is_valid():
            value = form.cleaned_data['value']
            how_many_months = form.cleaned_data['how_many_months']
            payoff_dates, money_back_in_month, procent_stavka = math_payoff_dates(value, how_many_months)
            if 'confirm_credit' in request.POST:

                take_credit(user=user, value=value, payoff_date=payoff_dates,
                            how_many_months=how_many_months, money_back_month=money_back_in_month,
                            procent_stavka=procent_stavka)
                return redirect('kabinet', id)
            text = f'На сумму {value} вы должны платить {25}%, тоесть: {money_back_in_month} в течении {how_many_months} месяцев'
            return render(request, 'main/take_credit_page.html', context={'form': form, 'text': text, 'user': user})
    else:
        form = MathCreditForm()

    return render(request, 'main/take_credit_page.html', context={'form': form, 'user': user})


def payoff_page(request, id):
    user = get_object_or_404(MyUser, id=id)
    credits = Credit.objects.filter(user=user)
    for credit in credits:
        payoff_date = json.loads(credit.payoff_date)

        if not payoff_date:
            credit.delete()
        prosrochka(credit, payoff_date)

    if request.method == 'POST':
        credit_id = request.POST.get('credit_id')
        if 'for_month' in request.POST:
            p = payoff_month(user, credit_id)
            if p:
                messages.warning(request, 'Нехватка денег на счету для кредита!')
            else:
                return redirect('payoff_page', id)
        else:
            p = payoff(user, credit_id)
            if p:
                messages.warning(request, 'Нехватка денег на счету для кредита!')
            else:
                return redirect('kabinet', id)

    return render(request, 'main/payoff_page.html', context={'credits': credits, 'user': user})




def show_exchange_rates(request):
    r = requests.get('https://www.nbkr.kg/XML/daily.xml')
    data_dict = xmltodict.parse(r.content)

    rates = []
    for i in data_dict['CurrencyRates']['Currency']:
        rates.append(f'{i['Nominal']}{i['@ISOCode']} = {i['Value']}')

    conversion_result = []
    if request.method == 'POST':
        form = CurrencyConverterForm(request.POST)
        if form.is_valid():
            from_currency = form.cleaned_data['from_currency']
            amount = form.cleaned_data['amount']
            amount = float(amount)
            conversion_result = currency_converter(data_dict, from_currency, amount)
    else:
        form = CurrencyConverterForm()
    return render(request, 'main/show_exchange_rates.html', context={'rates': rates,
                                                                     'form': form, 'conversion_result': conversion_result})
















#
# from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
# from django.contrib.auth.forms import PasswordChangeForm
#
# from .forms import SignUpForm, EditProfileForm
# # Create your views here.
#
# def home(request):
# 	return render(request, 'authenticate/home.html', {})
#
# def login_user (request):
# 	if request.method == 'POST': #if someone fills out form , Post it
# 		username = request.POST['username']
# 		password = request.POST['password']
# 		user = authenticate(request, username=username, password=password)
# 		if user is not None:# if user exist
# 			login(request, user)
# 			messages.success(request,('Youre logged in'))
# 			return redirect('home') #routes to 'home' on successful login
# 		else:
# 			messages.success(request,('Error logging in'))
# 			return redirect('login') #re routes to login page upon unsucessful login
# 	else:
# 		return render(request, 'authenticate/login.html', {})
#
# def logout_user(request):
# 	logout(request)
# 	messages.success(request,('Youre now logged out'))
# 	return redirect('home')
#
# def register_user(request):
# 	if request.method =='POST':
# 		form = SignUpForm(request.POST)
# 		if form.is_valid():
# 			form.save()
# 			username = form.cleaned_data['username']
# 			password = form.cleaned_data['password1']
# 			user = authenticate(username=username, password=password)
# 			login(request,user)
# 			messages.success(request, ('Youre now registered'))
# 			return redirect('home')
# 	else:
# 		form = SignUpForm()
#
# 	context = {'form': form}
# 	return render(request, 'authenticate/register.html', context)
#
# def edit_profile(request):
# 	if request.method =='POST':
# 		form = EditProfileForm(request.POST, instance= request.user)
# 		if form.is_valid():
# 			form.save()
# 			messages.success(request, ('You have edited your profile'))
# 			return redirect('home')
# 	else: 		#passes in user information
# 		form = EditProfileForm(instance= request.user)
#
# 	context = {'form': form}
# 	return render(request, 'authenticate/edit_profile.html', context)
# 	#return render(request, 'authenticate/edit_profile.html',{})
#
#
#
# def change_password(request):
# 	if request.method =='POST':
# 		form = PasswordChangeForm(data=request.POST, user= request.user)
# 		if form.is_valid():
# 			form.save()
# 			update_session_auth_hash(request, form.user)
# 			messages.success(request, ('You have edited your password'))
# 			return redirect('home')
# 	else: 		#passes in user information
# 		form = PasswordChangeForm(user= request.user)
#
# 	context = {'form': form}
# 	return render(request, 'authenticate/change_password.html', context)




