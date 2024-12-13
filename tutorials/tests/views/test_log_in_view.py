"""Tests for LogInView."""
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.auth import login, SESSION_KEY
from tutorials.forms import LogInForm
from tutorials.models import StudentProfile

User = get_user_model()

class LogInViewTestCase(TestCase):
    """Test suite for LogInView."""

    def setUp(self):
        self.url = reverse('log_in') 
        self.user = User.objects.create_user(
            username='@testuser',
            email='test@example.org',
            password='Password123',
            is_student=True,
            is_tutor=False
        )
        self.student_profile = StudentProfile.objects.create(user=self.user)

        print(self.user.is_student)

    def test_get_log_in_view(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'log_in.html')
        self.assertIsInstance(response.context['form'], LogInForm)

    def test_post_log_in_valid_credentials(self):
        form_data = {
            'username': '@testuser',
            'password': 'Password123'
        }
        response = self.client.post(self.url, form_data, follow=True)
        self.assertRedirects(response, reverse('dashboard'))
        # Check if user is authenticated
        self.assertIn(SESSION_KEY, self.client.session)

    def test_post_log_in_invalid_credentials(self):
        form_data = {
            'username': '@wronguser',
            'password': 'WrongPassword'
        }
        response = self.client.post(self.url, form_data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'log_in.html')
        self.assertFormError(response, 'form', None, 'Invalid username or password.')
        self.assertNotIn(SESSION_KEY, self.client.session)

    def test_get_log_in_redirects_if_authenticated(self):
        # Log in user
        self.client.login(username='@testuser', password='Password123')
        response = self.client.get(self.url, follow=True)
        self.assertRedirects(response, reverse('dashboard'))
