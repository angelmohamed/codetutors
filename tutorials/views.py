from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ImproperlyConfigured
from django.db.models import Q
from django.shortcuts import redirect, render
from django.views import View
from django.views.generic.edit import FormView, UpdateView
from django.urls import reverse
from tutorials.forms import LogInForm, PasswordForm, UserForm, SignUpForm
from tutorials.helpers import login_prohibited
from django.views.generic import ListView


from .forms import User, UserForm, TutorProfileForm
from .models import Invoice, User, TutorProfile, Lesson

from datetime import datetime

from datetime import datetime, timedelta

@login_required
def dashboard(request):
    """Display the current user's dashboard."""
    current_user = request.user
    if current_user.is_student:
        # Extract query parameters for tutor search
        q_name = request.GET.get('q_name', '').strip()
        q_language = request.GET.get('q_language', '').strip()
        q_specialization = request.GET.get('q_specialization', '').strip()

        tutors = None
        if q_name or q_language or q_specialization:
            tutors = TutorProfile.objects.select_related('user')
            if q_name:
                tutors = tutors.filter(
                    Q(user__first_name__icontains=q_name) |
                    Q(user__last_name__icontains=q_name) |
                    Q(user__username__icontains=q_name)
                )
            if q_language:
                tutors = tutors.filter(languages__icontains=q_language)
            if q_specialization:
                tutors = tutors.filter(specializations__icontains=q_specialization)

        # Retrieve the student's invoices
        invoices = current_user.student_profile.invoices.select_related('term').all()

        # Fetch lessons for the student
        # Filter by student and select related fields for convenience
        lessons = Lesson.objects.filter(student=current_user.student_profile).select_related('term', 'tutor__user', 'venue')

        # Calculate all upcoming sessions based on frequency (similar to tutor logic)
        upcoming_lessons = []
        today = datetime.now().date()
        for lesson in lessons:
            current_date = lesson.start_date
            while current_date <= lesson.term.end_date:
                if current_date >= today:  # Only future lessons
                    upcoming_lessons.append({
                        'date': current_date,
                        'time': lesson.start_time,
                        'tutor': lesson.tutor.user.full_name,
                        'tutor_email': lesson.tutor.user.email,
                        'venue': lesson.venue.name if lesson.venue else "N/A",
                        'address': lesson.venue.address if lesson.venue else "N/A",
                        'room': lesson.venue.room_number if lesson.venue else "N/A",
                        'frequency': lesson.frequency,
                        'duration': lesson.duration_minutes,
                    })
                # Increment date based on frequency
                increment = timedelta(weeks=2) if lesson.frequency == 'fortnightly' else timedelta(weeks=1)
                current_date += increment

        # Sort all lessons by date and time
        upcoming_lessons = sorted(upcoming_lessons, key=lambda x: (x['date'], x['time']))

        return render(request, 'student_dashboard.html', {
            'user': current_user,
            'tutors': tutors,
            'invoices': invoices,
            'upcoming_lessons': upcoming_lessons
        })
    else:
        # For a tutor, provide both UserForm and TutorProfileForm
        user_form = UserForm(instance=current_user)
        tutor_profile = getattr(current_user, 'tutor_profile', None)
        if not tutor_profile:
            tutor_profile = TutorProfile.objects.create(user=current_user)
        tutor_form = TutorProfileForm(instance=tutor_profile)

        # Fetch lessons for the tutor
        lessons = Lesson.objects.filter(tutor=tutor_profile).select_related('term', 'student__user', 'venue')

        # Calculate all upcoming sessions based on frequency
        upcoming_lessons = []
        today = datetime.now().date()
        for lesson in lessons:
            current_date = lesson.start_date
            while current_date <= lesson.term.end_date:
                if current_date >= today:  # Only include future lessons
                    upcoming_lessons.append({
                        'date': current_date,
                        'time': lesson.start_time,
                        'student': lesson.student.user.full_name,
                        'email': lesson.student.user.email,  # Fetch email through StudentProfile -> User
                        'venue': lesson.venue.name if lesson.venue else "N/A",
                        'address': lesson.venue.address if lesson.venue else "N/A",
                        'room': lesson.venue.room_number if lesson.venue else "N/A",
                    })
                # Increment date based on frequency
                increment = timedelta(weeks=2) if lesson.frequency == 'fortnightly' else timedelta(weeks=1)
                current_date += increment

        # Sort all lessons by date and time
        upcoming_lessons = sorted(upcoming_lessons, key=lambda x: (x['date'], x['time']))

        return render(
            request,
            'tutor_dashboard.html',
            {
                'user': current_user,
                'form': user_form,
                'tutor_form': tutor_form,
                'upcoming_lessons': upcoming_lessons
            }
        )

from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse
from .models import TutorProfile, LessonRequest
from .forms import LessonRequestForm

@login_required
def request_lesson(request, tutor_id):
    """Handle lesson request form."""
    tutor = get_object_or_404(TutorProfile, id=tutor_id)  # Fetch the tutor
    if request.method == 'POST':
        form = LessonRequestForm(request.POST)
        if form.is_valid():
            lesson_request = form.save(commit=False)  # Don't save to the DB yet
            lesson_request.student = request.user.student_profile  # Assign the student
            lesson_request.tutor = tutor  # Assign the tutor
            lesson_request.save()  # Save the lesson request
            form.save_m2m()  # Save many-to-many fields (if any)
            return redirect('dashboard')  # Redirect after successful submission
    else:
        form = LessonRequestForm()  # Empty form for GET request
    
    return render(request, 'request_lesson.html', {
        'tutor': tutor,
        'form': form
    })

@login_prohibited
def home(request):
    """Display the application's start/home screen."""

    return render(request, 'home.html')


class LoginProhibitedMixin:
    """Mixin that redirects when a user is logged in."""

    redirect_when_logged_in_url = None

    def dispatch(self, *args, **kwargs):
        """Redirect when logged in, or dispatch as normal otherwise."""
        if self.request.user.is_authenticated:
            return self.handle_already_logged_in(*args, **kwargs)
        return super().dispatch(*args, **kwargs)

    def handle_already_logged_in(self, *args, **kwargs):
        url = self.get_redirect_when_logged_in_url()
        return redirect(url)

    def get_redirect_when_logged_in_url(self):
        """Returns the url to redirect to when not logged in."""
        if self.redirect_when_logged_in_url is None:
            raise ImproperlyConfigured(
                "LoginProhibitedMixin requires either a value for "
                "'redirect_when_logged_in_url', or an implementation for "
                "'get_redirect_when_logged_in_url()'."
            )
        else:
            return self.redirect_when_logged_in_url

class LogInView(LoginProhibitedMixin, View):
    """Display login screen and handle user login."""

    http_method_names = ['get', 'post']
    redirect_when_logged_in_url = settings.REDIRECT_URL_WHEN_LOGGED_IN

    def get(self, request):
        """Display log in template."""
        self.next = request.GET.get('next') or ''
        return self.render()

    def post(self, request):
        """Handle log in attempt."""
        form = LogInForm(request.POST)
        self.next = request.POST.get('next') or settings.REDIRECT_URL_WHEN_LOGGED_IN
        if form.is_valid():# Ensure form is validated first
            user = form.get_user()
            if user:
                login(request, user)
                return redirect(self.next)
            messages.add_message(request, messages.ERROR, "The credentials provided were invalid!")
        else:
            messages.add_message(request, messages.ERROR, "Invalid input. Please correct the errors below.")
            
        return render(request, 'log_in.html', {'form': form, 'next': self.next})

    def render(self):
        """Render log in template with the given context."""
        form = LogInForm()
        return render(self.request, 'log_in.html', {'form': form, 'next': self.next})


def log_out(request):
    """Log out the current user"""

    logout(request)
    return redirect('home')





class PasswordView(LoginRequiredMixin, FormView):
    """Display password change screen and handle password change requests."""

    template_name = 'password.html'
    form_class = PasswordForm

    def get_form_kwargs(self, **kwargs):
        """Pass the current user to the password change form."""

        kwargs = super().get_form_kwargs(**kwargs)
        kwargs.update({'user': self.request.user})
        return kwargs

    def form_valid(self, form):
        """Handle valid form by saving the new password."""

        form.save()
        login(self.request, self.request.user)
        return super().form_valid(form)

    def get_success_url(self):
        """Redirect the user after successful password change."""

        messages.add_message(self.request, messages.SUCCESS, "Password updated!")
        return reverse('dashboard')


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    """Update user details."""
    model = User
    form_class = UserForm
    template_name = "profile.html"

    def get_object(self):
        return self.request.user

    def get_success_url(self):
        messages.success(self.request, "Profile updated!")
        return reverse('dashboard')

class TutorProfileUpdateView(LoginRequiredMixin, UpdateView):
    """Update tutor profile details."""
    model = TutorProfile
    form_class = TutorProfileForm
    template_name = "tutor_profile.html"

    def get_object(self):
        # Return the current user's tutor profile
        return self.request.user.tutor_profile

    def get_success_url(self):
        messages.success(self.request, "Tutor profile updated!")
        return reverse('dashboard')

class SignUpView(LoginProhibitedMixin, FormView):
    """Display the sign up screen and handle sign ups."""

    form_class = SignUpForm
    template_name = "sign_up.html"
    redirect_when_logged_in_url = settings.REDIRECT_URL_WHEN_LOGGED_IN

    def form_valid(self, form):
        """Handle valid signup by saving the user and logging them in."""
        self.object = form.save()
        login(self.request, self.object)
        return redirect(self.get_success_url())  # Explicitly redirect

    def get_success_url(self):
        """Redirect user to dashboard after signup."""
        return reverse(settings.REDIRECT_URL_WHEN_LOGGED_IN)
    

class InvoiceView(LoginRequiredMixin, ListView):
    """Display invoices for the current user (student)."""
    model = Invoice
    template_name = "invoices.html"
    context_object_name = 'invoices'

    def get_queryset(self):
        """Return the invoices for the current logged-in student's profile."""
        return Invoice.objects.filter(student=self.request.user.student_profile).select_related('term')

    def get_context_data(self, **kwargs):
        """Add additional context such as the student's name and total due amount."""
        context = super().get_context_data(**kwargs)
        student_profile = self.request.user.student_profile
        context['student_name'] = student_profile.user.full_name
        context['total_due'] = sum(invoice.amount_due for invoice in context['invoices'])
        return context

