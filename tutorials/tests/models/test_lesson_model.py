"""Unit tests for the Lesson model."""
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.contrib.auth import get_user_model
from tutorials.models import (
    StudentProfile, TutorProfile, Term, Venue, Lesson
)
from datetime import date, time

User = get_user_model()

class LessonModelTestCase(TestCase):
    """Unit tests for the Lesson model."""

    def setUp(self):
        # Create a student user and profile
        student_user = User.objects.create_user(
            username='@studentalex',
            first_name='Alex',
            last_name='Student',
            email='alex@example.org'
        )
        self.student_profile = StudentProfile.objects.create(user=student_user)

        # Create a tutor user and profile
        tutor_user = User.objects.create_user(
            username='@tutormary',
            first_name='Mary',
            last_name='Tutor',
            email='mary@example.org'
        )
        self.tutor_profile = TutorProfile.objects.create(user=tutor_user)

        # Create a term
        self.term = Term.objects.create(
            name="Spring 2024",
            start_date=date(2024, 4, 1),
            end_date=date(2024, 6, 30)
        )

        # Create a venue
        self.venue = Venue.objects.create(
            name="Lab 202",
            address="456 College Ave",
            room_number="202",
            capacity=20
        )

        # Create a Lesson
        self.lesson = Lesson.objects.create(
            tutor=self.tutor_profile,
            student=self.student_profile,
            term=self.term,
            venue=self.venue,
            start_date=date(2024, 4, 5),
            start_time=time(14, 30),
            frequency='weekly',
            duration_minutes=60,
            active=True
        )

    def test_valid_lesson(self):
        self._assert_lesson_is_valid()

    def test_str_method_returns_expected_string(self):
        expected_str = (
            f"Lesson: {self.student_profile.user.full_name()} "
            f"with {self.tutor_profile.user.full_name()} "
            f"at {self.venue}"
        )
        self.assertEqual(str(self.lesson), expected_str)

    def test_duration_cannot_be_zero(self):
        self.lesson.duration_minutes = 0
        self._assert_lesson_is_invalid()

    def test_frequency_defaults_to_weekly(self):
        new_lesson = Lesson.objects.create(
            tutor=self.tutor_profile,
            student=self.student_profile,
            term=self.term,
            start_date=date(2024, 4, 10),
            start_time=time(15, 0)
        )
        self.assertEqual(new_lesson.frequency, 'weekly')

    def _assert_lesson_is_valid(self):
        try:
            self.lesson.full_clean()
        except ValidationError:
            self.fail('Lesson should be valid.')

    def _assert_lesson_is_invalid(self):
        with self.assertRaises(ValidationError):
            self.lesson.full_clean()
