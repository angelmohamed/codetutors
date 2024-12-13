from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group, Permission
from django.db.models import Q

from .models import (
    User,
    TutorProfile,
    StudentProfile,
    Term,
    Venue,
    LessonRequest,
    Lesson,
    Invoice
)


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'is_superuser')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    list_filter = ('is_staff', 'is_active', 'is_superuser')
    ordering = ('last_name', 'first_name', 'username')

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email')}),
        ('Permissions', {'fields': (
            'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'
        )}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )

    def save_model(self, request, obj, form, change):
        """
        Automatically assign model permissions to staff members if they are staff but not superusers.
        """
        super().save_model(request, obj, form, change)
        if obj.is_staff and not obj.is_superuser:
            from django.contrib.auth.models import Permission
            from django.contrib.contenttypes.models import ContentType

            tutorials_permissions = Permission.objects.filter(content_type__app_label='tutorials')
            obj.user_permissions.set(tutorials_permissions)
            obj.save()



@admin.register(TutorProfile)
class TutorProfileAdmin(admin.ModelAdmin):
    list_display = ('user_full_name', 'experience_years', 'contact_number')
    search_fields = ('user__first_name', 'user__last_name', 'contact_number')
    list_filter = ('experience_years', 'languages', 'specializations')

    def user_full_name(self, obj):
        return obj.user.full_name()
    user_full_name.short_description = 'Tutor Name'


@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ('user_full_name', 'contact_number', 'preferred_communication_method')
    search_fields = ('user__first_name', 'user__last_name', 'contact_number')
    list_filter = ('preferred_communication_method',)

    def user_full_name(self, obj):
        return obj.user.full_name()
    user_full_name.short_description = 'Student Name'


@admin.register(Term)
class TermAdmin(admin.ModelAdmin):
    list_display = ('name', 'start_date', 'end_date')
    list_filter = ('start_date', 'end_date')
    search_fields = ('name',)


@admin.register(Venue)
class VenueAdmin(admin.ModelAdmin):
    list_display = ('name', 'address', 'room_number', 'capacity')
    search_fields = ('name', 'address', 'room_number')


@admin.register(LessonRequest)
class LessonRequestAdmin(admin.ModelAdmin):
    list_display = ('student_name', 'term', 'frequency', 'status', 'requested_start_time')
    list_filter = ('term', 'status', 'frequency')
    search_fields = ('student__user__first_name', 'student__user__last_name', 'notes')

    def student_name(self, obj):
        return obj.student.user.full_name()
    student_name.short_description = 'Student'


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ('student_name', 'tutor_name', 'term', 'venue', 'start_date', 'start_time', 'frequency', 'active')
    list_filter = ('term', 'frequency', 'active')
    search_fields = (
        'student__user__first_name', 'student__user__last_name',
        'tutor__user__first_name', 'tutor__user__last_name',
        'notes'
    )

    def student_name(self, obj):
        return obj.student.user.full_name()
    student_name.short_description = 'Student'

    def tutor_name(self, obj):
        return obj.tutor.user.full_name()
    tutor_name.short_description = 'Tutor'


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('student_name', 'term', 'amount', 'issued_date', 'paid_date')
    list_filter = ('term', 'issued_date', 'paid_date')
    search_fields = (
        'student__user__first_name', 'student__user__last_name',
    )

    def student_name(self, obj):
        return obj.student.user.full_name()
    student_name.short_description = 'Student'
