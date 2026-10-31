from django.contrib.auth import login, logout
from django.contrib.auth.views import LoginView as BaseLoginView
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView

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


def robots_txt(request):
    """Serves clean robots.txt linking to sitemap."""
    lines = [
        "User-agent: *",
        "Allow: /",
        "Disallow: /admin/",
        f"Sitemap: {request.scheme}://{request.get_host()}/sitemap.xml",
    ]
    return HttpResponse("\n".join(lines), content_type="text/plain")
