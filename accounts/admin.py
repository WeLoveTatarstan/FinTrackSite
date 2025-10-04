from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import AccessLevel, Client, Profile


@admin.register(AccessLevel)
class AccessLevelAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_premium', 'max_transactions_per_month', 'can_export_data', 'can_advanced_analytics']
    list_filter = ['is_premium', 'can_export_data', 'can_advanced_analytics']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'description', 'is_premium')
        }),
        ('Ограничения', {
            'fields': ('max_transactions_per_month', 'can_export_data', 'can_advanced_analytics')
        }),
        ('Системная информация', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'user', 'access_level', 'phone', 'email', 'is_active', 'registration_date']
    list_filter = ['access_level', 'is_active', 'gender', 'country', 'city']
    search_fields = ['first_name', 'last_name', 'middle_name', 'phone', 'email', 'user__username']
    readonly_fields = ['registration_date', 'updated_at']
    list_per_page = 25
    
    fieldsets = (
        ('Пользователь и доступ', {
            'fields': ('user', 'access_level', 'is_active')
        }),
        ('Персональная информация', {
            'fields': ('first_name', 'last_name', 'middle_name', 'birth_date', 'gender')
        }),
        ('Контактная информация', {
            'fields': ('phone', 'email')
        }),
        ('Адрес', {
            'fields': ('address', 'city', 'postal_code', 'country'),
            'classes': ('collapse',)
        }),
        ('Финансовая информация', {
            'fields': ('monthly_income', 'occupation'),
            'classes': ('collapse',)
        }),
        ('Системная информация', {
            'fields': ('registration_date', 'last_login_date', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'has_client_data', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__username', 'user__email']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('user', 'client')
        }),
        ('Дополнительная информация', {
            'fields': ('avatar', 'bio', 'website')
        }),
        ('Системная информация', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


# Расширяем стандартную админку User для отображения связанных моделей
class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'Профиль'


class ClientInline(admin.StackedInline):
    model = Client
    can_delete = False
    verbose_name_plural = 'Клиент'
    extra = 0


class CustomUserAdmin(UserAdmin):
    inlines = (ProfileInline, ClientInline)
    list_display = UserAdmin.list_display + ('get_client_access_level',)
    
    def get_client_access_level(self, obj):
        if hasattr(obj, 'client'):
            return obj.client.access_level.name
        return 'Нет данных'
    get_client_access_level.short_description = 'Уровень доступа'


# Перерегистрируем UserAdmin
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
