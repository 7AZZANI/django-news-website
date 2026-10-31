from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View

from .forms import NewsletterSubscriptionForm
from .models import NewsletterSubscriber


class SubscribeView(View):
    """
    Handles newsletter subscriptions via standard form POST or AJAX.
    """
    def post(self, request):
        form = NewsletterSubscriptionForm(request.POST)
        is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.content_type == 'application/json'

        if form.is_valid():
            email = form.cleaned_data['email']
            subscriber, created = NewsletterSubscriber.objects.get_or_create(
                email=email,
                defaults={'is_active': True, 'is_confirmed': True}
            )

            if not created and not subscriber.is_active:
                subscriber.is_active = True
                subscriber.unsubscribed_at = None
                subscriber.save(update_fields=['is_active', 'unsubscribed_at'])

            msg = "Thank you for subscribing to The Chronicle Daily! You will now receive our morning editorial briefing."

            if is_ajax:
                return JsonResponse({'status': 'success', 'message': msg})

            messages.success(request, msg)
            next_url = request.POST.get('next') or request.META.get('HTTP_REFERER') or '/'
            return redirect(next_url)
        else:
            err_msg = form.errors.get('email', ['Please enter a valid email address.'])[0]
            if is_ajax:
                return JsonResponse({'status': 'error', 'message': err_msg}, status=400)

            messages.error(request, err_msg)
            next_url = request.POST.get('next') or request.META.get('HTTP_REFERER') or '/'
            return redirect(next_url)


class UnsubscribeView(View):
    """
    One-click unsubscribe endpoint allowing readers to opt out safely.
    """
    template_name = 'newsletter/unsubscribed.html'

    def get(self, request, token):
        subscriber = get_object_or_404(NewsletterSubscriber, token=token)
        subscriber.unsubscribe()
        return render(request, self.template_name, {'subscriber': subscriber})
