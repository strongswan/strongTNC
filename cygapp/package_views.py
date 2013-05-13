import re
from django.http import HttpResponse
from django.views.decorators.http import require_GET, require_POST
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render, redirect
from django.utils.translation import ugettext_lazy as _
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from models import Package, Version

@require_GET
@login_required
def packages(request):
    context = {}
    context['title'] = _('Packages')
    context['packages'] = Package.objects.all().order_by('name')
    
    paginator = Paginator(context['packages'], 50) # Show 50 packages per page
    page = request.GET.get('page')
    try:
        packages = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        packages = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        packages = paginator.page(paginator.num_pages)
    
    context['packages'] = packages

    return render(request, 'cygapp/packages.html', context)

@require_GET
@login_required
def package(request, packageID):
    try:
        package = Package.objects.get(pk=packageID)
    except Package.DoesNotExist:
        package = None
        messages.error(request, _('Package not found!'))

    context = {}
    context['packages'] = Package.objects.all().order_by('name')
    context['title'] = _('Packages')

    paginator = Paginator(context['packages'], 50) # Show 50 packages per page
    page = request.GET.get('page')
    try:
        packages = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        packages = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        packages = paginator.page(paginator.num_pages)
    
    context['packages'] = packages

    if package:
        context['package'] = package
        versions = package.versions.all().order_by('release')
        context['versions'] = versions
        context['title'] = _('Package ') + package.name

    return render(request, 'cygapp/packages.html', context)

@require_GET
@login_required
def add(request):
    context = {}
    context['title'] = _('New package')
    context['packages'] = Package.objects.all().order_by('name')[:50]
    context['package'] = Package()
    return render(request, 'cygapp/packages.html', context)


@require_POST
@login_required
def save(request):
    packageID = request.POST['packageId']
    if not (packageID == 'None' or re.match(r'^\d+$', packageID)):
        return HttpResponse(status=400)

    name = request.POST['name']
    if not re.match(r'^[\S]+$', name):
        return HttpResponse(status=400)

    blacklist = request.POST.get('blacklist')
    blacklist = True if blacklist=='blacklist' else False

    if packageID == 'None':
        package = Package.objects.create(name=name, blacklist=blacklist)
    else:
        package = get_object_or_404(Package, pk=packageID)
        package.name = name

        if blacklist != package.blacklist: 
            #Override blacklist settings on versions
            for version in package.versions.all():
                version.blacklist = None
                version.save()

        package.blacklist = blacklist
        package.save()

    messages.success(request, _('Package saved!'))
    return redirect('/packages/%d' % package.id)

@require_POST
@login_required
def delete(request, packageID):
    package = get_object_or_404(Package, pk=packageID)
    package.delete()

    messages.success(request, _('Package deleted!'))
    return redirect('/packages')

@require_GET
@login_required
def toggle_version(request, versionID):
    version = get_object_or_404(Version, pk=versionID)
    if version.blacklist == None:
        version.blacklist = 1 if version.package.blacklist == 0 else 0
    else:
        version.blacklist = 1 if version.blacklist == 0 else 0

    version.save()
    return HttpResponse(_('Yes' if version.blacklist else 'No'))

@require_GET
@login_required
def search(request):
    context = {}
    context['title'] = _('Packages')
    context['packages'] = Package.objects.all().order_by('name')
    
    if 'q' in request.GET:
        q = request.GET['q']
        if q:
            context['query'] = q
            context['packages'] = Package.objects.filter(name__icontains=q)

    paginator = Paginator(context['packages'], 50) # Show 50 packages per page
    page = request.GET.get('page')
    try:
        packages = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        packages = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        packages = paginator.page(paginator.num_pages)
    
    context['packages'] = packages
    return render(request, 'cygapp/packages.html', context)
