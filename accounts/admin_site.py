from django.contrib.admin import AdminSite
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from django.db.models import Count
from django.utils.html import format_html
from .models import Client, AccessLevel, Profile


class FinTrackAdminSite(AdminSite):
    site_header = 'FinTrack Administration'
    site_title = 'FinTrack Admin'
    index_title = 'Панель администратора'
    
    def index(self, request, extra_context=None):
        """
        Кастомная главная страница админки с статистикой
        """
        extra_context = extra_context or {}
        
        # Получаем статистику
        total_users = User.objects.count()
        total_clients = Client.objects.filter(is_active=True).count()
        premium_clients = Client.objects.filter(
            access_level__is_premium=True, 
            is_active=True
        ).count()
        total_access_levels = AccessLevel.objects.count()
        
        # Последние действия (заглушка для демонстрации)
        recent_actions = [
            {
                'icon': '👤',
                'description': 'Новый пользователь зарегистрирован',
                'time': '2 минуты назад'
            },
            {
                'icon': '💼',
                'description': 'Клиент обновил профиль',
                'time': '15 минут назад'
            },
            {
                'icon': '⭐',
                'description': 'Премиум подписка активирована',
                'time': '1 час назад'
            },
            {
                'icon': '📊',
                'description': 'Создан новый уровень доступа',
                'time': '2 часа назад'
            }
        ]
        
        extra_context.update({
            'total_users': total_users,
            'total_clients': total_clients,
            'premium_clients': premium_clients,
            'total_access_levels': total_access_levels,
            'recent_actions': recent_actions,
        })
        
        return super().index(request, extra_context)


# Создаем кастомный админ-сайт
admin_site = FinTrackAdminSite(name='fintrack_admin')

# Регистрируем модели в кастомном админ-сайте
from .admin import AccessLevelAdmin, ClientAdmin, ProfileAdmin, CustomUserAdmin

admin_site.register(AccessLevel, AccessLevelAdmin)
admin_site.register(Client, ClientAdmin)
admin_site.register(Profile, ProfileAdmin)
admin_site.register(User, CustomUserAdmin)
