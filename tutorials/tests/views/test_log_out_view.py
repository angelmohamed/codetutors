"""Tests for log_out view."""
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.auth import SESSION_KEY

from tutorials.models import StudentProfile

User = get_user_model()

class LogOutViewTestCase(TestCase):
    """Test suite for the log_out view."""

    def setUp(self):
        self.url = reverse('log_out')
        self.user = User.objects.create_user(
            username='@testuser',
            password='Password123',
            email="student123@gmail.com",
            is_student=True,  
            is_tutor=False
        )
        self.student_profile = StudentProfile.objects.create(user=self.user)


    def test_log_out_redirects_home(self):
        # Log in user
        self.client.login(username='@testuser', password='Password123')
        self.assertIn(SESSION_KEY, self.client.session, "User should be logged in.")
        response = self.client.get(self.url, follow=True)
        self.assertRedirects(response, reverse('home'))
        self.assertNotIn(SESSION_KEY, self.client.session, "User should be logged out after log_out view.")
