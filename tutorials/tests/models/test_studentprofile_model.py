"""Unit tests for the StudentProfile model."""
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.contrib.auth import get_user_model
from tutorials.models import StudentProfile

User = get_user_model()

class StudentProfileModelTestCase(TestCase):
    """Unit tests for the StudentProfile model."""

    def setUp(self):
        # Create a user for the student
        self.student_user = User.objects.create_user(
            username='@studentjane',
            first_name='Jane',
            last_name='Student',
            email='jane@example.org'
        )
        # Create the StudentProfile
        self.student_profile = StudentProfile.objects.create(
            user=self.student_user,
            contact_number="987654321",
            preferred_communication_method="email",
            notes="Looking forward to learning!"
        )

    def test_valid_student_profile(self):
        self._assert_student_profile_is_valid()

    def test_contact_number_can_be_blank(self):
        self.student_profile.contact_number = ''
        self._assert_student_profile_is_valid()

    def test_preferred_communication_method_can_be_blank(self):
        self.student_profile.preferred_communication_method = ''
        self._assert_student_profile_is_valid()

    def test_str_method_returns_expected_string(self):
        expected_str = f"Student: {self.student_user.first_name} {self.student_user.last_name}"
        self.assertEqual(str(self.student_profile), expected_str)

    def _assert_student_profile_is_valid(self):
        try:
            self.student_profile.full_clean()
        except ValidationError:
            self.fail('StudentProfile should be valid.')

    def _assert_student_profile_is_invalid(self):
        with self.assertRaises(ValidationError):
            self.student_profile.full_clean()
