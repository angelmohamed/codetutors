"""Unit tests for the Term model."""
from django.core.exceptions import ValidationError
from django.test import TestCase
from tutorials.models import Term
from datetime import date

class TermModelTestCase(TestCase):
    """Unit tests for the Term model."""

    def setUp(self):
        self.term = Term.objects.create(
            name="September-Christmas 2024",
            start_date=date(2024, 9, 1),
            end_date=date(2024, 12, 20)
        )

    def test_valid_term(self):
        self._assert_term_is_valid()

    def test_name_cannot_be_blank(self):
        self.term.name = ''
        self._assert_term_is_invalid()

    def test_name_must_be_unique(self):
        duplicate = Term(
            name="September-Christmas 2024",
            start_date=date(2024, 9, 1),
            end_date=date(2024, 12, 20)
        )
        with self.assertRaises(ValidationError):
            duplicate.full_clean()

    def test_str_method_returns_name(self):
        self.assertEqual(str(self.term), "September-Christmas 2024")

    def test_start_date_before_end_date(self):
        self.term.start_date = date(2024, 12, 21)
        with self.assertRaises(ValidationError):
            self.term.full_clean()

    def _assert_term_is_valid(self):
        try:
            self.term.full_clean()
        except ValidationError:
            self.fail('Term should be valid.')

    def _assert_term_is_invalid(self):
        with self.assertRaises(ValidationError):
            self.term.full_clean()
