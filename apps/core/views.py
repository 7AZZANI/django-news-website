from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.views import LoginView as BaseLoginView
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView, TemplateView

from .forms import EmailAuthenticationForm, UserRegistrationForm


class UserLoginView(BaseLoginView):
    """
    Login view styled with modern editorial dark/light mode aesthetics.
    """
    form_class = EmailAuthenticationForm
    template_name = 'registration/login.html'
    redirect_authenticated_user = True


class UserRegisterView(CreateView):
    """
    Reader registration view.
    """
    form_class = UserRegistrationForm
    template_name = 'registration/register.html'
    success_url = reverse_lazy('login')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, "Account created successfully! You can now sign in.")
        return response


class UserLogoutView(View):
    """
    Logs out the user and redirects to homepage.
    """
    def post(self, request):
        logout(request)
        return redirect('articles:home')

    def get(self, request):
        logout(request)
        return redirect('articles:home')


# Editorial & Trust Information Views
class AboutView(TemplateView):
    template_name = 'core/about.html'


class EthicsView(TemplateView):
    template_name = 'core/ethics.html'


class PrivacyPolicyView(TemplateView):
    template_name = 'core/privacy.html'


class TermsOfServiceView(TemplateView):
    template_name = 'core/terms.html'


class ContactView(View):
    template_name = 'core/contact.html'

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        subject = request.POST.get('subject', '').strip()
        message = request.POST.get('message', '').strip()
        honeypot = request.POST.get('honeypot', '').strip()

        if honeypot:
            return redirect('core:contact')

        if not name or not email or not message:
            messages.error(request, "Please fill in all required fields.")
            return render(request, self.template_name)

        messages.success(
            request,
            "Thank you for reaching out to The Chronicle newsroom. An editor or desk correspondent will review your inquiry shortly."
        )
        return redirect('core:contact')


def robots_txt(request):
    """Serves clean robots.txt linking to sitemap."""
    lines = [
        "User-agent: *",
        "Allow: /",
        "Disallow: /admin/",
        "Disallow: /ckeditor5/",
        f"Sitemap: {request.scheme}://{request.get_host()}/sitemap.xml",
    ]
    return HttpResponse("\n".join(lines), content_type="text/plain")


def custom_404_view(request, exception=None):
    return render(request, '404.html', status=404)


def custom_500_view(request):
    return render(request, '500.html', status=500)


def custom_403_view(request, exception=None):
    return render(request, '403.html', status=403)
