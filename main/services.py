from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from .constant import *
from .models import *
from .forms import *
from django.contrib import messages
from datetime import datetime, timedelta, date
from dateutil.relativedelta import relativedelta
import json
from .views import *
import calendar


def transaction(user, amount, recipient, kupon_n=False):
    if kupon_n:
        kupon = get_object_or_404(Kupon, number=kupon_n)
    else:
        kupon = False
    if amount:
        user.profile.wallet -= amount
        user.profile.save()
        if kupon and kupon.active == True:
            recipient.profile.wallet += amount + kupon.value
            recipient.profile.save()
            kupon.active = False
            kupon.save()
            Transaction.objects.create(user=user, amount=amount, value='-', recipient=recipient, kupon=kupon)
            Transaction.objects.create(user=recipient, amount=amount, value='+', recipient=user, kupon=kupon)
        else:
            recipient.profile.wallet += amount
            recipient.profile.save()
            Transaction.objects.create(user=user, amount=amount, value='-', recipient=recipient)
            Transaction.objects.create(user=recipient, amount=amount, value='+', recipient=user)


def get_months_and_days():
    months_and_days = {}
    year = 2023
    # Итерация по всем месяцам
    for month in range(1, 13):
        # Получение количества дней в месяце
        days_in_month = calendar.monthrange(year, month)[1]
        # Создание списка всех дней в месяце
        days = len(list(range(1, days_in_month + 1)))
        # Добавление месяца и его дней в словарь
        months_and_days[calendar.month_name[month]] = days

    return months_and_days


def money_back_in_month(value, how_many_months, procent_stavka):
    money_back_in_month = round(value / how_many_months + (value / 100 * procent_stavka))
    return money_back_in_month


def payoff_dates(how_many_months):
    today = datetime.today()
    payoff_dates = []
    for month in range(1, how_many_months + 1):
        payoff_date = today + relativedelta(months=month)
        payoff_dates.append(payoff_date.strftime("%Y-%m-%d"))
    return payoff_dates


def math_payoff_dates(value, how_many_months):
    if how_many_months <= 36:
        procent_stavka = PERCENT_BEFORE_AND_EQUALS_3_YEARS
    elif 36 < how_many_months <= 60:
        procent_stavka = PERCENT_BETWEEN_3_AND_EQUALS_5_YEARS
    else:
        procent_stavka = PERCENT_AFTER_5_YEARS

    money_back_month = money_back_in_month(value, how_many_months, procent_stavka)

    payoff_datess = payoff_dates(how_many_months)

    payoff_dates_json = json.dumps(payoff_datess)
    return payoff_dates_json, money_back_month, procent_stavka

def take_credit(user, value, payoff_date, how_many_months, money_back_month, procent_stavka):
    bank = get_object_or_404(Bank, id=1)

    if bank.balance >= value:
        user.profile.wallet += value
        user.save()
        bank.balance -= value
        bank.save()
        Credit.objects.create(user= user, value=value, how_many_months=how_many_months,
                              payoff_date=payoff_date, bank_balance=bank,
                              money_back_month=money_back_month, procent_stavka=procent_stavka)



def payoff(self, credit_id):
    credit = get_object_or_404(Credit, id=credit_id)
    bank = get_object_or_404(Bank, id=1)

    payoff_dates = json.loads(credit.payoff_date)
    money_should_pay_all = credit.current_value

    if self.profile.wallet >= money_should_pay_all:
        bank.balance +=money_should_pay_all
        bank.save()
        self.profile.wallet -= money_should_pay_all
        self.save()
        if len(payoff_dates) > 0:
            payoff_dates.clear()
        payoff_dates_json = json.dumps(payoff_dates)
        credit.payoff_date = payoff_dates_json
        credit.save()

    else:
        return True

    if not payoff_dates:
        credit.delete()


def payoff_month(self, credit_id):
    credit = get_object_or_404(Credit, id=credit_id)
    money_back_month = credit.money_back_month
    bank = get_object_or_404(Bank, id=1)
    payoff_dates = json.loads(credit.payoff_date)
    if self.profile.wallet >= money_back_month:
        bank.balance += money_back_month
        bank.save()
        self.profile.wallet -= money_back_month
        self.save()

        if len(payoff_dates) > 0:
            del payoff_dates[0]
            print(22)

        payoff_dates_json = json.dumps(payoff_dates)
        credit.payoff_date = payoff_dates_json
        credit.save()

        CreditPayment.objects.create(credit=credit, amount_paid=credit.money_back_month)
    else:
        return True

    payoff_date = json.loads(credit.payoff_date)
    if not payoff_date:
        credit.delete()

def prosrochka(credit, request):
    today = date.today()
    date1 = date(2024, 11, 20)

    payoff_dates = json.loads(credit.payoff_date)
    payoff_date_1 = datetime.strptime(payoff_dates[0], '%Y-%m-%d').date()
    if payoff_date_1 < date1:
        if credit.user.profile.wallet >= credit.money_back_month and credit.payoff_date:
            payoff_month(self=request.user, credit_id=credit.id)

            Notification.objects.create(user=request.user, message=f'У вас была списана({credit.money_back_month}) плата за этот месяц за кредит')
        else:

            if credit.procent_stavka < credit.current_procent_stavka + 2:
                credit.procent_stavka += 2
                credit.save()
                Notification.objects.create(user=request.user,
                                            message='За нехватка денег для выплаты кредита за этот месяц было добавлена 2% к плате')

            money_back_month = money_back_in_month(credit.value, credit.how_many_months, credit.procent_stavka)
            credit.update_money_back_month(money_back_month)
    else:

        credit.procent_stavka = credit.current_procent_stavka
        credit.save()




def currency_converter(rates, from_currency, to_currency, amount):
    from_value = None
    to_value = None

    # Проход по всем курсам валют для получения значений
    for rate in rates:

        # Получаем курс для from_currency
        if from_currency == 'KGS':
            from_value = 1
        elif rate['ISOCode'] == from_currency:
            from_value = float(rate['Value'].replace(',', '.'))

        if rate['ISOCode'] == to_currency:
            to_value = float(rate['Value'].replace(',', '.'))

    if to_currency == 'KGS':
        converted_amount = amount * from_value
    else:
        amount_in_kgs = amount * from_value
        converted_amount = amount_in_kgs / to_value
    return round(converted_amount, 3)



