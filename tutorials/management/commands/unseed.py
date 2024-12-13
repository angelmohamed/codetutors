from django.core.management.base import BaseCommand
from tutorials.models import (
    User, Term, Venue, LessonRequest, Lesson, Invoice, TutorProfile, StudentProfile
)
from django.db import transaction


class Command(BaseCommand):
    """Build automation command to unseed the database."""

    help = 'Removes all seeded data from the database'

    def handle(self, *args, **options):
        """Unseed the database."""
        Invoice.objects.all().delete()
        Lesson.objects.all().delete()
        LessonRequest.objects.all().delete()
        TutorProfile.objects.all().delete()
        StudentProfile.objects.all().delete()
        Term.objects.all().delete()
        Venue.objects.all().delete()
        User.objects.all().delete()