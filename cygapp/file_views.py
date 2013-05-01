import re
from django.http import HttpResponse
from django.views.decorators.http import require_GET, require_POST
from django.contrib import messages
from django.shortcuts import get_object_or_404, render, redirect
from django.utils.translation import ugettext_lazy as _
from models import File

@require_GET
def files(request):
    context = {}
    context['title'] = _('Files')
    context['files'] = File.objects.all().order_by('name')
    return render(request, 'cygapp/files.html', context)

@require_GET
def file(request,fileID):
    try:
        file = File.objects.get(pk=fileID)
    except File.DoesNotExist:
        file = None
        messages.error(request, _('File not found!'))

    context = {}
    context['files'] = File.objects.all().order_by('name')
    context['title'] = _('Files')

    if file:
        context['file'] = file
        context['title'] = _('File ') + file.name

    return render(request, 'cygapp/files.html', context)

@require_GET
def add(request):
    context = {}
    context['title'] = _('New file')
    context['files'] = File.objects.all().order_by('name')
    context['file'] = File()
    return render(request, 'cygapp/files.html', context)


@require_POST
def save(request):
    fileID = request.POST['fileId']
    if not (fileID == 'None' or re.match(r'^\d+$', fileID)):
        return HttpResponse(status=400)

    name = request.POST['name']
    if not re.match(r'^[\S]+$', name):
        return HttpResponse(status=400)

    messages.success(request, _('File saved!'))
    return redirect('/files/%d' % file.id)

@require_GET
def delete(request, fileID):
    file = get_object_or_404(File, pk=fileID)
    file.delete()

    messages.success(request, _('File deleted!'))
    return redirect('/files')
