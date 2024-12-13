"""Tests for PasswordForm and NewPasswordMixin."""
from django.test import TestCase
from django.contrib.auth import get_user_model, authenticate
from tutorials.forms import PasswordForm

User = get_user_model()

class PasswordFormTestCase(TestCase):
    """Test suite for PasswordForm (includes NewPasswordMixin)."""

    def setUp(self):
        self.user = User.objects.create_user(
            username='@passworduser',
            email='pwuser@example.com',
            password='OldPassword123'
        )

    def test_form_valid_data(self):
        form_data = {
            'password': 'OldPassword123',   # current password
            'new_password': 'NewPassword123',
            'password_confirmation': 'NewPassword123'
        }
        form = PasswordForm(data=form_data, user=self.user)
        self.assertTrue(form.is_valid(), "Form should be valid with matching new_password and password_confirmation.")
        updated_user = form.save()
        self.assertIsNotNone(updated_user)
        self.assertTrue(authenticate(username='@passworduser', password='NewPassword123'))

    def test_form_invalid_mismatched_password(self):
        form_data = {
            'password': 'OldPassword123',
            'new_password': 'NewPassword123',
            'password_confirmation': 'MismatchPassword123'
        }
        form = PasswordForm(data=form_data, user=self.user)
        self.assertFalse(form.is_valid(), "Form should be invalid if new_password and confirmation do not match.")

    def test_form_invalid_current_password(self):
        form_data = {
            'password': 'WrongOldPassword',
            'new_password': 'NewPassword123',
            'password_confirmation': 'NewPassword123'
        }
        form = PasswordForm(data=form_data, user=self.user)
        self.assertFalse(form.is_valid(), "Form should be invalid if current password is incorrect.")
