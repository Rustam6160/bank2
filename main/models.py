from django.db import models


class MyUser(models.Model):
    name = models.CharField(max_length=255,)
    password = models.CharField(max_length=8, default='00000000')
    wallet = models.IntegerField(default=0)

    def __str__(self):
        return self.name


class Kupon(models.Model):
    name = models.CharField(max_length=255)
    number = models.IntegerField()
    active = models.BooleanField(default=True)
    value = models.IntegerField(default=0)

    def __str__(self):
        return str(self.number)


class Transaction(models.Model):
    user = models.ForeignKey(MyUser, on_delete=models.CASCADE, related_name='transactions')
    amount = models.PositiveIntegerField()
    value = models.CharField(max_length=1)
    recipient = models.ForeignKey(MyUser, on_delete=models.CASCADE, related_name='recipient')
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
    user = models.ForeignKey(MyUser, on_delete=models.CASCADE)
    value = models.PositiveIntegerField()
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
        super().save(*args, **kwargs)

    def update_money_back_month(self, money_back_month):
        self.money_back_month = money_back_month
        self.save()



