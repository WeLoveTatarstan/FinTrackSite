"""
Утилиты для работы с клиентами и уровнями доступа
"""
from django.contrib.auth.models import User
from .models import Client, AccessLevel, Profile


def create_client_from_user(user, access_level_name='Обычный', **client_data):
    """
    Создает клиента на основе существующего пользователя
    
    Args:
        user: Объект User Django
        access_level_name: Название уровня доступа ('Обычный' или 'Премиум')
        **client_data: Дополнительные данные клиента
    
    Returns:
        Client: Созданный объект клиента
    """
    try:
        access_level = AccessLevel.objects.get(name=access_level_name)
    except AccessLevel.DoesNotExist:
        # Если уровень не найден, создаем обычный
        access_level = AccessLevel.objects.filter(is_premium=False).first()
        if not access_level:
            access_level = AccessLevel.objects.create(
                name='Обычный',
                description='Базовый уровень доступа',
                is_premium=False
            )
    
    # Подготавливаем данные клиента
    client_data.setdefault('first_name', user.first_name or '')
    client_data.setdefault('last_name', user.last_name or '')
    client_data.setdefault('email', user.email or '')
    client_data.setdefault('phone', '')
    
    # Создаем клиента
    client = Client.objects.create(
        user=user,
        access_level=access_level,
        **client_data
    )
    
    # Обновляем профиль, если он существует
    try:
        profile = user.profile
        profile.client = client
        profile.save()
    except Profile.DoesNotExist:
        Profile.objects.create(user=user, client=client)
    
    return client


def upgrade_client_to_premium(client):
    """
    Повышает уровень доступа клиента до премиум
    
    Args:
        client: Объект Client
    
    Returns:
        bool: True если обновление прошло успешно
    """
    try:
        premium_level = AccessLevel.objects.get(name='Премиум')
        client.access_level = premium_level
        client.save()
        return True
    except AccessLevel.DoesNotExist:
        return False


def downgrade_client_to_basic(client):
    """
    Понижает уровень доступа клиента до обычного
    
    Args:
        client: Объект Client
    
    Returns:
        bool: True если обновление прошло успешно
    """
    try:
        basic_level = AccessLevel.objects.get(name='Обычный')
        client.access_level = basic_level
        client.save()
        return True
    except AccessLevel.DoesNotExist:
        return False


def get_client_by_user(user):
    """
    Получает клиента по пользователю
    
    Args:
        user: Объект User Django
    
    Returns:
        Client или None
    """
    try:
        return user.client
    except Client.DoesNotExist:
        return None


def is_premium_client(user):
    """
    Проверяет, является ли пользователь премиум-клиентом
    
    Args:
        user: Объект User Django
    
    Returns:
        bool: True если пользователь премиум-клиент
    """
    client = get_client_by_user(user)
    return client and client.is_premium


def can_perform_action(user, action_type):
    """
    Проверяет, может ли пользователь выполнить определенное действие
    
    Args:
        user: Объект User Django
        action_type: Тип действия ('export_data', 'advanced_analytics')
    
    Returns:
        bool: True если действие разрешено
    """
    client = get_client_by_user(user)
    if not client:
        return False
    
    access_level = client.access_level
    
    if action_type == 'export_data':
        return access_level.can_export_data
    elif action_type == 'advanced_analytics':
        return access_level.can_advanced_analytics
    
    return False


def get_client_statistics():
    """
    Возвращает статистику по клиентам
    
    Returns:
        dict: Словарь со статистикой
    """
    total_clients = Client.objects.count()
    active_clients = Client.objects.filter(is_active=True).count()
    premium_clients = Client.objects.filter(access_level__is_premium=True).count()
    basic_clients = Client.objects.filter(access_level__is_premium=False).count()
    
    return {
        'total_clients': total_clients,
        'active_clients': active_clients,
        'premium_clients': premium_clients,
        'basic_clients': basic_clients,
        'inactive_clients': total_clients - active_clients,
    }
