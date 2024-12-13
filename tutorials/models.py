from django.core.validators import RegexValidator
from django.contrib.auth.models import AbstractUser
from django.db import models
from libgravatar import Gravatar

from django.conf import settings

class User(AbstractUser):
    """Model used for user authentication, and team member related information."""

    username = models.CharField(
        max_length=30,
        unique=True,
        validators=[RegexValidator(
            regex=r'^@\w{3,}$',
            message='Username must consist of @ followed by at least three alphanumericals'
        )]
    )
    first_name = models.CharField(max_length=50, blank=False)
    last_name = models.CharField(max_length=50, blank=False)
    email = models.EmailField(unique=True, blank=False)
    is_student = models.BooleanField(default=True)
    is_tutor = models.BooleanField(default=False)

    class Meta:
        """Model options."""

        ordering = ['last_name', 'first_name']

    def full_name(self):
        """Return a string containing the user's full name."""

        return f'{self.first_name} {self.last_name}'

    def gravatar(self, size=120):
        """Return a URL to the user's gravatar."""

        gravatar_object = Gravatar(self.email)
        gravatar_url = gravatar_object.get_image(size=size, default='mp')
        return gravatar_url

    def mini_gravatar(self):
        """Return a URL to a miniature version of the user's gravatar."""
        
        return self.gravatar(size=60)


class TutorProfile(models.Model):
    """
    Additional fields and relationships for a tutor user.
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='tutor_profile'
    )
    bio = models.TextField(blank=True, help_text="Short biography or background.")
    experience_years = models.PositiveIntegerField(default=0, help_text="Number of years of tutoring experience.")
    contact_number = models.CharField(
        max_length=15,
        blank=True,
        help_text="Optional contact number."
    )
    languages = models.TextField(blank=True, help_text="Programming languages this tutor can teach.")
    specializations = models.TextField(blank=True, help_text="Advanced areas this tutor can teach.")

    class Meta:
        verbose_name = 'Tutor Profile'
        verbose_name_plural = 'Tutor Profiles'

    def __str__(self):
        return f"Tutor: {self.user.full_name()}"
    

class StudentProfile(models.Model):
    """
    Additional fields for student users.
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='student_profile'
    )
    contact_number = models.CharField(max_length=15, blank=True)
    preferred_communication_method = models.CharField(
        max_length=20,
        blank=True,
        help_text="e.g. email, phone"
    )
    notes = models.TextField(blank=True, help_text="Additional information about the student.")

    class Meta:
        verbose_name = 'Student Profile'
        verbose_name_plural = 'Student Profiles'

    def __str__(self):
        return f"Student: {self.user.full_name()}"

class Term(models.Model):
    """
    Represents a term in the academic year, e.g. 'September-Christmas 2024'.
    """
    name = models.CharField(max_length=100, unique=True)
    start_date = models.DateField()
    end_date = models.DateField()

    class Meta:
        ordering = ['start_date']

    def __str__(self):
        return self.name
    
class Venue(models.Model):
    """
    Represents a location for lessons. This might be a classroom, office, or even a Zoom link.
    """
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=255, blank=True)
    room_number = models.CharField(max_length=50, blank=True)
    capacity = models.PositiveIntegerField(null=True, blank=True, help_text="Optional")

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name
    
class LessonRequest(models.Model):
    """
    Represents a request from a student for lessons in a given term.
    These requests will be manually handled by the admin team.
    """
    FREQUENCY_CHOICES = [
        ('weekly', 'Weekly'),
        ('fortnightly', 'Every other week'),
    ]

    student = models.ForeignKey(
        StudentProfile,
        on_delete=models.CASCADE,
        related_name='lesson_requests'
    )
    tutor = models.ForeignKey(
        TutorProfile,
        on_delete=models.CASCADE,
        default=None,
        related_name='lesson_requests'
    )
    term = models.ForeignKey(
        Term,
        on_delete=models.CASCADE,
        related_name='lesson_requests'
    )
    requested_languages = models.TextField(blank=True, help_text="Programming languages the student wants to learn.")

    requested_specializations = models.TextField(blank=True, help_text="Advanced topics the student wants to focus on.")

    frequency = models.CharField(
        max_length=20,
        choices=FREQUENCY_CHOICES,
        default='weekly'
    )
    duration_minutes = models.PositiveIntegerField(
        default=60,
        help_text="Duration of each lesson in minutes"
    )
    requested_start_date = models.DateField(
        null=True,
        blank=False,
        help_text="Preferred start date for the lesson"
    )
    requested_start_time = models.TimeField(
        help_text="Preferred start time for the lesson"
    )
    requested_venue = models.ForeignKey(
        Venue,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='requested_lessons',
        help_text="Preferred venue for the lessons (if any)."
    )
    # No strict enforcement of deadlines: admin can still accept late requests.
    status = models.CharField(
        max_length=20,
        choices=[('pending', 'Pending'), ('allocated', 'Allocated'), ('rejected', 'Rejected')],
        default='pending',
        help_text="The status of the request. Admin sets this manually."
    )
    notes = models.TextField(
        blank=True,
        help_text="Additional notes from the student."
    )

    def __str__(self):
        return f"Request by {self.student} for {self.term}"


class Lesson(models.Model):
    """
    Represents a scheduled lesson in a given term.
    Lessons are typically created by the admin team based on requests.
    They are not automatically generated.
    """
    FREQUENCY_CHOICES = [
        ('weekly', 'Weekly'),
        ('fortnightly', 'Every other week'),
    ]

    # This can reference the original request if relevant, but it's optional.
    request = models.ForeignKey(
        LessonRequest,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='lessons',
        help_text="The original request that led to this lesson, if any."
    )
    tutor = models.ForeignKey(
        TutorProfile,
        on_delete=models.CASCADE,
        related_name='lessons'
    )
    student = models.ForeignKey(
        StudentProfile,
        on_delete=models.CASCADE,
        related_name='lessons'
    )
    term = models.ForeignKey(
        Term,
        on_delete=models.CASCADE,
        related_name='lessons'
    )
    venue = models.ForeignKey(
        Venue,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='lessons'
    )
    start_date = models.DateField(help_text="First date of this lesson in the term.")
    start_time = models.TimeField(help_text="Start time of the lesson.")
    frequency = models.CharField(
        max_length=20,
        choices=FREQUENCY_CHOICES,
        default='weekly',
        help_text="How often the lesson occurs."
    )
    duration_minutes = models.PositiveIntegerField(
        default=60,
        help_text="Duration of each lesson in minutes."
    )
    active = models.BooleanField(
        default=True,
        help_text="Whether the lesson is currently active this term."
    )
    notes = models.TextField(
        blank=True,
        help_text="Additional notes for this lesson (e.g., cancellations, changes)."
    )

    def __str__(self):
        return f"Lesson: {self.student.user.full_name()} with {self.tutor.user.full_name()} at {self.venue}"


class Invoice(models.Model):
    """
    Represents an invoice for a term's lessons for a given student.
    Payments are handled via bank transfer externally.
    """
    student = models.ForeignKey(
        StudentProfile,
        on_delete=models.CASCADE,
        related_name='invoices'
    )
    term = models.ForeignKey(
        Term,
        on_delete=models.CASCADE,
        related_name='invoices'
    )
    amount = models.DecimalField(max_digits=8, decimal_places=2)
    issued_date = models.DateField(auto_now_add=True)
    paid_date = models.DateField(
        null=True,
        blank=True,
        help_text="Date the invoice was paid. Left blank if not yet paid."
    )
    notes = models.TextField(
        blank=True,
        help_text="Additional notes regarding the invoice."
    )

    class Meta:
        ordering = ['-issued_date']

    def __str__(self):
        return f"Invoice for {self.student.user.full_name()} - {self.term.name}"