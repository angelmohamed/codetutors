"""Tests for LogInForm."""
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from tutorials.forms import LogInForm

User = get_user_model()

class LogInFormTestCase(TestCase):
    """Test suite for LogInForm."""

    def setUp(self):
        # Create a sample user for authentication tests
        self.user = User.objects.create(
            username='@testuser',
            email='test@example.com',
            password=make_password('Password123')  # Store a hashed password
        )

    def test_form_is_valid_with_correct_credentials(self):
        form_data = {
            'username': '@testuser',
            'password': 'Password123'
        }
        form = LogInForm(data=form_data)
        self.assertTrue(form.is_valid(), "Form should be valid with correct credentials.")
        self.assertEqual(form.get_user(), self.user, "Form should authenticate the correct user.")

    def test_form_is_invalid_with_incorrect_username(self):
        form_data = {
            'username': '@wronguser',
            'password': 'Password123'
        }
        form = LogInForm(data=form_data)
        self.assertFalse(form.is_valid(), "Form should be invalid with incorrect username.")
        self.assertIsNone(form.get_user())

    def test_form_is_invalid_with_incorrect_password(self):
        form_data = {
            'username': '@testuser',
            'password': 'WrongPassword'
        }
        form = LogInForm(data=form_data)
        self.assertFalse(form.is_valid(), "Form should be invalid with incorrect password.")
        self.assertIsNone(form.get_user())

    def test_form_is_invalid_with_blank_credentials(self):
        form_data = {
            'username': '',
            'password': ''
        }
        form = LogInForm(data=form_data)
        self.assertFalse(form.is_valid(), "Form should be invalid with blank username/password.")
        self.assertIsNone(form.get_user())
