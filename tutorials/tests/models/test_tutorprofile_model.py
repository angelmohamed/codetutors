"""Unit tests for the TutorProfile model."""
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.contrib.auth import get_user_model
from tutorials.models import TutorProfile

User = get_user_model()

class TutorProfileModelTestCase(TestCase):
    """Unit tests for the TutorProfile model."""

    def setUp(self):
        # Create a user for the tutor
        self.tutor_user = User.objects.create_user(
            username='@tutorsam',
            first_name='Sam',
            last_name='Tutor',
            email='sam@example.org'
        )
        # Create the TutorProfile
        self.tutor_profile = TutorProfile.objects.create(
            user=self.tutor_user,
            bio="I love teaching Python",
            experience_years=5,
            contact_number="1234567890",
            languages="Python, JavaScript",
            specializations="Machine Learning, Django"
        )

    def test_valid_tutor_profile(self):
        self._assert_tutor_profile_is_valid()

    def test_bio_can_be_blank(self):
        self.tutor_profile.bio = ''
        self._assert_tutor_profile_is_valid()

    def test_experience_years_cannot_be_negative(self):
        self.tutor_profile.experience_years = -1
        self._assert_tutor_profile_is_invalid()

    def test_contact_number_can_be_blank(self):
        self.tutor_profile.contact_number = ''
        self._assert_tutor_profile_is_valid()

    def test_str_method_returns_expected_string(self):
        expected_str = f"Tutor: {self.tutor_user.first_name} {self.tutor_user.last_name}"
        self.assertEqual(str(self.tutor_profile), expected_str)

    def _assert_tutor_profile_is_valid(self):
        try:
            self.tutor_profile.full_clean()
        except ValidationError:
            self.fail('TutorProfile should be valid.')

    def _assert_tutor_profile_is_invalid(self):
        with self.assertRaises(ValidationError):
            self.tutor_profile.full_clean()
