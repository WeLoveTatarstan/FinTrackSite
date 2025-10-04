# Generated manually for new Client and AccessLevel models

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_profile_avatar_profile_bio_profile_birth_date_and_more'),
    ]

    operations = [
        # Create AccessLevel model
        migrations.CreateModel(
            name='AccessLevel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, unique=True, verbose_name='Название уровня')),
                ('description', models.TextField(blank=True, verbose_name='Описание')),
                ('is_premium', models.BooleanField(default=False, verbose_name='Премиум доступ')),
                ('max_transactions_per_month', models.PositiveIntegerField(default=100, verbose_name='Максимум транзакций в месяц')),
                ('can_export_data', models.BooleanField(default=False, verbose_name='Может экспортировать данные')),
                ('can_advanced_analytics', models.BooleanField(default=False, verbose_name='Расширенная аналитика')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Уровень доступа',
                'verbose_name_plural': 'Уровни доступа',
                'ordering': ['name'],
            },
        ),
        
        # Create Client model
        migrations.CreateModel(
            name='Client',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=50, verbose_name='Имя')),
                ('last_name', models.CharField(max_length=50, verbose_name='Фамилия')),
                ('middle_name', models.CharField(blank=True, max_length=50, verbose_name='Отчество')),
                ('phone', models.CharField(max_length=20, unique=True, verbose_name='Телефон')),
                ('email', models.EmailField(unique=True, verbose_name='Email')),
                ('address', models.TextField(blank=True, verbose_name='Адрес')),
                ('city', models.CharField(blank=True, max_length=100, verbose_name='Город')),
                ('postal_code', models.CharField(blank=True, max_length=20, verbose_name='Почтовый индекс')),
                ('country', models.CharField(default='Россия', max_length=100, verbose_name='Страна')),
                ('birth_date', models.DateField(verbose_name='Дата рождения')),
                ('gender', models.CharField(choices=[('M', 'Мужской'), ('F', 'Женский'), ('O', 'Другой')], max_length=10, verbose_name='Пол')),
                ('monthly_income', models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True, verbose_name='Месячный доход')),
                ('occupation', models.CharField(blank=True, max_length=100, verbose_name='Профессия')),
                ('is_active', models.BooleanField(default=True, verbose_name='Активный клиент')),
                ('registration_date', models.DateTimeField(auto_now_add=True, verbose_name='Дата регистрации')),
                ('last_login_date', models.DateTimeField(blank=True, null=True, verbose_name='Последний вход')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Обновлено')),
                ('access_level', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='accounts.accesslevel', verbose_name='Уровень доступа')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='client', to='auth.user', verbose_name='Пользователь')),
            ],
            options={
                'verbose_name': 'Клиент',
                'verbose_name_plural': 'Клиенты',
                'ordering': ['last_name', 'first_name'],
            },
        ),
        
        # Update Profile model to add client relationship
        migrations.AddField(
            model_name='profile',
            name='client',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='profile', to='accounts.client'),
        ),
        
        # Remove old fields from Profile that are now in Client
        migrations.RemoveField(
            model_name='profile',
            name='birth_date',
        ),
        migrations.RemoveField(
            model_name='profile',
            name='location',
        ),
        migrations.RemoveField(
            model_name='profile',
            name='phone',
        ),
    ]
