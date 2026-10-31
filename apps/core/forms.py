from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.forms import AuthenticationForm
from .models import CustomUser


class UserRegistrationForm(forms.ModelForm):
    """
    Reader registration form with email, name, and password confirmation.
    """
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Create a secure password',
            'class': 'w-full px-4 py-2.5 rounded-lg border border-slate-300 dark:border-zinc-700 bg-white dark:bg-zinc-800 text-slate-900 dark:text-zinc-100 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-600 text-sm transition',
        })
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Confirm your password',
            'class': 'w-full px-4 py-2.5 rounded-lg border border-slate-300 dark:border-zinc-700 bg-white dark:bg-zinc-800 text-slate-900 dark:text-zinc-100 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-600 text-sm transition',
        })
    )

    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'username', 'email']
        widgets = {
            'first_name': forms.TextInput(attrs={
                'placeholder': 'First name',
                'class': 'w-full px-4 py-2.5 rounded-lg border border-slate-300 dark:border-zinc-700 bg-white dark:bg-zinc-800 text-slate-900 dark:text-zinc-100 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-600 text-sm transition',
            }),
            'last_name': forms.TextInput(attrs={
                'placeholder': 'Last name',
                'class': 'w-full px-4 py-2.5 rounded-lg border border-slate-300 dark:border-zinc-700 bg-white dark:bg-zinc-800 text-slate-900 dark:text-zinc-100 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-600 text-sm transition',
            }),
            'username': forms.TextInput(attrs={
                'placeholder': 'Choose a unique username',
                'class': 'w-full px-4 py-2.5 rounded-lg border border-slate-300 dark:border-zinc-700 bg-white dark:bg-zinc-800 text-slate-900 dark:text-zinc-100 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-600 text-sm transition',
            }),
            'email': forms.EmailInput(attrs={
                'placeholder': 'name@example.com',
                'class': 'w-full px-4 py-2.5 rounded-lg border border-slate-300 dark:border-zinc-700 bg-white dark:bg-zinc-800 text-slate-900 dark:text-zinc-100 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-600 text-sm transition',
            }),
        }

    def clean_confirm_password(self):
        pwd = self.cleaned_data.get('password')
        pwd_confirm = self.cleaned_data.get('confirm_password')
        if pwd and pwd_confirm and pwd != pwd_confirm:
            raise forms.ValidationError("Passwords do not match.")
        return pwd_confirm

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        user.role = CustomUser.ROLE_READER
        if commit:
            user.save()
        return user


class EmailAuthenticationForm(forms.Form):
    """
    Custom email authentication form matching modern editorial UI standards.
    """
    username = forms.EmailField(
        label='Email Address',
        widget=forms.EmailInput(attrs={
            'placeholder': 'Enter your registered email',
            'class': 'w-full px-4 py-2.5 rounded-lg border border-slate-300 dark:border-zinc-700 bg-white dark:bg-zinc-800 text-slate-900 dark:text-zinc-100 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-600 text-sm transition',
            'autocomplete': 'email',
        })
    )
    password = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Enter your password',
            'class': 'w-full px-4 py-2.5 rounded-lg border border-slate-300 dark:border-zinc-700 bg-white dark:bg-zinc-800 text-slate-900 dark:text-zinc-100 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-600 text-sm transition',
            'autocomplete': 'current-password',
        })
    )

    def __init__(self, request=None, *args, **kwargs):
        self.request = request
        self.user_cache = None
        super().__init__(*args, **kwargs)

    def clean(self):
        email = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if email and password:
            self.user_cache = authenticate(self.request, username=email, password=password)
            if self.user_cache is None:
                raise forms.ValidationError("Invalid email address or password.")
            elif not self.user_cache.is_active:
                raise forms.ValidationError("This account is currently deactivated.")
        return self.cleaned_data

    def get_user(self):
        return self.user_cache
