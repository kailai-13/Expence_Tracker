from django.db import models
from datetime import datetime
from dateutil.relativedelta import relativedelta

class account(models.Model):
    name = models.CharField(max_length=200)
    expense = models.FloatField(default=0)
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    expense_list = models.ManyToManyField('Expense', blank=True)

class Expense(models.Model):
    name = models.CharField(max_length=200)
    amount = models.FloatField(default=0)
    date = models.DateField(null=False, default=datetime.now().date())
    long_term = models.BooleanField(default=False)
    interest_rate = models.FloatField(default=0, null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    monthly_expense = models.FloatField(default=0, null=True, blank=True)
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        if self.long_term:
            self.monthly_expense = self.calculate_monthly_expense()
        super(Expense, self).save(*args, **kwargs)

    def calculate_monthly_expense(self):
        # Check if it's a long-term expense and calculate accordingly
        if self.long_term and self.end_date:
            # Calculate number of months between start date and end date
            months = (self.end_date.year - self.date.year) * 12 + (self.end_date.month - self.date.month)

            if months <= 0:
                return 0  # Ensure end date is valid

            if self.interest_rate == 0:
                # Simple division if no interest rate
                return self.amount / months
            else:
                # Calculate monthly expense with interest rate (using the formula for loan amortization)
                monthly_rate = self.interest_rate / 12 / 100
                return self.amount * (monthly_rate / (1 - (1 + monthly_rate) ** -months))
        else:
            return self.amount
