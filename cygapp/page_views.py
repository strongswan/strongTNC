import re
from django.http import HttpResponse
from django.views.decorators.http import require_GET, require_POST
from django.contrib import messages
from django.shortcuts import get_object_or_404, render, redirect, render_to_response
from django.utils.translation import ugettext_lazy as _
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from models import Package

    
#@require_GET
#def pages(request):
#    context = {}
#    context['title'] = _('Packages')
#    context['packages'] = Package.objects.all().order_by('name')
#    return render(request, 'cygapp/pages.html', context)

def listing(request):
    contact_list = Package.objects.all()
    paginator = Paginator(contact_list, 25) # Show 25 contacts per page

    page = request.GET.get('page')
    try:
        packages = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        packages = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        packages = paginator.page(paginator.num_pages)

    return render_to_response('cygapp/pages.html', {"packages": packages})
