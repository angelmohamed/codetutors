"""Tests for SignUpView."""
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from tutorials.models import StudentProfile, TutorProfile
from tutorials.forms import SignUpForm

User = get_user_model()

class SignUpViewTestCase(TestCase):
    """Test suite for the SignUpView."""

    def setUp(self):
        self.url = reverse('sign_up') 

    def test_get_sign_up_view_renders_correct_template(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'sign_up.html')
        self.assertIsInstance(response.context['form'], SignUpForm)

    def test_can_sign_up_as_student(self):
        form_input = {
            'first_name': 'John',
            'last_name': 'Doe',
            'username': '@johndoe',
            'email': 'john@example.org',
            'user_type': 'student',
            'new_password': 'Password123',
            'confirm_password': 'Password123'
        }
        response = self.client.post(self.url, form_input, follow=True)
        self.assertRedirects(response, reverse('dashboard')) 
        self.assertTrue(User.objects.filter(username='@johndoe').exists())
        user = User.objects.get(username='@johndoe')
        self.assertTrue(user.is_student)
        self.assertFalse(user.is_tutor)
        self.assertTrue(StudentProfile.objects.filter(user=user).exists())

    def test_can_sign_up_as_tutor(self):
        form_input = {
            'first_name': 'Jane',
            'last_name': 'Smith',
            'username': '@janesmith',
            'email': 'jane@example.org',
            'user_type': 'tutor',
            'new_password': 'Password123',
            'confirm_password': 'Password123'
        }
        response = self.client.post(self.url, form_input, follow=True)
        self.assertRedirects(response, reverse('dashboard'))
        self.assertTrue(User.objects.filter(username='@janesmith').exists())
        user = User.objects.get(username='@janesmith')
        self.assertFalse(user.is_student)
        self.assertTrue(user.is_tutor)
        self.assertTrue(TutorProfile.objects.filter(user=user).exists())

    def test_sign_up_view_rejects_mismatched_passwords(self):
        form_input = {
            'first_name': 'Alice',
            'last_name': 'Wonderland',
            'username': '@alice',
            'email': 'alice@example.org',
            'user_type': 'student',
            'new_password': 'Password123',
            'confirm_password': 'Mismatch123'
        }
        response = self.client.post(self.url, form_input)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username='@alice').exists())
        self.assertFormError(response, 'form', 'confirm_password', "Passwords do not match.")

    def test_sign_up_view_redirects_if_logged_in(self):
        # Create a user
        user = User.objects.create_user(
            username='@existinguser',
            password='ExistingPass123'
        )
        self.client.login(username='@existinguser', password='ExistingPass123')
        response = self.client.get(self.url)
        self.assertNotEqual(response.status_code, 200, "Should redirect away if user is already logged in.")
