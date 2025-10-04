from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from .models import Profile, Client, AccessLevel


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=50, required=True)
    last_name = forms.CharField(max_length=50, required=True)
    phone = forms.CharField(max_length=20, required=True)
    birth_date = forms.DateField(required=True, widget=forms.DateInput(attrs={'type': 'date'}))
    gender = forms.ChoiceField(
        choices=[('M', 'Мужской'), ('F', 'Женский'), ('O', 'Другой')],
        required=True
    )

    class Meta:
        model = User
        fields = ("username", "email", "first_name", "last_name", "password1", "password2")

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("Этот email уже используется")
        return email

    def clean_phone(self):
        phone = self.cleaned_data.get("phone")
        if Client.objects.filter(phone=phone).exists():
            raise forms.ValidationError("Этот телефон уже используется")
        return phone


class LoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={"autofocus": True}))
    password = forms.CharField(label="Password", strip=False, widget=forms.PasswordInput)


class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        widgets = {
            'first_name': forms.TextInput(attrs={'placeholder': 'Имя'}),
            'last_name': forms.TextInput(attrs={'placeholder': 'Фамилия'}),
            'email': forms.EmailInput(attrs={'placeholder': 'Email'}),
        }


class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = [
            'first_name', 'last_name', 'middle_name', 'phone', 'email',
            'address', 'city', 'postal_code', 'country', 'birth_date',
            'gender', 'monthly_income', 'occupation'
        ]
        widgets = {
            'first_name': forms.TextInput(attrs={'placeholder': 'Имя'}),
            'last_name': forms.TextInput(attrs={'placeholder': 'Фамилия'}),
            'middle_name': forms.TextInput(attrs={'placeholder': 'Отчество'}),
            'phone': forms.TextInput(attrs={'placeholder': '+7 (999) 123-45-67'}),
            'email': forms.EmailInput(attrs={'placeholder': 'email@example.com'}),
            'address': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Полный адрес'}),
            'city': forms.TextInput(attrs={'placeholder': 'Город'}),
            'postal_code': forms.TextInput(attrs={'placeholder': '123456'}),
            'country': forms.TextInput(attrs={'placeholder': 'Страна'}),
            'birth_date': forms.DateInput(attrs={'type': 'date'}),
            'monthly_income': forms.NumberInput(attrs={'placeholder': '50000.00', 'step': '0.01'}),
            'occupation': forms.TextInput(attrs={'placeholder': 'Профессия'}),
        }

    def clean_phone(self):
        phone = self.cleaned_data.get("phone")
        if self.instance.pk:
            # При редактировании исключаем текущий объект
            if Client.objects.filter(phone=phone).exclude(pk=self.instance.pk).exists():
                raise forms.ValidationError("Этот телефон уже используется")
        else:
            # При создании нового клиента
            if Client.objects.filter(phone=phone).exists():
                raise forms.ValidationError("Этот телефон уже используется")
        return phone

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if self.instance.pk:
            # При редактировании исключаем текущий объект
            if Client.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
                raise forms.ValidationError("Этот email уже используется")
        else:
            # При создании нового клиента
            if Client.objects.filter(email=email).exists():
                raise forms.ValidationError("Этот email уже используется")
        return email


class ProfileExtendedForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['avatar', 'bio', 'website']
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Расскажите о себе...'}),
            'website': forms.URLInput(attrs={'placeholder': 'https://example.com'}),
        }


class AccessLevelForm(forms.ModelForm):
    class Meta:
        model = AccessLevel
        fields = [
            'name', 'description', 'is_premium', 'max_transactions_per_month',
            'can_export_data', 'can_advanced_analytics'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Название уровня'}),
            'description': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Описание уровня доступа'}),
            'max_transactions_per_month': forms.NumberInput(attrs={'min': 1}),
        }


class ClientSearchForm(forms.Form):
    search_query = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Поиск по имени, телефону или email'})
    )
    access_level = forms.ModelChoiceField(
        queryset=AccessLevel.objects.all(),
        required=False,
        empty_label="Все уровни доступа"
    )
    is_active = forms.ChoiceField(
        choices=[('', 'Все'), ('true', 'Активные'), ('false', 'Неактивные')],
        required=False
    )
    city = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Фильтр по городу'})
    )
