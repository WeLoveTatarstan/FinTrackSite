"""
Сигналы для автоматического создания клиентов при регистрации пользователей
"""
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Client, AccessLevel, Profile
from .utils import create_client_from_user


@receiver(post_save, sender=User)
def create_client_for_new_user(sender, instance, created, **kwargs):
    """
    Автоматически создает клиента для каждого нового пользователя
    """
    if created:
        # Создаем базовый уровень доступа, если его нет
        basic_level, _ = AccessLevel.objects.get_or_create(
            name='Базовый',
            defaults={
                'description': 'Базовый уровень доступа для всех пользователей',
                'is_premium': False,
                'max_transactions_per_month': 50,
                'can_export_data': False,
                'can_advanced_analytics': False
            }
        )
        
        # Создаем клиента с базовыми данными
        client_data = {
            'first_name': instance.first_name or '',
            'last_name': instance.last_name or '',
            'email': instance.email or '',
            'phone': '',  # Будет заполнено при регистрации
        }
        
        # Создаем клиента
        client = Client.objects.create(
            user=instance,
            access_level=basic_level,
            **client_data
        )
        
        # Создаем профиль
        Profile.objects.create(
            user=instance,
            client=client
        )


@receiver(post_save, sender=User)
def update_client_data(sender, instance, created, **kwargs):
    """
    Обновляет данные клиента при изменении данных пользователя
    """
    if not created and hasattr(instance, 'client'):
        client = instance.client
        client.first_name = instance.first_name or client.first_name
        client.last_name = instance.last_name or client.last_name
        client.email = instance.email or client.email
        client.save()
