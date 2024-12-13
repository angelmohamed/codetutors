"""Tests for home view."""
from django.test import TestCase
from django.urls import reverse

class HomeViewTestCase(TestCase):
    """Test suite for the home view."""

    def setUp(self):
        self.url = reverse('home')

    def test_home_view_renders_correct_template(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'home.html')
