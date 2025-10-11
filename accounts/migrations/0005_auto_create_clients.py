# Generated manually for auto-creating clients

from django.db import migrations
from django.contrib.auth.models import User
from accounts.models import Client, AccessLevel, Profile


def create_basic_access_level(apps, schema_editor):
    """Создает базовый уровень доступа"""
    AccessLevel = apps.get_model('accounts', 'AccessLevel')
    
    basic_level, created = AccessLevel.objects.get_or_create(
        name='Базовый',
        defaults={
            'description': 'Базовый уровень доступа для всех пользователей',
            'is_premium': False,
            'max_transactions_per_month': 50,
            'can_export_data': False,
            'can_advanced_analytics': False
        }
    )
    
    if created:
        print("Создан базовый уровень доступа")


def create_clients_for_existing_users(apps, schema_editor):
    """Создает клиентов для всех существующих пользователей"""
    User = apps.get_model('auth', 'User')
    Client = apps.get_model('accounts', 'Client')
    AccessLevel = apps.get_model('accounts', 'AccessLevel')
    Profile = apps.get_model('accounts', 'Profile')
    
    # Получаем базовый уровень доступа
    try:
        basic_level = AccessLevel.objects.get(name='Базовый')
    except AccessLevel.DoesNotExist:
        basic_level = AccessLevel.objects.create(
            name='Базовый',
            description='Базовый уровень доступа для всех пользователей',
            is_premium=False,
            max_transactions_per_month=50,
            can_export_data=False,
            can_advanced_analytics=False
        )
    
    # Создаем клиентов для всех пользователей, у которых их нет
    users_without_clients = User.objects.filter(client__isnull=True)
    
    for user in users_without_clients:
        # Создаем клиента
        client = Client.objects.create(
            user=user,
            access_level=basic_level,
            first_name=user.first_name or '',
            last_name=user.last_name or '',
            email=user.email or '',
            phone='',  # Будет заполнено позже
            birth_date='1990-01-01',  # Значение по умолчанию
            gender='M',  # Значение по умолчанию
            is_active=True
        )
        
        # Создаем профиль, если его нет
        Profile.objects.get_or_create(
            user=user,
            defaults={'client': client}
        )
        
        print(f"Создан клиент для пользователя: {user.username}")


def reverse_create_clients(apps, schema_editor):
    """Обратная операция - удаляет клиентов (НЕ РЕКОМЕНДУЕТСЯ)"""
    # Не делаем ничего, так как удаление клиентов может привести к потере данных
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0004_create_initial_access_levels'),
    ]

    operations = [
        migrations.RunPython(
            create_basic_access_level,
            reverse_create_clients,
        ),
        migrations.RunPython(
            create_clients_for_existing_users,
            reverse_create_clients,
        ),
    ]
