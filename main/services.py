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
    recipient = MyUser.objects.get(name=recipient)
    print(22)
    if kupon_n:
        kupon = get_object_or_404(Kupon, number=kupon_n)
    else:
        kupon = False
    print(55)
    if amount >= 0 and amount:
        print(99)
        user.wallet -= amount
        user.save()
        if kupon:
            Transaction.objects.create(user=user, amount=amount, value='-', recipient=recipient, kupon=kupon)
        else:
            Transaction.objects.create(user=user, amount=amount, value='-', recipient=recipient)

        if kupon and kupon.active == True:
            recipient.wallet += amount + kupon.value
            kupon.active = False
            kupon.save()
        else:
            recipient.wallet += amount
        recipient.save()
        print(33)
        if kupon:
            Transaction.objects.create(user=recipient, amount=amount, value='+', recipient=user, kupon=kupon)
        else:
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

def math_payoff_dates(value, how_many_months):
    if how_many_months <= 36:
        procent_stavka = PERCENT_BEFORE_AND_EQUALS_3_YEARS
    elif 36 < how_many_months <= 60:
        procent_stavka = PERCENT_BETWEEN_3_AND_EQUALS_5_YEARS
    else:
        procent_stavka = PERCENT_AFTER_5_YEARS

    today = datetime.today()

    money_back_month = money_back_in_month(value, how_many_months, procent_stavka)

    payoff_dates = []
    for month in range(1, how_many_months + 1):
        payoff_date = today + relativedelta(months=month)
        payoff_dates.append(payoff_date.strftime("%Y-%m-%d"))

    payoff_dates_json = json.dumps(payoff_dates)
    return payoff_dates_json, money_back_month, procent_stavka

def take_credit(user, value, payoff_date, how_many_months, money_back_month, procent_stavka):
    bank = get_object_or_404(Bank, id=1)

    if bank.balance >= value:
        user.wallet += value
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
    money_should_pay_all = 0
    for payoff_date in payoff_dates:
        money_should_pay_all += credit.money_back_month


    if self.wallet >= money_should_pay_all:
        bank.balance +=money_should_pay_all
        bank.save()
        self.wallet -= money_should_pay_all
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
    if self.wallet >= money_back_month:
        bank.balance += money_back_month
        bank.save()
        self.wallet -= money_back_month
        self.save()

        if len(payoff_dates) > 0:
            del payoff_dates[0]

        payoff_dates_json = json.dumps(payoff_dates)
        credit.payoff_date = payoff_dates_json
        credit.save()
    else:
        return True

    payoff_date = json.loads(credit.payoff_date)
    if not payoff_date:
        credit.delete()

def prosrochka(credit, payoff_dates):
    today = date.today()
    date1 = date(2024, 11, 20)
    payoff_date_1 = datetime.strptime(payoff_dates[0], '%Y-%m-%d').date()
    if payoff_date_1 < date1:
        if credit.procent_stavka < credit.current_procent_stavka + 2:
            credit.procent_stavka += 2
            credit.save()
    else:
        credit.procent_stavka = credit.current_procent_stavka
        credit.save()
    money_back_month = money_back_in_month(credit.value, credit.how_many_months, credit.procent_stavka)
    credit.update_money_back_month(money_back_month)


def currency_converter(data_dict, from_currency, amount):
    for i in data_dict['CurrencyRates']['Currency']:
        if i['@ISOCode'] == from_currency:
            value = i['Value']
            if ',' in value:
                value = value.replace(',', '.')
            return amount * float(value)