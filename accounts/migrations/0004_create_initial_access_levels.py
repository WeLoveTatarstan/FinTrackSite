# Generated manually for initial AccessLevel data

from django.db import migrations


def create_initial_access_levels(apps, schema_editor):
    AccessLevel = apps.get_model('accounts', 'AccessLevel')
    
    # Создаем обычный уровень доступа
    AccessLevel.objects.create(
        name='Обычный',
        description='Базовый уровень доступа для обычных пользователей',
        is_premium=False,
        max_transactions_per_month=50,
        can_export_data=False,
        can_advanced_analytics=False
    )
    
    # Создаем премиум уровень доступа
    AccessLevel.objects.create(
        name='Премиум',
        description='Расширенный уровень доступа с дополнительными возможностями',
        is_premium=True,
        max_transactions_per_month=1000,
        can_export_data=True,
        can_advanced_analytics=True
    )


def reverse_create_initial_access_levels(apps, schema_editor):
    AccessLevel = apps.get_model('accounts', 'AccessLevel')
    AccessLevel.objects.filter(name__in=['Обычный', 'Премиум']).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0003_create_client_and_access_level_models'),
    ]

    operations = [
        migrations.RunPython(
            create_initial_access_levels,
            reverse_create_initial_access_levels
        ),
    ]
