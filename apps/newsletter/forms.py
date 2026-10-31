from django import forms
from .models import NewsletterSubscriber


class NewsletterSubscriptionForm(forms.ModelForm):
    """
    Newsletter email signup form with bot honeypot protection.
    """
    honeypot = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'style': 'display:none !important;', 'tabindex': '-1', 'autocomplete': 'off'}),
        label=''
    )

    class Meta:
        model = NewsletterSubscriber
        fields = ['email']
        widgets = {
            'email': forms.EmailInput(attrs={
                'placeholder': 'Enter your work or personal email...',
                'class': 'w-full px-4 py-3 rounded-lg border border-slate-300 dark:border-zinc-700 bg-white dark:bg-zinc-800 text-slate-900 dark:text-zinc-100 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-600 focus:border-transparent text-sm transition',
                'required': 'required',
            }),
        }

    def clean_honeypot(self):
        val = self.cleaned_data.get('honeypot')
        if val:
            raise forms.ValidationError("Spam bot identified.")
        return val
