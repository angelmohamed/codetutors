"""Unit tests for the Venue model."""
from django.core.exceptions import ValidationError
from django.test import TestCase
from tutorials.models import Venue

class VenueModelTestCase(TestCase):
    """Unit tests for the Venue model."""

    def setUp(self):
        self.venue = Venue.objects.create(
            name="Room A101",
            address="123 Main Street",
            room_number="A101",
            capacity=30
        )

    def test_valid_venue(self):
        self._assert_venue_is_valid()

    def test_name_cannot_be_blank(self):
        self.venue.name = ''
        self._assert_venue_is_invalid()

    def test_name_can_be_100_characters_long(self):
        self.venue.name = 'x' * 100
        self._assert_venue_is_valid()

    def test_name_cannot_exceed_100_characters(self):
        self.venue.name = 'x' * 101
        self._assert_venue_is_invalid()

    def test_str_method_returns_name(self):
        self.assertEqual(str(self.venue), "Room A101")

    def _assert_venue_is_valid(self):
        try:
            self.venue.full_clean()
        except ValidationError:
            self.fail('Venue should be valid.')

    def _assert_venue_is_invalid(self):
        with self.assertRaises(ValidationError):
            self.venue.full_clean()
