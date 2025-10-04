from django.db import models
from django.contrib.auth.models import User


class AccessLevel(models.Model):
    """Модель для уровней доступа пользователей"""
    name = models.CharField(max_length=50, unique=True, verbose_name="Название уровня")
    description = models.TextField(blank=True, verbose_name="Описание")
    is_premium = models.BooleanField(default=False, verbose_name="Премиум доступ")
    max_transactions_per_month = models.PositiveIntegerField(default=100, verbose_name="Максимум транзакций в месяц")
    can_export_data = models.BooleanField(default=False, verbose_name="Может экспортировать данные")
    can_advanced_analytics = models.BooleanField(default=False, verbose_name="Расширенная аналитика")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Уровень доступа"
        verbose_name_plural = "Уровни доступа"
        ordering = ['name']

    def __str__(self) -> str:
        return f"{self.name} ({'Премиум' if self.is_premium else 'Обычный'})"


class Client(models.Model):
    """Модель клиента с расширенной информацией"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='client', verbose_name="Пользователь")
    access_level = models.ForeignKey(AccessLevel, on_delete=models.PROTECT, verbose_name="Уровень доступа")
    
    # Персональная информация
    first_name = models.CharField(max_length=50, verbose_name="Имя")
    last_name = models.CharField(max_length=50, verbose_name="Фамилия")
    middle_name = models.CharField(max_length=50, blank=True, verbose_name="Отчество")
    
    # Контактная информация
    phone = models.CharField(max_length=20, unique=True, verbose_name="Телефон")
    email = models.EmailField(unique=True, verbose_name="Email")
    
    # Адрес
    address = models.TextField(blank=True, verbose_name="Адрес")
    city = models.CharField(max_length=100, blank=True, verbose_name="Город")
    postal_code = models.CharField(max_length=20, blank=True, verbose_name="Почтовый индекс")
    country = models.CharField(max_length=100, default="Россия", verbose_name="Страна")
    
    # Дополнительная информация
    birth_date = models.DateField(verbose_name="Дата рождения")
    gender = models.CharField(
        max_length=10,
        choices=[('M', 'Мужской'), ('F', 'Женский'), ('O', 'Другой')],
        verbose_name="Пол"
    )
    
    # Финансовая информация
    monthly_income = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        null=True, 
        blank=True,
        verbose_name="Месячный доход"
    )
    occupation = models.CharField(max_length=100, blank=True, verbose_name="Профессия")
    
    # Статус и даты
    is_active = models.BooleanField(default=True, verbose_name="Активный клиент")
    registration_date = models.DateTimeField(auto_now_add=True, verbose_name="Дата регистрации")
    last_login_date = models.DateTimeField(null=True, blank=True, verbose_name="Последний вход")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Обновлено")

    class Meta:
        verbose_name = "Клиент"
        verbose_name_plural = "Клиенты"
        ordering = ['last_name', 'first_name']

    def __str__(self) -> str:
        return f"{self.last_name} {self.first_name} ({self.user.username})"

    @property
    def full_name(self):
        """Возвращает полное имя клиента"""
        if self.middle_name:
            return f"{self.last_name} {self.first_name} {self.middle_name}"
        return f"{self.last_name} {self.first_name}"

    @property
    def is_premium(self):
        """Проверяет, является ли клиент премиум"""
        return self.access_level.is_premium


class Profile(models.Model):
    """Расширенный профиль пользователя, связанный с клиентом"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    client = models.OneToOneField(Client, on_delete=models.CASCADE, related_name='profile', null=True, blank=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    bio = models.TextField(max_length=500, blank=True)
    website = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"Profile({self.user.username})"

    @property
    def has_client_data(self):
        """Проверяет, есть ли связанные данные клиента"""
        return self.client is not None

# Create your models here.
