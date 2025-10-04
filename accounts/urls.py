from django.urls import path
from django.contrib.auth import views as auth_views
from .views import (
    register_view, dashboard_view, login_view, profile_view, 
    converter_view, about_view, client_list_view, client_detail_view,
    client_edit_view, access_level_list_view, access_level_edit_view,
    subscription_plans_view
)


urlpatterns = [
    # Основные страницы
    path('register/', register_view, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='accounts/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('dashboard/', dashboard_view, name='dashboard'),
    path('news/', dashboard_view, name='news'),
    path('profile/', profile_view, name='profile'),
    path('converter/', converter_view, name='converter'),
    path('about/', about_view, name='about'),
    path('subscription/', subscription_plans_view, name='subscription_plans'),
    
    # Управление клиентами (только для администраторов)
    path('clients/', client_list_view, name='client_list'),
    path('clients/<int:client_id>/', client_detail_view, name='client_detail'),
    path('clients/<int:client_id>/edit/', client_edit_view, name='client_edit'),
    
    # Управление уровнями доступа (только для администраторов)
    path('access-levels/', access_level_list_view, name='access_level_list'),
    path('access-levels/<int:level_id>/edit/', access_level_edit_view, name='access_level_edit'),
]


