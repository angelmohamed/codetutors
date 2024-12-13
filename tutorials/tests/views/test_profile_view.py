"""Tests for ProfileUpdateView and TutorProfileUpdateView."""
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from tutorials.forms import UserForm, TutorProfileForm
from tutorials.models import TutorProfile, StudentProfile



User = get_user_model()

class ProfileUpdateViewTestCase(TestCase):
    """Test suite for the ProfileUpdateView."""

    def setUp(self):
        self.url = reverse('profile')
        self.user = User.objects.create_user(
            username='@profileuser',
            password='Password123',
            first_name='Old',
            last_name='Name',
            email='old@example.com',
            is_student=True,
            is_tutor=False
        )
        self.student_profile = StudentProfile.objects.create(user=self.user)

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(self.url, follow=True)
        self.assertNotEqual(response.request['PATH_INFO'], self.url, "Should redirect if not logged in.")

    def test_get_profile_update_form(self):
        self.client.login(username='@profileuser', password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'profile.html')
        self.assertIsInstance(response.context['form'], UserForm)

    def test_post_valid_profile_update(self):
        self.client.login(username='@profileuser', password='Password123')
        form_data = {
            'first_name': 'New',
            'last_name': 'Name',
            'username': '@profileuser',
            'email': 'new@example.com'
        }
        response = self.client.post(self.url, form_data, follow=True)
        self.assertRedirects(response, reverse('dashboard'))
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, 'New')
        self.assertEqual(self.user.email, 'new@example.com')


class TutorProfileUpdateViewTestCase(TestCase):
    """Test suite for TutorProfileUpdateView."""

    def setUp(self):
        self.url = reverse('tutor_profile')
        self.user = User.objects.create_user(
            username='@tutoruser',
            password='Password123',
            is_student=False,
            is_tutor=True
        )
        self.tutor_profile = TutorProfile.objects.create(
            user=self.user,
            bio='Old bio',
            experience_years=5,
            contact_number='1234567890',
            languages='Python',
            specializations='Django'
        )

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(self.url, follow=True)
        self.assertNotEqual(response.request['PATH_INFO'], self.url, "Should redirect if not logged in.")

    def test_get_tutor_profile_update_form(self):
        self.client.login(username='@tutoruser', password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tutor_profile.html')
        self.assertIsInstance(response.context['form'], TutorProfileForm)

    def test_post_valid_tutor_profile_update(self):
        self.client.login(username='@tutoruser', password='Password123')
        form_data = {
            'bio': 'New Bio',
            'experience_years': 10,
            'contact_number': '0987654321',
            'languages': 'Python, Go',
            'specializations': 'Flask, Docker'
        }
        response = self.client.post(self.url, form_data, follow=True)
        self.assertRedirects(response, reverse('dashboard'))
        self.tutor_profile.refresh_from_db()
        self.assertEqual(self.tutor_profile.bio, 'New Bio')
        self.assertEqual(self.tutor_profile.experience_years, 10)
        self.assertEqual(self.tutor_profile.contact_number, '0987654321')
        self.assertEqual(self.tutor_profile.languages, 'Python, Go')
        self.assertEqual(self.tutor_profile.specializations, 'Flask, Docker')
