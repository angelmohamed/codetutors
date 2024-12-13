"""Tests for LessonRequestForm."""
from django.test import TestCase
from datetime import time, date
from tutorials.forms import LessonRequestForm
from tutorials.models import Term

class LessonRequestFormTestCase(TestCase):
    """Test suite for LessonRequestForm."""

    def setUp(self):
        # Create a sample Term for form tests
        self.term = Term.objects.create(
            name="Spring 2025",
            start_date=date(2025, 4, 1),
            end_date=date(2025, 6, 30)
        )

    def test_form_is_valid_with_minimum_data(self):
        form_data = {
            'term': self.term.id,
            'requested_languages': 'Python, Django',
            'requested_specializations': 'REST APIs',
            'frequency': 'weekly',
            'duration_minutes': 60,
            'requested_start_time': '10:00',
            'requested_start_date': '2025-04-10',
            'notes': 'Looking forward to lessons!'
        }
        form = LessonRequestForm(data=form_data)
        self.assertTrue(form.is_valid(), "Form should be valid with the minimum required fields.")

    def test_form_is_invalid_with_blank_languages(self):
        form_data = {
            'term': self.term.id,
            'requested_languages': '',  # Required field
            'requested_specializations': 'REST APIs',
            'frequency': 'weekly',
            'duration_minutes': 60,
            'requested_start_time': '10:00',
            'requested_start_date': '2025-04-10',
            'notes': ''
        }
        form = LessonRequestForm(data=form_data)
        self.assertFalse(form.is_valid(), "Form should be invalid if requested_languages is blank.")

    def test_form_is_invalid_with_negative_duration(self):
        form_data = {
            'term': self.term.id,
            'requested_languages': 'Python',
            'requested_specializations': '',
            'frequency': 'weekly',
            'duration_minutes': -10,
            'requested_start_time': '10:00',
            'requested_start_date': '2025-04-10',
            'notes': ''
        }
        form = LessonRequestForm(data=form_data)
        self.assertFalse(form.is_valid(), "Form should be invalid if duration_minutes is negative.")

    def test_form_is_invalid_with_blank_start_date(self):
        form_data = {
            'term': self.term.id,
            'requested_languages': 'Python',
            'requested_specializations': 'REST APIs',
            'frequency': 'weekly',
            'duration_minutes': 60,
            'requested_start_time': '10:00',
            'requested_start_date': '',  # Required field
            'notes': ''
        }
        form = LessonRequestForm(data=form_data)
        self.assertFalse(form.is_valid(), "Form should be invalid if requested_start_date is blank.")
