from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .forms import RegisterForm, LoginForm


def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Регистрация прошла успешно!')
            return redirect('dashboard')
    else:
        form = RegisterForm()
    return render(request, 'accounts/register.html', { 'form': form })


def login_view(request):
    # Using Django's auth views via URL, but keep form rendering compatibility
    form = LoginForm(request, data=request.POST or None)
    return render(request, 'accounts/login.html', { 'form': form })


@login_required
def dashboard_view(request):
    # Landing page is news
    return render(request, 'pages/news.html')


@login_required
def profile_view(request):
    return render(request, 'pages/profile.html')


@login_required
def converter_view(request):
    currency_rates = {
        'USD': 1.00,
        'EUR': 0.93,
        'RUB': 96.50,
        'GBP': 0.80,
        'CNY': 7.10,
        'JPY': 148.0,
        'KZT': 488.0,
    }
    metal_prices_usd = {
        'XAU': 1930.00,  # Gold per troy ounce in USD (static)
        'XAG': 23.50,    # Silver per troy ounce in USD (static)
        'XPT': 910.00,   # Platinum
        'XPD': 1250.00,  # Palladium
    }
    context = {
        'rates': currency_rates,
        'metals': metal_prices_usd,
        'base_currency': 'USD',
    }
    return render(request, 'pages/converter.html', context)


@login_required
def about_view(request):
    return render(request, 'pages/about.html')

# Create your views here.
