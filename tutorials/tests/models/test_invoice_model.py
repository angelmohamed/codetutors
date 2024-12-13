"""Unit tests for the Invoice model."""
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.contrib.auth import get_user_model
from tutorials.models import StudentProfile, Term, Invoice
from datetime import date

from decimal import Decimal

User = get_user_model()

class InvoiceModelTestCase(TestCase):
    """Unit tests for the Invoice model."""

    def setUp(self):
        # Create a student user and profile
        student_user = User.objects.create_user(
            username='@studentmark',
            first_name='Mark',
            last_name='Student',
            email='mark@example.org'
        )
        self.student_profile = StudentProfile.objects.create(user=student_user)

        # Create a term
        self.term = Term.objects.create(
            name="Autumn 2024",
            start_date=date(2024, 9, 1),
            end_date=date(2024, 12, 15)
        )

        # Create an invoice
        self.invoice = Invoice.objects.create(
            student=self.student_profile,
            term=self.term,
            amount=499,
            notes="Invoice for fall term lessons"
        )

    def test_valid_invoice(self):
        self._assert_invoice_is_valid()

    def test_amount_cannot_be_negative(self):
        self.invoice.amount = -100
        self._assert_invoice_is_invalid()

    def test_paid_date_can_be_blank(self):
        self.assertIsNone(self.invoice.paid_date)  # The default is blank
        self._assert_invoice_is_valid()

    def test_str_method_returns_expected_string(self):
        expected_str = f"Invoice for {self.invoice.student.user.full_name()} - {self.term.name}"
        self.assertEqual(str(self.invoice), expected_str)

    def _assert_invoice_is_valid(self):
        try:
            self.invoice.full_clean()
        except ValidationError:
            self.fail('Invoice should be valid.')

    def _assert_invoice_is_invalid(self):
        with self.assertRaises(ValidationError):
            self.invoice.full_clean()
