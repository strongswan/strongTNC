"""
Provides CRUD for files
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
from models import File, FileHash

@require_GET
@login_required
def files(request):
    """
    All files
    """
    context = {}
    context['title'] = _('Files')
    context['count'] = File.objects.count()
    files = File.objects.all().order_by('directory__path','name')    
    context['files'] = paginate(files, request)
    return render(request, 'cygapp/files.html', context)

@require_GET
@login_required
def file(request,fileID):
    """
    File detail view
    """
    try:
        file = File.objects.get(pk=fileID)
    except File.DoesNotExist:
        file = None
        messages.error(request, _('File not found!'))

    context = {}
    context['title'] = _('Files')
    context['count'] = File.objects.count()
    files = File.objects.all().order_by('directory__path','name')    

    context['files'] = paginate(files, request)

    if file:
        context['file'] = file
        context['title'] = _('File ') + file.name        
        file_hashes = file.hashes.all().order_by('product', 'algorithm')
        context['file_hashes'] = file_hashes

    return render(request, 'cygapp/files.html', context)

@require_POST
@login_required
def save(request):
    """
    Insert/update view
    """
    fileID = request.POST['fileId']
    if not (fileID == 'None' or re.match(r'^\d+$', fileID)):
        return HttpResponse(status=400)

    name = request.POST['name']
    if not re.match(r'^[\S]+$', name):
        return HttpResponse(status=400)

    messages.success(request, _('File saved!'))
    return redirect('/files/%d' % file.id)

@require_POST
@login_required
def delete(request, fileID):
    """
    Delete a file
    """
    file = get_object_or_404(File, pk=fileID)
    file.delete()

    messages.success(request, _('File deleted!'))
    return redirect('/files')

@require_GET
@login_required
def deleteHash(request, file_hashID):
    """
    Delete a file hash
    """
    hash = get_object_or_404(FileHash, pk=file_hashID)
    file = hash.file
    hash.delete()

    messages.success(request, _('Hash deleted!'))
    return redirect('/files/%d' % file.id)

@require_GET
@login_required
def search(request):
    """
    Filter files
    """
    context = {}
    context['title'] = _('Files')
    context['count'] = File.objects.count()
    files = File.objects.all().order_by('name')
    
    q = request.GET.get('q', None)
    if q != '':
        context['query'] = q
        q1 = Q(name__icontains=q)
        q2 = Q(directory__path__icontains=q)
        files = File.objects.filter(q1 | q2)
    else:
        return redirect('/files')
    
    context['files'] = paginate(files, request)
    return render(request, 'cygapp/files.html', context)

def paginate(items, request):
    """
    Paginated browsing
    """
    paginator = Paginator(items, 50) # Show 50 packages per page
    page = request.GET.get('page')
    try:
        files = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        files = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        files = paginator.page(paginator.num_pages)
    
    return files

