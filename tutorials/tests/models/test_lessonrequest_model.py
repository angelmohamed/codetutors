"""Unit tests for the LessonRequest model."""
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.contrib.auth import get_user_model
from tutorials.models import (
    StudentProfile, TutorProfile, Term, Venue, LessonRequest
)
from datetime import date, time

User = get_user_model()

class LessonRequestModelTestCase(TestCase):
    """Unit tests for the LessonRequest model."""

    def setUp(self):
        # Create a student user and profile
        student_user = User.objects.create_user(
            username='@studentamy',
            first_name='Amy',
            last_name='Student',
            email='amy@example.org'
        )
        self.student_profile = StudentProfile.objects.create(user=student_user)

        # Create a tutor user and profile
        tutor_user = User.objects.create_user(
            username='@tutorbob',
            first_name='Bob',
            last_name='Tutor',
            email='bob@example.org'
        )
        self.tutor_profile = TutorProfile.objects.create(user=tutor_user)

        # Create a term
        self.term = Term.objects.create(
            name="Winter 2024",
            start_date=date(2024, 1, 10),
            end_date=date(2024, 3, 20)
        )

        # Create a venue
        self.venue = Venue.objects.create(
            name="Room A101",
            address="123 Main Street",
            room_number="A101"
        )

        # Create a LessonRequest
        self.request = LessonRequest.objects.create(
            student=self.student_profile,
            tutor=self.tutor_profile,
            term=self.term,
            requested_languages="Python, JavaScript",
            requested_specializations="Django REST Framework",
            frequency='weekly',
            duration_minutes=60,
            requested_start_date=date(2024, 1, 15),
            requested_start_time=time(10, 0),
            requested_venue=self.venue,
            status='pending',
            notes="Some notes"
        )

    def test_valid_lesson_request(self):
        self._assert_request_is_valid()

    def test_status_default_is_pending(self):
        new_request = LessonRequest.objects.create(
            student=self.student_profile,
            tutor=self.tutor_profile,
            term=self.term,
            requested_start_date=date(2024, 2, 1),
            requested_start_time=time(9, 30)
        )
        self.assertEqual(new_request.status, 'pending')

    def test_duration_cannot_be_zero(self):
        self.request.duration_minutes = 0
        self._assert_request_is_invalid()

    def test_str_method_returns_expected_string(self):
        expected_str = f"Request by {self.request.student} for {self.request.term}"
        self.assertEqual(str(self.request), expected_str)

    def _assert_request_is_valid(self):
        try:
            self.request.full_clean()
        except ValidationError:
            self.fail('LessonRequest should be valid.')

    def _assert_request_is_invalid(self):
        with self.assertRaises(ValidationError):
            self.request.full_clean()
