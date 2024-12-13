"""Tests for SignUpForm."""
from django.test import TestCase
from django.contrib.auth import get_user_model
from tutorials.forms import SignUpForm
from tutorials.models import StudentProfile, TutorProfile

User = get_user_model()

class SignUpFormTestCase(TestCase):
    """Test suite for SignUpForm."""

    def test_valid_student_sign_up(self):
        form_data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'username': '@johndoe',
            'email': 'john@example.com',
            'user_type': 'student',
            'new_password': 'Password123',
            'confirm_password': 'Password123'
        }
        form = SignUpForm(data=form_data)
        self.assertTrue(form.is_valid(), "Form should be valid for a proper student sign up.")
        user = form.save(commit=True)
        # Check user info
        self.assertEqual(user.first_name, 'John')
        self.assertTrue(user.is_student, "User should be a student.")
        self.assertFalse(user.is_tutor)
        self.assertTrue(StudentProfile.objects.filter(user=user).exists(), "StudentProfile should be created.")

    def test_valid_tutor_sign_up(self):
        form_data = {
            'first_name': 'Jane',
            'last_name': 'Smith',
            'username': '@janesmith',
            'email': 'jane@example.com',
            'user_type': 'tutor',
            'new_password': 'Password123',
            'confirm_password': 'Password123'
        }
        form = SignUpForm(data=form_data)
        self.assertTrue(form.is_valid(), "Form should be valid for a proper tutor sign up.")
        user = form.save(commit=True)
        self.assertEqual(user.last_name, 'Smith')
        self.assertFalse(user.is_student)
        self.assertTrue(user.is_tutor, "User should be a tutor.")
        self.assertTrue(TutorProfile.objects.filter(user=user).exists(), "TutorProfile should be created.")

    def test_mismatched_passwords(self):
        form_data = {
            'first_name': 'Bob',
            'last_name': 'Builder',
            'username': '@bobbuilder',
            'email': 'bob@example.com',
            'user_type': 'student',
            'new_password': 'Password123',
            'confirm_password': 'Mismatch123'
        }
        form = SignUpForm(data=form_data)
        self.assertFalse(form.is_valid(), "Form should be invalid if new_password and confirm_password don't match.")

    def test_blank_fields(self):
        form_data = {
            'first_name': '',
            'last_name': '',
            'username': '',
            'email': '',
            'user_type': 'student',
            'new_password': 'Password123',
            'confirm_password': 'Password123'
        }
        form = SignUpForm(data=form_data)
        self.assertFalse(form.is_valid(), "Form should be invalid with blank required fields.")
