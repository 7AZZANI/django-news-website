from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from unfold.admin import ModelAdmin
from unfold.decorators import display
from unfold.forms import AdminPasswordChangeForm, UserChangeForm, UserCreationForm

from .models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(BaseUserAdmin, ModelAdmin):
    """
    Styled Custom User Admin utilizing Django Unfold's UI components,
    role-based filtering, and author bio attributes.
    """
    form = UserChangeForm
    add_form = UserCreationForm
    change_password_form = AdminPasswordChangeForm

    list_display = (
        'display_avatar',
        'email',
        'username',
        'get_full_name',
        'display_role',
        'is_staff',
        'date_joined',
    )
    list_display_links = ('email', 'username')
    list_filter = ('role', 'is_staff', 'is_superuser', 'is_active', 'date_joined')
    search_fields = ('email', 'username', 'first_name', 'last_name', 'job_title')
    ordering = ('-date_joined',)

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {
            'fields': (
                'first_name',
                'last_name',
                'username',
                'job_title',
                'bio',
                'avatar',
            )
        }),
        ('Editorial Role & Permissions', {
            'fields': (
                'role',
                'is_active',
                'is_staff',
                'is_superuser',
                'groups',
                'user_permissions',
            )
        }),
        ('Social Links', {
            'classes': ('collapse',),
            'fields': (
                'twitter_handle',
                'linkedin_url',
                'website_url',
            )
        }),
        ('Important Dates', {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'email',
                'username',
                'first_name',
                'last_name',
                'role',
                'password1',
                'password2',
                'is_staff',
                'is_active',
            ),
        }),
    )

    @display(description="Avatar")
    def display_avatar(self, obj):
        url = obj.avatar_url
        return format_html(
            '<img src="{}" class="w-8 h-8 rounded-full object-cover border border-slate-200 dark:border-zinc-700 shadow-sm" alt="Avatar" />',
            url
        )

    @display(description="Role", label={
        'admin': 'danger',
        'editor': 'warning',
        'writer': 'info',
        'reader': 'success',
    })
    def display_role(self, obj):
        return obj.role
