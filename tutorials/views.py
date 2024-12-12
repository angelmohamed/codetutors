from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ImproperlyConfigured
from django.shortcuts import redirect, render
from django.views import View
from django.views.generic.edit import FormView, UpdateView
from django.urls import reverse
from tutorials.forms import LogInForm, PasswordForm, UserForm, SignUpForm
from tutorials.helpers import login_prohibited

from .forms import User, UserForm, TutorProfileForm
from .models import User, TutorProfile, Lesson

from datetime import datetime

from datetime import datetime, timedelta

@login_required
def dashboard(request):
    """Display the current user's dashboard."""
    current_user = request.user
    if current_user.is_student:
        return render(request, 'student_dashboard.html', {'user': current_user})
    else:
        # For a tutor, provide both UserForm and TutorProfileForm
        user_form = UserForm(instance=current_user)
        tutor_profile = getattr(current_user, 'tutor_profile', None)
        if not tutor_profile:
            tutor_profile = TutorProfile.objects.create(user=current_user)
        tutor_form = TutorProfileForm(instance=tutor_profile)

        # Fetch lessons for the tutor
        lessons = Lesson.objects.filter(tutor=tutor_profile).select_related('term', 'student', 'venue')

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

def tutor_log_in(request):
    """Handle login for tutors."""
    form = LogInForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.get_user()
        if user and user.is_tutor:  # Ensure the user is a tutor
            login(request, user)
            return redirect('dashboard')  # Redirect to tutor dashboard
        else:
            messages.error(request, "Invalid credentials or you are not a tutor.")
    return render(request, 'log_in.html', {'form': form})



def student_log_in(request):
    """Handle login for students."""
    form = LogInForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.get_user()
        if user and user.is_student:
            login(request, user)
            return redirect('dashboard')  # Redirect to student dashboard
        else:
            messages.error(request, "Invalid credentials or you are not a student.")
    return render(request, 'log_in.html', {'form': form})



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
