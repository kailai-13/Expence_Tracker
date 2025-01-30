from typing import Any
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from exp_tracker.forms import ExpenseForm
from .models import account, Expense
from django.views.generic.edit import FormView
from django.contrib import messages
from dateutil.relativedelta import relativedelta
from django.utils.safestring import mark_safe
import plotly.express as px

# Home View
def home(request):
    return render(request, 'home/home.html')

# Sign-up View
def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'login/signup.html', {'form': form})

# Graph Generation Function
def generate_graph(data):
    fig = px.bar(data, x='month', y='expenses')
    fig.update_layout(
        xaxis=dict(rangeslider=dict(visible=True)),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font_color='rgba(0,0,0,1)',
    )
    fig.update_traces(marker_color='#000c41')
    graph_json = fig.to_json()
    return graph_json

# Login View
def login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            # Authenticate user
            user = authenticate(
                username=form.cleaned_data.get('username'),
                password=form.cleaned_data.get('password')
            )
            if user is not None:
                login(request, user)
                return redirect('home')
            messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Invalid login credentials.")
    else:
        form = AuthenticationForm()

    return render(request, 'login/login.html', {'form': form})


# Expense ListView
class ExpenseListView(FormView):
    template_name = 'expense/expense.html'
    form_class = ExpenseForm
    success_url = '/'

    def form_valid(self, form):
        # Get or create account for the user
        account_instance, _ = account.objects.get_or_create(user=self.request.user)

        # Create a new expense entry
        expense = Expense(
            name=form.cleaned_data['name'],
            account=account_instance,
            interest_rate=form.cleaned_data['interest_rate'],
            date=form.cleaned_data['date'],
            end_date=form.cleaned_data['end_date'],
            long_term=form.cleaned_data['long_term'],
            user=self.request.user
        )
        expense.save()

        # Add the expense to the user's account
        account_instance.expense_list.add(expense)
        
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        accounts = account.objects.filter(user=user)

        expense_data_graph = {}

        # Loop through all user accounts and expenses
        for account in accounts:
            expenses = account.expense_list.all()

            for expense in expenses:
                if expense.long_term and expense.monthly_expenses:
                    # For long-term expenses, spread over months
                    current_date = expense.date
                    while current_date <= expense.end_date:
                        year_month = current_date.strftime('%Y-%m')
                        if year_month not in expense_data_graph:
                            expense_data_graph[year_month] = []
                        expense_data_graph[year_month].append({
                            'name': expense.name,
                            'amount': expense.monthly_expenses,
                            'date': expense.date,
                            'end_date': expense.end_date,
                        })
                        current_date += relativedelta(months=1)
                else:
                    # For one-time expenses
                    year_month = expense.date.strftime('%Y-%m')
                    if year_month not in expense_data_graph:
                        expense_data_graph[year_month] = []
                    expense_data_graph[year_month].append({
                        'name': expense.name,
                        'amount': expense.amount,
                        'date': expense.date,
                    })

        # Aggregate expense data for the graph
        aggregated_data = [{'year_month': key, 'expenses': sum(item['amount'] for item in value)}
                           for key, value in expense_data_graph.items()]

        context['expense_data'] = expense_data_graph
        context['aggregated_data'] = aggregated_data

        # Prepare data for the chart
        graph_data = {
            'month': [item['year_month'] for item in aggregated_data],
            'expenses': [item['expenses'] for item in aggregated_data]
        }
        context['graph_data'] = mark_safe(generate_graph(graph_data))

        return context
