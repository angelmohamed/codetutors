"""Tests for the PasswordView."""
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model, SESSION_KEY
from tutorials.forms import PasswordForm

from tutorials.models import StudentProfile

User = get_user_model()

class PasswordViewTestCase(TestCase):
    """Test suite for PasswordView."""

    def setUp(self):
        self.url = reverse('password')
        self.user = User.objects.create_user(
            username='@pwduser',
            password='OldPassword123',
            email="student123@gmail.com",
            is_student=True,
            is_tutor=False
        )
        self.student_profile = StudentProfile.objects.create(user=self.user)

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(self.url, follow=True)
        self.assertNotEqual(response.request['PATH_INFO'], self.url, "Should redirect if not logged in.")

    def test_get_password_view(self):
        self.client.login(username='@pwduser', password='OldPassword123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'password.html')
        self.assertIsInstance(response.context['form'], PasswordForm)

    def test_post_valid_password_change(self):
        self.client.login(username='@pwduser', password='OldPassword123')
        form_data = {
            'password': 'OldPassword123',
            'new_password': 'NewPassword123',
            'password_confirmation': 'NewPassword123'
        }
        response = self.client.post(self.url, form_data, follow=True)
        self.assertRedirects(response, reverse('dashboard'))
        # Verify the password is updated
        self.assertIn(SESSION_KEY, self.client.session)
        self.assertTrue(self.client.login(username='@pwduser', password='NewPassword123'))

    def test_post_invalid_current_password(self):
        self.client.login(username='@pwduser', password='OldPassword123')
        form_data = {
            'password': 'WrongPassword',
            'new_password': 'NewPassword123',
            'password_confirmation': 'NewPassword123'
        }
        response = self.client.post(self.url, form_data)
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, 'form', 'password', "Password is invalid")
