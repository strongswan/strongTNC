import re
from django import forms
from django.http import HttpResponse
from django.views.decorators.http import require_GET, require_safe
from django.shortcuts import render

@require_GET
def login(request):
    errors = []
    if 'username' in request.GET:
        username = request.GET['username']
        if not username:
            errors.append('Enter a username.')
        elif len(q) > 20:
            errors.append('Please enter at most 20 characters.')
    return render(request, 'cygapp/login.html', {'errors': errors})