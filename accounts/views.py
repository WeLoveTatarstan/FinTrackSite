from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.db.models import Q

from .forms import (
    RegisterForm, LoginForm, ProfileForm, ProfileExtendedForm, 
    ClientForm, AccessLevelForm, ClientSearchForm
)
from .models import Profile, Client, AccessLevel
from .utils import create_client_from_user, get_client_by_user, is_premium_client


def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            
            # Создаем клиента на основе данных регистрации
            client_data = {
                'first_name': form.cleaned_data['first_name'],
                'last_name': form.cleaned_data['last_name'],
                'phone': form.cleaned_data['phone'],
                'birth_date': form.cleaned_data['birth_date'],
                'gender': form.cleaned_data['gender'],
                'email': form.cleaned_data['email'],
            }
            
            create_client_from_user(user, **client_data)
            
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
    client = get_client_by_user(request.user)
    context = {
        'client': client,
        'is_premium': is_premium_client(request.user)
    }
    return render(request, 'pages/news.html', context)


@login_required
def profile_view(request):
    profile, created = Profile.objects.get_or_create(user=request.user)
    client = get_client_by_user(request.user)
    
    if request.method == 'POST':
        user_form = ProfileForm(request.POST, instance=request.user)
        profile_form = ProfileExtendedForm(request.POST, request.FILES, instance=profile)
        
        if client:
            client_form = ClientForm(request.POST, instance=client)
        else:
            client_form = ClientForm(request.POST)
        
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            
            if client_form.is_valid():
                if client:
                    client_form.save()
                else:
                    # Создаем нового клиента
                    client_data = client_form.cleaned_data
                    create_client_from_user(request.user, **client_data)
                
                messages.success(request, 'Профиль успешно обновлен!')
                return redirect('profile')
    else:
        user_form = ProfileForm(instance=request.user)
        profile_form = ProfileExtendedForm(instance=profile)
        
        if client:
            client_form = ClientForm(instance=client)
        else:
            client_form = ClientForm()
    
    context = {
        'user_form': user_form,
        'profile_form': profile_form,
        'client_form': client_form,
        'profile': profile,
        'client': client,
        'is_premium': is_premium_client(request.user)
    }
    return render(request, 'pages/profile.html', context)


@login_required
def client_list_view(request):
    """Список всех клиентов (только для администраторов)"""
    if not request.user.is_staff:
        messages.error(request, 'У вас нет прав для просмотра этого раздела')
        return redirect('dashboard')
    
    search_form = ClientSearchForm(request.GET)
    clients = Client.objects.all()
    
    if search_form.is_valid():
        search_query = search_form.cleaned_data.get('search_query')
        access_level = search_form.cleaned_data.get('access_level')
        is_active = search_form.cleaned_data.get('is_active')
        city = search_form.cleaned_data.get('city')
        
        if search_query:
            clients = clients.filter(
                Q(first_name__icontains=search_query) |
                Q(last_name__icontains=search_query) |
                Q(phone__icontains=search_query) |
                Q(email__icontains=search_query)
            )
        
        if access_level:
            clients = clients.filter(access_level=access_level)
        
        if is_active:
            clients = clients.filter(is_active=is_active == 'true')
        
        if city:
            clients = clients.filter(city__icontains=city)
    
    paginator = Paginator(clients, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'clients': page_obj,
        'search_form': search_form,
        'access_levels': AccessLevel.objects.all(),
    }
    return render(request, 'accounts/client_list.html', context)


@login_required
def client_detail_view(request, client_id):
    """Детальная информация о клиенте"""
    if not request.user.is_staff:
        messages.error(request, 'У вас нет прав для просмотра этого раздела')
        return redirect('dashboard')
    
    client = get_object_or_404(Client, id=client_id)
    
    context = {
        'client': client,
    }
    return render(request, 'accounts/client_detail.html', context)


@login_required
def client_edit_view(request, client_id):
    """Редактирование клиента"""
    if not request.user.is_staff:
        messages.error(request, 'У вас нет прав для редактирования клиентов')
        return redirect('dashboard')
    
    client = get_object_or_404(Client, id=client_id)
    
    if request.method == 'POST':
        form = ClientForm(request.POST, instance=client)
        if form.is_valid():
            form.save()
            messages.success(request, 'Данные клиента успешно обновлены!')
            return redirect('client_detail', client_id=client.id)
    else:
        form = ClientForm(instance=client)
    
    context = {
        'form': form,
        'client': client,
    }
    return render(request, 'accounts/client_edit.html', context)


@login_required
def access_level_list_view(request):
    """Список уровней доступа"""
    if not request.user.is_staff:
        messages.error(request, 'У вас нет прав для просмотра этого раздела')
        return redirect('dashboard')
    
    access_levels = AccessLevel.objects.all()
    
    context = {
        'access_levels': access_levels,
    }
    return render(request, 'accounts/access_level_list.html', context)


@login_required
def access_level_edit_view(request, level_id):
    """Редактирование уровня доступа"""
    if not request.user.is_staff:
        messages.error(request, 'У вас нет прав для редактирования уровней доступа')
        return redirect('dashboard')
    
    access_level = get_object_or_404(AccessLevel, id=level_id)
    
    if request.method == 'POST':
        form = AccessLevelForm(request.POST, instance=access_level)
        if form.is_valid():
            form.save()
            messages.success(request, 'Уровень доступа успешно обновлен!')
            return redirect('access_level_list')
    else:
        form = AccessLevelForm(instance=access_level)
    
    context = {
        'form': form,
        'access_level': access_level,
    }
    return render(request, 'accounts/access_level_edit.html', context)


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
        'is_premium': is_premium_client(request.user)
    }
    return render(request, 'pages/converter.html', context)


@login_required
def about_view(request):
    return render(request, 'pages/about.html')


@login_required
def subscription_plans_view(request):
    """Страница выбора планов подписки"""
    client = get_client_by_user(request.user)
    current_plan = client.access_level if client else None
    
    # Определяем планы подписки
    plans = [
        {
            'id': 'basic',
            'name': 'Базовый',
            'price': '0',
            'currency': 'тг',
            'period': 'месяц',
            'is_current': current_plan and not current_plan.is_premium,
            'features': [
                'Доступ к новостям',
                'Доступ к конвертеру',
                'Возможность создать три копилки',
                'Ограничения периода отчетов'
            ],
            'color': '#1d5cff',
            'icon': 'clock'
        },
        {
            'id': 'premium',
            'name': 'Премиум',
            'price': '2990',
            'currency': 'тг',
            'period': 'месяц',
            'is_current': current_plan and current_plan.is_premium,
            'is_popular': True,
            'features': [
                'Неограниченное количество копилок',
                'Выбор периода для создания отчета',
                'Возможность привязать карту к приложению',
                'Приоритетная поддержка',
                'Расширенная аналитика'
            ],
            'color': '#ffd700',
            'icon': 'star'
        }
    ]
    
    context = {
        'plans': plans,
        'current_plan': current_plan,
        'is_premium': is_premium_client(request.user)
    }
    return render(request, 'accounts/subscription_plans.html', context)

# Create your views here.
