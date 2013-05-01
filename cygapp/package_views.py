import re
from django.http import HttpResponse
from django.views.decorators.http import require_GET, require_POST
from django.contrib import messages
from django.shortcuts import get_object_or_404, render, redirect
from django.utils.translation import ugettext_lazy as _
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from models import Package, Version

@require_GET
def packages(request):
    context = {}
    context['title'] = _('Packages')
    context['packages'] = Package.objects.all().order_by('name')[:10]
    return render(request, 'cygapp/packages.html', context)

@require_GET
def package(request, packageID):
    try:
        package = Package.objects.get(pk=packageID)
    except Package.DoesNotExist:
        package = None
        messages.error(request, _('Package not found!'))

    context = {}
    context['packages'] = Package.objects.all().order_by('name')[:10]
    context['title'] = _('Packages')

    if package:
        context['package'] = package
        versions = package.versions.all().order_by('release')
        context['versions'] = versions
        context['title'] = _('Package ') + package.name

    return render(request, 'cygapp/packages.html', context)

@require_GET
def add(request):
    context = {}
    context['title'] = _('New package')
    context['packages'] = Package.objects.all().order_by('name')[:10]
    context['package'] = Package()
    return render(request, 'cygapp/packages.html', context)


@require_POST
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

@require_GET
def delete(request, packageID):
    package = get_object_or_404(Package, pk=packageID)
    package.delete()

    messages.success(request, _('Package deleted!'))
    return redirect('/packages')

@require_GET
def toggle_version(request, versionID):
    version = get_object_or_404(Version, pk=versionID)
    if version.blacklist == None:
        version.blacklist = 1 if version.package.blacklist == 0 else 0
    else:
        version.blacklist = 1 if version.blacklist == 0 else 0

    version.save()
    return HttpResponse(_('Yes' if version.blacklist else 'No'))
