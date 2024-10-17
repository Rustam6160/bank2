import json

from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    wallet = models.IntegerField(default=0)

    def __str__(self):
        return self.user.username


class Kupon(models.Model):
    name = models.CharField(max_length=255)
    number = models.IntegerField()
    active = models.BooleanField(default=True)
    value = models.IntegerField(default=0)

    def __str__(self):
        return str(self.number)


class Transaction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='transactions')
    amount = models.PositiveIntegerField()
    value = models.CharField(max_length=1)
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='recipient')
    time = models.DateTimeField(auto_now=True)
    kupon = models.ForeignKey(Kupon, on_delete=models.CASCADE, related_name='kupon', null=True, blank=True)

    def __str__(self):
        if self.kupon:
            kupon_info = f"использован купон на сумму: {self.kupon.value}"
        else:
            kupon_info = "без купона"

        if self.value == '+':
            return f"{self.value, self.amount} от {self.recipient} для {self.user} ({kupon_info}), время: {self.time}"
        else:
            return f"{self.value, self.amount} от {self.user} для {self.recipient} ({kupon_info}), время: {self.time}"


class Bank(models.Model):
    balance = models.IntegerField()


class Credit(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    value = models.PositiveIntegerField()
    current_value = models.PositiveIntegerField()
    credit_taken_date = models.DateTimeField(auto_now_add=True)
    how_many_months = models.PositiveIntegerField()
    payoff_date = models.TextField(default=dict)
    procent_stavka = models.IntegerField()
    current_procent_stavka = models.IntegerField()
    money_back_month = models.IntegerField(default=0)
    bank_balance = models.ForeignKey(Bank, on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        if not self.current_procent_stavka:
            self.current_procent_stavka = self.procent_stavka
        if self.payoff_date:
            payoff_dates = json.loads(self.payoff_date)
            self.current_value = 0
            for payoff_date in payoff_dates:
                self.current_value += self.money_back_month
        super().save(*args, **kwargs)

    def update_money_back_month(self, money_back_month):
        self.money_back_month = money_back_month
        self.save()


class CreditPayment(models.Model):
    credit = models.ForeignKey(Credit, on_delete=models.CASCADE)
    amount_paid = models.IntegerField()
    payment_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.credit.user.username} - {self.amount_paid}'


class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.message} - {self.created_at}"


class CreditCard(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    card_number = models.CharField(max_length=16, unique=True)
    expiration_date = models.DateField()
    cvv = models.CharField(max_length=3)
    card_type = models.CharField(max_length=20, choices=[('CREDIT', 'Credit'), ('DEBIT', 'Debit')])
    account = models.ForeignKey(Profile, on_delete=models.CASCADE)


    def _str_(self):
        return f"{self.user.username} - {self.card_number}"


class BillPayment(models.Model):
    account = models.ForeignKey(User, on_delete=models.CASCADE)
    service_name = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateTimeField(auto_now_add=True)

    def _str_(self):
        return f"{self.account.user_name} - {self.service_name} - {self.amount}"
