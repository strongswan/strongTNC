# -*- coding: utf-8 -*-
from __future__ import print_function, division, absolute_import, unicode_literals

from django.contrib import messages
from django.contrib.auth import authenticate, login as django_login, logout as django_logout
from django.views.decorators.http import require_http_methods
from django.shortcuts import render, redirect
from django.utils.translation import ugettext_lazy as _


@require_http_methods(('GET', 'POST'))
def login(request):
    """
    Login view
    """
    if request.method == 'POST':
        # Get login data from POST
        password = request.POST.get('password', None)
        username = request.POST.get('access_level', None)

        # Validate credentials
        if username not in ['admin-user', 'readonly-user']:
            # Make sure that people cannot log in as an arbitrary user
            # using faked HTTP requests.
            user = None
        else:
            # If authentication fails, the function returns ``None``.
            user = authenticate(username=username, password=password)

        # Authenticate user
        if user is not None and user.is_active:
            django_login(request, user)
            next_url = request.POST.get('next_url', None)
            if next_url is not None:
                return redirect(next_url)
            else:
                return redirect('/')
        else:
            messages.error(request, _('Bad password!'))

    if request.user.is_authenticated:
        return redirect('/')

    context = {'next_url': request.GET.get('next', '')}
    return render(request, 'authentication/login.html', context)


def logout(request):
    """
    Logout and redirect to login view
    """
    django_logout(request)
    messages.success(request, _('Logout successful!'))

    return render(request, 'authentication/login.html')
