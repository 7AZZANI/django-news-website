from django import forms
from .models import Comment, Category


class CommentForm(forms.ModelForm):
    """
    Reader comment submission form supporting anonymous guests and
    logged-in subscribers, with anti-bot honeypot and clean Tailwind styling.
    """
    honeypot = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'style': 'display:none !important;', 'tabindex': '-1', 'autocomplete': 'off'}),
        label=''
    )

    class Meta:
        model = Comment
        fields = ['name', 'email', 'content']
        widgets = {
            'name': forms.TextInput(attrs={
                'placeholder': 'Your Full Name',
                'class': 'w-full px-4 py-2.5 rounded-lg border border-slate-300 dark:border-zinc-700 bg-white dark:bg-zinc-800 text-slate-900 dark:text-zinc-100 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-600 focus:border-transparent text-sm transition',
            }),
            'email': forms.EmailInput(attrs={
                'placeholder': 'Your Email (will not be published)',
                'class': 'w-full px-4 py-2.5 rounded-lg border border-slate-300 dark:border-zinc-700 bg-white dark:bg-zinc-800 text-slate-900 dark:text-zinc-100 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-600 focus:border-transparent text-sm transition',
            }),
            'content': forms.Textarea(attrs={
                'placeholder': 'Join the discussion with thoughtful, respectful commentary...',
                'rows': 4,
                'class': 'w-full px-4 py-3 rounded-lg border border-slate-300 dark:border-zinc-700 bg-white dark:bg-zinc-800 text-slate-900 dark:text-zinc-100 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-600 focus:border-transparent text-sm transition resize-y',
            }),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        # If user is authenticated, name and email are not mandatory from the form
        if self.user and self.user.is_authenticated:
            self.fields['name'].required = False
            self.fields['email'].required = False
        else:
            self.fields['name'].required = True
            self.fields['email'].required = True

    def clean_honeypot(self):
        value = self.cleaned_data.get('honeypot')
        if value:
            raise forms.ValidationError("Spam detection triggered.")
        return value


class SearchFilterForm(forms.Form):
    """
    Search and multi-faceted filtering for articles.
    """
    DATE_CHOICES = (
        ('', 'Any Time'),
        ('today', 'Past 24 Hours'),
        ('week', 'Past Week'),
        ('month', 'Past Month'),
        ('year', 'Past Year'),
    )

    SORT_CHOICES = (
        ('latest', 'Most Recent'),
        ('popular', 'Most Read'),
        ('relevance', 'Best Match'),
    )

    q = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'Search headlines, topics, keywords...',
            'class': 'w-full px-4 py-3 pl-11 rounded-xl border border-slate-300 dark:border-zinc-700 bg-white dark:bg-zinc-800 text-slate-900 dark:text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-600 text-sm shadow-sm transition',
        })
    )
    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        required=False,
        empty_label='All Categories',
        widget=forms.Select(attrs={
            'class': 'w-full px-3 py-2.5 rounded-lg border border-slate-300 dark:border-zinc-700 bg-white dark:bg-zinc-800 text-slate-900 dark:text-white text-sm focus:outline-none focus:ring-2 focus:ring-blue-600 transition',
        })
    )
    tag = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'Filter by tag...',
            'class': 'w-full px-3 py-2.5 rounded-lg border border-slate-300 dark:border-zinc-700 bg-white dark:bg-zinc-800 text-slate-900 dark:text-white text-sm focus:outline-none focus:ring-2 focus:ring-blue-600 transition',
        })
    )
    date_range = forms.ChoiceField(
        choices=DATE_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'w-full px-3 py-2.5 rounded-lg border border-slate-300 dark:border-zinc-700 bg-white dark:bg-zinc-800 text-slate-900 dark:text-white text-sm focus:outline-none focus:ring-2 focus:ring-blue-600 transition',
        })
    )
    sort_by = forms.ChoiceField(
        choices=SORT_CHOICES,
        required=False,
        initial='latest',
        widget=forms.Select(attrs={
            'class': 'w-full px-3 py-2.5 rounded-lg border border-slate-300 dark:border-zinc-700 bg-white dark:bg-zinc-800 text-slate-900 dark:text-white text-sm focus:outline-none focus:ring-2 focus:ring-blue-600 transition',
        })
    )
