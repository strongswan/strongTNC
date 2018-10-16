# -*- coding: utf-8 -*-
from __future__ import print_function, division, absolute_import, unicode_literals

from django.db.models import Count, Q
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_GET
from django.shortcuts import render
from django.utils.translation import ugettext_lazy as _

from apps.core.models import Session, Result, Identity
from apps.policies.models import Policy, Enforcement
from apps.devices.models import Device, Group, Product
from apps.packages.models import Package, Version
from apps.filesystem.models import Directory, File, FileHash
from apps.swid.models import Tag, TagStats, Entity, Event


@require_GET
@login_required
def overview(request):
    """
    Main page
    """
    return render(request, 'front/overview.html')


@require_GET
@login_required
def vulnerabilities(request):
    """
    Vulnerabilities view
    """
    context = {}
    context['title'] = _('Vulnerabilities')

    vulnerabilities = TagStats.objects.exclude(first_installed=None).filter(last_deleted=None,
                                                                     tag__version__security=1,
                                                                     device__inactive=False)
    context['vulnerabilities'] = vulnerabilities

    return render(request, 'front/vulnerabilities.html', context)


@require_GET
@login_required
def statistics(request):
    """
    Statistics view
    """
    context = {}
    context['title'] = _('Statistics')
    context['sessions'] = Session.objects.count()
    context['results'] = Result.objects.count()
    context['policies'] = Policy.objects.count()
    context['enforcements'] = Enforcement.objects.count()
    context['identities'] = Identity.objects.count()
    context['devices'] = Device.objects.count()
    context['products'] = Product.objects.count()
    context['groups'] = Group.objects.count()
    context['entities'] = Entity.objects.count()
    context['tags'] = Tag.objects.count()
    context['events'] = Event.objects.count()
    context['directories'] = Directory.objects.count()
    context['files'] = File.objects.count()
    context['hashes'] = FileHash.objects.count()
    context['packages'] = Package.objects.count()
    context['versions'] = Version.objects.count()
    context['secure'] = Version.objects.filter(security=0).count()
    context['vulnerable'] = Version.objects.filter(security=1).count()
    context['OSranking'] = Product.objects.annotate(
            num=Count('devices__id')).filter(num__gt=0).order_by('-num', 'name')

    context['rec_count_session'] = Session.objects.values('recommendation').annotate(
            num=Count('recommendation')).order_by('-num')

    for item in context['rec_count_session']:
        item['recommendation'] = Policy.action[item['recommendation']]

    context['rec_count_result'] = Result.objects.values('recommendation').annotate(
            num=Count('recommendation')).order_by('-num')

    for item in context['rec_count_result']:
        item['recommendation'] = Policy.action[item['recommendation']]

    return render(request, 'front/statistics.html', context)


@require_GET
@login_required
def search(request):
    """
    Global search view
    """
    context = {}
    context['group_title'] = _('Groups')
    context['policy_title'] = _('Policies')
    context['enforcement_title'] = _('Enforcements')
    context['device_title'] = _('Devices')
    context['package_title'] = _('Packages')
    context['product_title'] = _('Products')
    context['file_title'] = _('Files')

    context['groups'] = Group.objects.all().order_by('name')
    context['policies'] = Policy.objects.all().order_by('name')
    context['enforcements'] = Enforcement.objects.all().order_by('policy')
    context['devices'] = Device.objects.all().order_by('description')
    context['packages'] = Package.objects.all().order_by('name')
    context['products'] = Product.objects.all().order_by('name')
    context['files'] = File.objects.all().order_by('name')

    q = request.GET.get('q', '')
    if q != '':
        context['query'] = q
        context['groups'] = Group.objects.filter(name__icontains=q)
        context['policies'] = Policy.objects.filter(name__icontains=q)
        context['enforcements'] = Enforcement.objects.filter(
                Q(policy__name__icontains=q) | Q(group__name__icontains=q))
        context['devices'] = Device.objects.filter(
                Q(description__icontains=q) | Q(value__icontains=q))
        context['packages'] = Package.objects.filter(name__icontains=q)
        context['products'] = Product.objects.filter(name__icontains=q)
        q1 = Q(name__icontains=q)
        q2 = Q(directory__path__icontains=q)
        context['files'] = File.objects.filter(q1 | q2)

    return render(request, 'front/search.html', context)
