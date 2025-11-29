from datetime import date

from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.test import TestCase
from django.urls import reverse

from .models import AccessLevel, Client, Profile
from .signals import create_client_for_new_user
from .utils import (
    can_perform_action,
    create_client_from_user,
    downgrade_client_to_basic,
    get_client_statistics,
    upgrade_client_to_premium,
)


class SignalIsolationMixin:
    """Disable automatic client creation via signals while tests run."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        post_save.disconnect(create_client_for_new_user, sender=User)

    @classmethod
    def tearDownClass(cls):
        post_save.connect(create_client_for_new_user, sender=User)
        super().tearDownClass()


class ClientModelTests(SignalIsolationMixin, TestCase):
    def setUp(self):
        self.basic, _ = AccessLevel.objects.get_or_create(
            name='Базовый',
            defaults={
                'description': 'Стартовый план',
                'is_premium': False,
                'can_export_data': False,
                'can_advanced_analytics': False,
            },
        )
        self.premium, _ = AccessLevel.objects.get_or_create(
            name='Премиум',
            defaults={
                'description': 'Улучшенный план',
                'is_premium': True,
                'can_export_data': True,
                'can_advanced_analytics': True,
            },
        )
        self.user = User.objects.create_user(username='tester', password='secret', email='user@example.com')
        self.client_obj = Client.objects.create(
            user=self.user,
            access_level=self.basic,
            first_name='Ivan',
            last_name='Petrov',
            middle_name='Ivanovich',
            phone='+70000000000',
            email='client@example.com',
            birth_date=date(1990, 1, 1),
            gender='M',
        )

    def test_full_name_includes_middle_name(self):
        self.assertEqual(self.client_obj.full_name, 'Petrov Ivan Ivanovich')

    def test_is_premium_flag_reflects_access_level(self):
        self.assertFalse(self.client_obj.is_premium)
        self.client_obj.access_level = self.premium
        self.client_obj.save()
        self.assertTrue(self.client_obj.is_premium)


class UtilsTests(SignalIsolationMixin, TestCase):
    def setUp(self):
        self.basic, _ = AccessLevel.objects.get_or_create(
            name='Базовый',
            defaults={
                'description': 'Стартовый план',
                'is_premium': False,
                'can_export_data': False,
                'can_advanced_analytics': False,
            },
        )
        self.standard, _ = AccessLevel.objects.get_or_create(
            name='Обычный',
            defaults={
                'description': 'Обычный уровень',
                'is_premium': False,
                'can_export_data': False,
                'can_advanced_analytics': False,
            },
        )
        self.premium, _ = AccessLevel.objects.get_or_create(
            name='Премиум',
            defaults={
                'description': 'Максимальный план',
                'is_premium': True,
                'can_export_data': True,
                'can_advanced_analytics': True,
            },
        )
        self.user = User.objects.create_user(
            username='util_user',
            password='secret',
            email='util@example.com',
            first_name='Util',
            last_name='User',
        )

    def test_create_client_from_user_creates_profile(self):
        client = create_client_from_user(
            self.user,
            phone='+71111111111',
            first_name='Test',
            last_name='User',
            birth_date=date(1995, 5, 5),
            gender='M',
        )
        self.assertEqual(client.user, self.user)
        self.assertTrue(Profile.objects.filter(user=self.user).exists())

    def test_upgrade_and_downgrade_client(self):
        client = create_client_from_user(
            self.user,
            phone='+72222222222',
            first_name='Test',
            last_name='User',
            birth_date=date(1993, 3, 3),
            gender='F',
        )
        self.assertTrue(upgrade_client_to_premium(client))
        client.refresh_from_db()
        self.assertEqual(client.access_level.name, 'Премиум')
        self.assertTrue(downgrade_client_to_basic(client))
        client.refresh_from_db()
        self.assertEqual(client.access_level.name, 'Обычный')

    def test_can_perform_action_based_on_access_level(self):
        client = create_client_from_user(
            self.user,
            phone='+73333333333',
            first_name='Test',
            last_name='User',
            birth_date=date(1992, 2, 2),
            gender='O',
        )
        self.assertFalse(can_perform_action(self.user, 'export_data'))
        client.access_level = self.premium
        client.save()
        self.assertTrue(can_perform_action(self.user, 'advanced_analytics'))

    def test_get_client_statistics_returns_expected_counts(self):
        client = create_client_from_user(
            self.user,
            phone='+74444444444',
            first_name='Test',
            last_name='User',
            birth_date=date(1991, 1, 1),
            gender='M',
        )
        stats = get_client_statistics()
        self.assertEqual(stats['total_clients'], 1)
        self.assertEqual(stats['active_clients'], 1)
        self.assertEqual(stats['premium_clients'], 0)
        client.access_level = self.premium
        client.save()
        stats = get_client_statistics()
        self.assertEqual(stats['premium_clients'], 1)


class MonitoringViewsTests(TestCase):
    def test_health_check_returns_ok(self):
        response = self.client.get(reverse('health_check'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['status'], 'ok')

    def test_metrics_endpoint_returns_prometheus_payload(self):
        response = self.client.get(reverse('metrics'))
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'fintrack_request_total', response.content)


class ViewsIntegrationTests(SignalIsolationMixin, TestCase):
    """Integration tests for account views."""

    def setUp(self):
        self.basic, _ = AccessLevel.objects.get_or_create(
            name='Базовый',
            defaults={
                'description': 'Стартовый план',
                'is_premium': False,
                'can_export_data': False,
                'can_advanced_analytics': False,
            },
        )
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@example.com',
        )
        self.client_obj = Client.objects.create(
            user=self.user,
            access_level=self.basic,
            first_name='Test',
            last_name='User',
            phone='+79999999999',
            email='test@example.com',
            birth_date=date(1990, 1, 1),
            gender='M',
        )

    def test_register_view_renders_form(self):
        """Test that registration page is accessible."""
        response = self.client.get(reverse('register'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Регистрация')

    def test_login_required_redirects_to_login(self):
        """Test that protected views redirect to login."""
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/', response.url)

    def test_dashboard_view_requires_authentication(self):
        """Test that dashboard is accessible after login."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)

    def test_profile_view_requires_authentication(self):
        """Test that profile page requires authentication."""
        response = self.client.get(reverse('profile'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/', response.url)

        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('profile'))
        self.assertEqual(response.status_code, 200)
