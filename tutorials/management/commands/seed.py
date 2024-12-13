from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
import logging
from tutorials.models import User, Term, Venue, LessonRequest, Lesson, Invoice, TutorProfile, StudentProfile
import pytz
from faker import Faker
from datetime import date, time

user_fixtures = [
    {'username': '@johndoe', 'email': 'john.doe@example.org', 'first_name': 'John', 'last_name': 'Doe', 'is_student': False, 'is_staff': True,'is_superuser': True},
    {'username': '@janedoe', 'email': 'jane.doe@example.org', 'first_name': 'Jane', 'last_name': 'Doe', 'is_student': False, 'is_tutor': True},
    {'username': '@charlie', 'email': 'charlie.johnson@example.org', 'first_name': 'Charlie', 'last_name': 'Johnson', 'is_student': True},
]

logging.basicConfig(level=logging.DEBUG)

class Command(BaseCommand):
    """Build automation command to seed the database."""

    USER_COUNT = 10
    DEFAULT_PASSWORD = 'Password123'
    help = 'Seeds the database with sample data'

    def __init__(self):
        self.faker = Faker('en_GB')

    def handle(self, *args, **options):
        self.create_users()
        self.create_profiles()
        self.create_fixtures()

    def create_users(self):
        for data in user_fixtures:
            self.try_create_user(data)

    def create_profiles(self):
        jane = User.objects.get(username='@janedoe')
        TutorProfile.objects.create(user=jane, bio="Experienced tutor", experience_years=5)

        charlie = User.objects.get(username='@charlie')
        StudentProfile.objects.create(user=charlie, notes="Eager to learn programming.")

    def create_fixtures(self):
        term = Term.objects.create(name="Spring 2026", start_date=date(2026, 3, 1), end_date=date(2026, 6, 1))
        venue = Venue.objects.create(name="Main Hall", address="123 Learning Lane")

        charlie = StudentProfile.objects.get(user__username='@charlie')
        jane = TutorProfile.objects.get(user__username='@janedoe')

        jane.languages = 'Python, JavaScript'
        jane.specializations = 'Web Development'
        jane.contact_number = '+44 1234 567890'
        jane.save()

        # Create LessonRequest
        lesson_request = LessonRequest.objects.create(
            student=charlie,
            tutor=jane,
            term=term,
            requested_languages="Python, JavaScript",
            requested_specializations="Web Development",
            frequency="weekly",
            duration_minutes=60,
            requested_start_date=date(2026, 3, 10),
            requested_start_time=time(10, 0),
            requested_venue=venue,
            notes="Looking to build foundational skills."
        )

        # Create Lesson
        lesson = Lesson.objects.create(
            request=lesson_request,
            tutor=jane,
            student=charlie,
            term=term,
            venue=venue,
            start_date=date(2024, 3, 10),
            start_time=time(10, 0),
            frequency="weekly",
            duration_minutes=60,
            active=True,
            notes="Initial lesson for basics."
        )

        # Create Invoice
        invoice = Invoice.objects.create(
            student=charlie,
            term=term,
            amount=200.00,
            notes="Invoice for weekly lessons in Spring 2024."
        )

    def try_create_user(self, data):
        try:
            self.create_user(data)
        except Exception as e:
            logging.error(f"Error creating user: {e}")

    def create_user(self, data):
        logging.debug(f"Creating user with data: {data}")
        try:
            with transaction.atomic():
                User.objects.create_user(
                    username=data['username'],
                    email=data['email'],
                    password=Command.DEFAULT_PASSWORD,
                    first_name=data['first_name'],
                    last_name=data['last_name'],
                    is_student=data.get('is_student', False),
                    is_tutor=data.get('is_tutor', False),
                    is_staff=data.get('is_staff', False),
                    is_superuser=data.get('is_superuser', False)
                )
            logging.debug("User created successfully")
        except Exception as e:
            logging.error(f"Error creating user: {e}")
