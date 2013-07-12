"""
Provides CRUD for directories
"""

import re
from django.http import HttpResponse
from django.views.decorators.http import require_GET, require_POST
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render, redirect
from django.utils.translation import ugettext_lazy as _
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from models import Directory, File

@require_GET
@login_required
def directories(request):
    """
    All directories
    """
    context = {}
    context['title'] = _('Directories')
    context['count'] = Directory.objects.count()
    directories = Directory.objects.all().order_by('path')    
    context['directories'] = paginate(directories, request)
    return render(request, 'tncapp/directories.html', context)

@require_GET
@login_required
def directory(request,directoryID):
    """
    Directory detail view
    """
    try:
        directory = Directory.objects.get(pk=directoryID)
    except Directory.DoesNotExist:
        directory = None
        messages.error(request, _('Directory not found!'))

    context = {}
    context['title'] = _('Directories')
    context['count'] = Directory.objects.count()
    directories = Directory.objects.all().order_by('path')    

    context['directories'] = paginate(directories, request)

    if directories:
        context['directory'] = directory
        context['title'] = _('Directory ') + directory.path        
        files = File.objects.filter(directory=directory).order_by('name')
        context['files'] = files

    return render(request, 'tncapp/directories.html', context)

@require_GET
@login_required
def add(request):
    """
    Add a directory
    """
    context = {}
    context['title'] = _('New directory')
    context['count'] = Directory.objects.count()
    directories = Directory.objects.all().order_by('path')
    context['directories'] = paginate(directories, request)
    context['directory'] = Directory()
    return render(request, 'tncapp/directories.html', context)

@require_POST
@login_required
def save(request):
    """
    Insert/update view
    """
    directoryID = request.POST['directoryId']
    if not (directoryID == 'None' or re.match(r'^\d+$', directoryID)):
        return HttpResponse(status=400)

    path = request.POST['path']
    if not re.match(r'^[\S]+$', path):
        return HttpResponse(status=400)

    if directoryID == 'None':
        directory = Directory.objects.create(path=path)
    else:
        directory = get_object_or_404(Directory, pk=directoryID)
        directory.path = path
        directory.save()

    messages.success(request, _('Directory saved!'))
    return redirect('/directories/%d' % directory.id)

@require_POST
@login_required
def delete(request, directoryID):
    """
    Delete a directory
    """
    directory = get_object_or_404(Directory, pk=directoryID)
    directory.delete()

    messages.success(request, _('Directory deleted!'))
    return redirect('/directories')

@require_GET
@login_required
def search(request):
    """
    Filter directories
    """
    context = {}
    context['title'] = _('Directories')
    context['count'] = Directory.objects.count()
    directories = Directory.objects.all().order_by('path')
    
    q = request.GET.get('q', None)
    if q != '':
        context['query'] = q
        q1 = Q(path__icontains=q)
        directories = Directory.objects.filter(q1)
    else:
        return redirect('/directories')
    
    context['directories'] = paginate(directories, request)
    return render(request, 'tncapp/directories.html', context)

def paginate(items, request):
    """
    Paginated browsing
    """
    paginator = Paginator(items, 50) # Show 50 packages per page
    page = request.GET.get('page')
    try:
        directories = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        directories = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        directories = paginator.page(paginator.num_pages)
    
    return directories

