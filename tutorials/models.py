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
    
class Specialization(models.Model):
    """
    A more advanced specialization area a tutor can teach,
    e.g. 'Ruby on Rails Web Development', 'React.js Front-End', etc.
    """
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

class ProgrammingLanguage(models.Model):
    name = models.CharField(max_length=50, unique=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name


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
    languages = models.ManyToManyField(
        ProgrammingLanguage,
        blank=True,
        help_text="Programming languages this tutor can teach."
    )
    specializations = models.ManyToManyField(
        Specialization,
        blank=True,
        help_text="Advanced topics this tutor can teach."
    )

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