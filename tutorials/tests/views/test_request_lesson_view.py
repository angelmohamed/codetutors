"""Tests for the request_lesson view."""
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from tutorials.models import StudentProfile, TutorProfile, LessonRequest, Term
from tutorials.forms import LessonRequestForm

User = get_user_model()

class RequestLessonViewTestCase(TestCase):
    """Test suite for request_lesson view."""

    def setUp(self):
        self.student_user = User.objects.create_user(
            username='@student',
            password='Student123',
            email="student123@gmail.com",
            is_student=True,
            is_tutor=False
        )
        self.tutor_user = User.objects.create_user(
            username='@tutor',
            password='Tutor123',
            email="tutor123@gmail.com",
            is_tutor=True,
            is_student=False
        )
        self.student_profile = StudentProfile.objects.create(user=self.student_user)
        self.tutor_profile = TutorProfile.objects.create(user=self.tutor_user)

        self.url = reverse('request_lesson', kwargs={'tutor_id': self.tutor_profile.id})

    def test_request_lesson_view_redirect_if_not_logged_in(self):
        response = self.client.get(self.url, follow=True)
        self.assertNotEqual(response.request['PATH_INFO'], self.url, "Should redirect to login page if not logged in.")

    def test_get_request_lesson_form(self):
        self.client.login(username='@student', password='Student123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'request_lesson.html')
        self.assertIsInstance(response.context['form'], LessonRequestForm)

    def test_post_valid_lesson_request_form(self):
        self.client.login(username='@student', password='Student123')

        # Create a Term
        term = Term.objects.create(
            name='Spring 2025',
            start_date='2025-01-01',
            end_date='2025-06-01',
        )

        form_data = {
            'term': term.id,
            'requested_languages': 'Python, JavaScript',
            'requested_specializations': 'REST, GraphQL',
            'frequency': 'weekly',
            'duration_minutes': 60,
            'requested_start_time': '10:00',
            'requested_start_date': '2025-01-20',
            'notes': 'Looking forward to it!'
        }
        response = self.client.post(self.url, form_data, follow=True)
        self.assertTrue(LessonRequest.objects.exists(), "A LessonRequest should have been created in DB.")
        lesson_request = LessonRequest.objects.first()
        self.assertEqual(lesson_request.student, self.student_profile)
        self.assertEqual(lesson_request.tutor, self.tutor_profile)
