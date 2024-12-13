"""Tests for TutorProfileForm."""
from django.test import TestCase
from django.contrib.auth import get_user_model
from tutorials.forms import TutorProfileForm
from tutorials.models import TutorProfile

User = get_user_model()

class TutorProfileFormTestCase(TestCase):
    """Test suite for TutorProfileForm."""

    def setUp(self):
        # Create a user for the tutor
        self.tutor_user = User.objects.create_user(
            username='@tutor',
            first_name='Tutor',
            last_name='User',
            email='tutor@example.com',
            password='TutorPassword123',
            is_tutor=True
        )
        self.tutor_profile = TutorProfile.objects.create(
            user=self.tutor_user,
            bio="Experienced Python tutor",
            experience_years=5,
            contact_number="1234567890",
            languages="Python, JavaScript",
            specializations="Machine Learning"
        )

    def test_form_valid_data(self):
        form_data = {
            'bio': 'New Bio',
            'experience_years': 3,
            'contact_number': '5555555555',
            'languages': 'Ruby, Go',
            'specializations': 'Rails, Docker'
        }
        form = TutorProfileForm(data=form_data, instance=self.tutor_profile)
        self.assertTrue(form.is_valid(), "Form should be valid with correct data.")
        updated_profile = form.save()
        self.assertEqual(updated_profile.bio, 'New Bio')
        self.assertEqual(updated_profile.experience_years, 3)
        self.assertEqual(updated_profile.contact_number, '5555555555')
        self.assertEqual(updated_profile.languages, 'Ruby, Go')
        self.assertEqual(updated_profile.specializations, 'Rails, Docker')

    def test_form_invalid_without_languages(self):
        form_data = {
            'bio': 'Missing languages',
            'experience_years': 2,
            'contact_number': '',
            'languages': '',  # Required
            'specializations': 'Machine Learning'
        }
        form = TutorProfileForm(data=form_data, instance=self.tutor_profile)
        self.assertFalse(form.is_valid(), "TutorProfileForm should be invalid without languages field populated.")
