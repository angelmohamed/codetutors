"""Forms for the tutorials app."""
from django import forms
from django.contrib.auth import authenticate
from django.core.validators import RegexValidator
from .models import User, StudentProfile, TutorProfile, LessonRequest, Term
from django.core.exceptions import ValidationError

class LogInForm(forms.Form):
    """Form enabling registered users to log in."""

    username = forms.CharField(label="Username")
    password = forms.CharField(label="Password", widget=forms.PasswordInput())

    def clean(self):
        """Authenticate the user and raise validation errors if login fails."""
        cleaned_data = super().clean()
        username = cleaned_data.get('username')
        password = cleaned_data.get('password')

        if username and password:
            # Authenticate the user
            user = authenticate(username=username, password=password)
            if user is None:
                raise forms.ValidationError('Invalid username or password.')
            if not user.is_active:
                raise forms.ValidationError('This account is inactive.')
            # Store the user object for later use
            cleaned_data['user'] = user
        return cleaned_data

    def get_user(self):
        """Returns authenticated user if possible."""
        return self.cleaned_data.get('user')
    # forms.py

class LessonRequestForm(forms.ModelForm):
    """Form for students to request a lesson."""

    term = forms.ModelChoiceField(
        queryset=Term.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=True
    )
    requested_languages = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Programming languages'}),
        required=True
    )
    requested_specializations = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Specializations'}),
        required=False
    )
    frequency = forms.ChoiceField(
        choices=LessonRequest.FREQUENCY_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=True
    )
    duration_minutes = forms.IntegerField(
        widget=forms.NumberInput(
            attrs={'class': 'form-control', 'placeholder': 'Duration in minutes'}
        ),
        required=True
    )
    requested_start_time = forms.TimeField(
        widget=forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
        required=True
    )
    # New date field:
    requested_start_date = forms.DateField(
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        required=True
    )
    notes = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Additional notes'}),
        required=False
    )

    class Meta:
        model = LessonRequest
        fields = ['term', 'requested_languages', 'requested_specializations', 'frequency', 'duration_minutes', 'requested_start_time', 'requested_start_date', 'notes']

class UserForm(forms.ModelForm):
    """Form to update user profiles."""
    first_name = forms.CharField(
        label='First Name',
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'First name'
            }
        ),
        required=True
    )
    last_name = forms.CharField(
        label='Last Name',
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Last name'
            }
        ),
        required=True
    )
    username = forms.CharField(
        label='Username',
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Username'
            }
        ),
        required=True
    )
    email = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Email'
            }
        ),
        required=True
    )

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email']

class TutorProfileForm(forms.ModelForm):
    """Form to update tutor profile details."""
    
    bio = forms.CharField(
        label='Biography',
        widget=forms.Textarea(
            attrs={
                'class': 'form-control',
                'placeholder': 'Short biography or background.'
            }
        ),
        required=True
    )
    experience_years = forms.IntegerField(
        label='Experience',
        widget=forms.NumberInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Number of years tutoring'
            }
        ),
        required=True
    )
    contact_number = forms.CharField(
        label='Contact number',
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Optional contact number'
            }
        ),
        required=False
    )
    languages = forms.CharField(
        label='Languages',
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Programming languages this tutor can teach'
            }
        ),
        required=True
    )
    specializations = forms.CharField(
        label='Specializations',
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Advanced topics this tutor can teach'
            }
        ),
        required=False
    )
    
    class Meta:
        model = TutorProfile
        fields = ['bio', 'experience_years', 'contact_number', 'languages', 'specializations']

class NewPasswordMixin(forms.Form):
    """Form mixing for new_password and password_confirmation fields."""

    new_password = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(),
        validators=[RegexValidator(
            regex=r'^(?=.*[A-Z])(?=.*[a-z])(?=.*[0-9]).*$',
            message='Password must contain an uppercase character, a lowercase '
                    'character and a number'
            )]
    )
    password_confirmation = forms.CharField(label='Password confirmation', widget=forms.PasswordInput())

    def clean(self):
        """Form mixing for new_password and password_confirmation fields."""

        super().clean()
        new_password = self.cleaned_data.get('new_password')
        password_confirmation = self.cleaned_data.get('password_confirmation')
        if new_password != password_confirmation:
            self.add_error('password_confirmation', 'Confirmation does not match password.')


class PasswordForm(NewPasswordMixin):
    """Form enabling users to change their password."""

    password = forms.CharField(label='Current password', widget=forms.PasswordInput())

    def __init__(self, user=None, **kwargs):
        """Construct new form instance with a user instance."""
        
        super().__init__(**kwargs)
        self.user = user

    def clean(self):
        """Clean the data and generate messages for any errors."""

        super().clean()
        password = self.cleaned_data.get('password')
        if self.user is not None:
            user = authenticate(username=self.user.username, password=password)
        else:
            user = None
        if user is None:
            self.add_error('password', "Password is invalid")

    def save(self):
        """Save the user's new password."""

        new_password = self.cleaned_data['new_password']
        if self.user is not None:
            self.user.set_password(new_password)
            self.user.save()
        return self.user


class SignUpForm(forms.ModelForm):
    """Form enabling unregistered users to sign up as either a student or tutor."""

    USER_TYPE_CHOICES = [
        ('student', 'Student'),
        ('tutor', 'Tutor'),
    ]
    user_type = forms.ChoiceField(
        choices=USER_TYPE_CHOICES,
        required=True,
        help_text="Select whether you are signing up as a student or a tutor."
    )
    new_password = forms.CharField(
        widget=forms.PasswordInput,
        label="Password",
        required=True
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput,
        label="Confirm Password",
        required=True
    )

    class Meta:
        """Form options."""
        model = User
        fields = ['first_name', 'last_name', 'username', 'email']

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('new_password')
        confirm = cleaned_data.get('confirm_password')
        if password and confirm and password != confirm:
            self.add_error('confirm_password', "Passwords do not match.")
        return cleaned_data

    def save(self, commit=True):
        """Create a new user and their corresponding profile."""
        user_type = self.cleaned_data.get('user_type')
        is_student = True if user_type == 'student' else False
        is_tutor = not is_student 

        print(user_type, is_student, is_tutor)

        user = User.objects.create_user(
            username=self.cleaned_data.get('username'),
            first_name=self.cleaned_data.get('first_name'),
            last_name=self.cleaned_data.get('last_name'),
            email=self.cleaned_data.get('email'),
            password=self.cleaned_data.get('new_password'),
        )
        
        user.is_student = is_student
        user.is_tutor = is_tutor 
        if commit:
            user.save()

        if is_student:
            StudentProfile.objects.create(user=user)
        else:
            TutorProfile.objects.create(user=user)

        return user