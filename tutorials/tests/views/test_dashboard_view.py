from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from tutorials.models import StudentProfile, TutorProfile

User = get_user_model()

class DashboardViewTestCase(TestCase):
    """Test suite for the dashboard view."""

    def setUp(self):
        self.url = reverse('dashboard')

        # Create a unique student
        self.student_user = User.objects.create_user(
            username='@studentuser',
            email='student_user@example.com',
            password='Student123',
            is_student=True,
            is_tutor=False
        )
        StudentProfile.objects.create(user=self.student_user)

        # Create a unique tutor
        self.tutor_user = User.objects.create_user(
            username='@tutoruser',
            email='tutor_user@example.com',
            password='Tutor123',
            is_student=False,
            is_tutor=True
        )
        TutorProfile.objects.create(user=self.tutor_user)

    def test_dashboard_redirect_when_not_logged_in(self):
        # Not logged in, so we expect a redirect
        response = self.client.get(self.url, follow=True)
        # By default, login_required would redirect to /accounts/login/ or whatever your LOGIN_URL is
        self.assertNotEqual(response.request['PATH_INFO'], self.url)

    def test_dashboard_student_view(self):
        # Log in the student
        self.client.login(username='@studentuser', password='Student123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'student_dashboard.html')
        self.assertIn('invoices', response.context)
        self.assertIn('upcoming_lessons', response.context)
        self.assertIn('tutors', response.context)

    def test_dashboard_tutor_view(self):
        # Log in the tutor
        self.client.login(username='@tutoruser', password='Tutor123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tutor_dashboard.html')
        self.assertIn('upcoming_lessons', response.context)
        self.assertIn('tutor_form', response.context)
