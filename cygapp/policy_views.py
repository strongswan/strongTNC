import re
from django.http import HttpResponse
from django.views.decorators.http import require_GET, require_POST
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render, redirect
from django.utils.translation import ugettext_lazy as _
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from models import Policy, Group, File, Directory

@require_GET
@login_required
def policies(request):
    context = {}
    context['title'] = _('Policies')
    context['count'] = Policy.objects.count()
    policies = Policy.objects.all().order_by('name')

    context['policies'] = paginate(policies, request)
    return render(request, 'cygapp/policies.html', context)

@require_GET
@login_required
def policy(request, policyID):
    try:
        policy = Policy.objects.get(pk=policyID)
    except Policy.DoesNotExist:
        policy = None
        messages.error(request, _('Policy not found!'))

    context = {}
    context['title'] = _('Policies')
    context['count'] = Policy.objects.count()
    policies = Policy.objects.all().order_by('name')

    context['policies'] = paginate(policies, request)

    if policy:
        context['policy'] = policy
        enforcements = policy.enforcements.all().order_by('id')
        context['enforcements'] = enforcements
        context['types'] = Policy.types
        for typ in context['types']:
            typ = _(typ)
        context['action'] = Policy.action
        files = File.objects.all().order_by('name')
        context['files'] = files
        dirs = Directory.objects.all().order_by('path')
        context['dirs'] = dirs

        groups = Group.objects.exclude(id__in = enforcements.values_list('id',
            flat=True))
        context['groups'] = groups
        context['title'] = _('Policy ') + policy.name

    return render(request, 'cygapp/policies.html', context)


@require_GET
@login_required
def add(request):
    context = {}
    policies = Policy.objects.all().order_by('name')
    context['policies'] = paginate(packages, request)
    context['title'] = _('New policy')
    context['count'] = Policy.objects.count()
    context['types'] = Policy.types
    context['action'] = Policy.action
    context['policy'] = Policy()
    files = File.objects.all().order_by('name')
    context['files'] = files
    dirs = Directory.objects.all().order_by('path')
    context['dirs'] = dirs
    return render(request, 'cygapp/policies.html', context)

@require_POST
@login_required
def save(request):
    policyID = request.POST['policyId']
    if not (policyID == 'None' or re.match(r'^\d+$', policyID)):
        raise ValueError
        return HttpResponse(status=400)

    type = request.POST['type']
    if not re.match(r'^\d+$', type) and int(type) in range(len(Policy.types)):
        raise ValueError
        return HttpResponse(status=400)

    type = int(type)

    fileID = request.POST.get('file','')
    file = None
    if not fileID == '':
        if not re.match(r'^\d+$', fileID):
            raise ValueError

        try:
            file = File.objects.get(pk=fileID)
        except (File.DoesNotExist):
            messages.warning(request, _('No such file'))

    dirID = request.POST.get('dir','')
    dir = None
    if not dirID == '':
        if not re.match(r'^\d+$', dirID):
            raise ValueError

        try:
            dir = Directory.objects.get(pk=dirID)
        except (Directory.DoesNotExist):
            messages.warning(request, _('No such directory'))

    argument = ''

    ranges = request.POST.get('range', None)
    flip = int(request.POST.get('flip', 0))
    if ranges != '':
        if not check_range(ranges):
            raise ValueError
        else:
            if flip:
                ranges = invert_range(ranges)


            argument = ranges

    fail = request.POST['fail']
    if not re.match(r'^\d+$', fail) and int(fail) in range(len(Policy.action)):
        raise ValueError
        return HttpResponse(status=400)

    noresult = request.POST['noresult']
    if not (re.match(r'^\d+$', noresult) and int(noresult) in
            range(len(Policy.action))):
        raise ValueError
        return HttpResponse(status=400)

    name = request.POST['name']
    if not re.match(r'^[\S ]+$', name):
        raise ValueError
        return HttpResponse(status=400)

    if policyID == 'None':
        policy = Policy(name=name, type=type, fail=fail,
                noresult=noresult, file=file, dir=dir, argument=argument)
    else:
        policy = get_object_or_404(Policy, pk=policyID)
        policy.name = name
        policy.type = type
        policy.file = file
        policy.dir = dir
        policy.fail = fail
        policy.noresult = noresult

    policy.argument = argument
    type_name = Policy.types[policy.type]
    arg_func = Policy.argument_funcs[type_name]
    policy.argument = arg_func(policy)
    policy.save()

    messages.success(request, _('Policy saved!'))
    return redirect('/policies/%d' % policy.id)

@require_POST
@login_required
def check(request):
    response = "false"
    if request.is_ajax():
        policy_name = request.POST['name']
        policy_id = request.POST['policy']
        if policy_id == 'None':
            policy_id = ''
        
        p = Policy.objects.filter(name=policy_name).count()
        if p != 0:
            if policy_id != '':
                policy_byid = Policy.objects.get(pk=policy_id)
                if policy_byid.name != policy_name:
                    response = "false"
                else:
                    response = "true"
            else:
                response = "false"
        else:
            response = "true"

    return HttpResponse("%s" % response)

@require_POST
@login_required
def delete(request, policyID):
    policy = get_object_or_404(Policy, pk=policyID)
    policy.delete()

    messages.success(request, _('Policy deleted!'))
    return redirect('/policies')
@require_GET
@login_required
def getAll(request):
    return Policy.count()


@require_GET
@login_required
def search(request):
    context = {}
    context['title'] = _('Policies')
    context['count'] = Policy.objects.count()
    policies = Policy.objects.all().order_by('name')
    
    q = request.GET.get('q', None)
    if q != '':
        context['query'] = q
        policies = Policy.objects.filter(name__icontains=q)
    else:
        return redirect('/policies')
    
    context['policies'] = paginate(policies, request)
    return render(request, 'cygapp/policies.html', context)

def check_range(ranges):
    if ranges == '': return True

    ranges = ranges.replace(' ','')
    for r in ranges.split(','):
        bounds = r.split('-', 1)
        for b in bounds:
            if not re.match('^\d+$', b):
                return False

        lower = int(bounds[0])
        upper = int(bounds[1]) if len(bounds) > 1 else -1

        if upper == -1:
            if not 0 <= lower <= 65535:
                return False
        else:
            if (not 0 <= upper <= 65535) or lower > upper:
                    return False
    return True

def invert_range(ranges):
    ranges = ranges.replace(' ','')

    #Very special cases
    if ranges == '0-65535': return ''
    if ranges == '': return '0-65535'

    doubles = []
    for r in ranges.split(','):
        bounds = r.split('-', 1)
        lower = int(bounds[0])
        upper = int(bounds[1]) if len(bounds) > 1 else -1

        if upper != -1:
            doubles.append((lower, upper))
        else:
            doubles.append((lower,lower))

    doubles.sort(reverse=True)
    ranges = []

    while len(doubles) > 0:
        d = doubles.pop()
        lower = int(d[0])
        upper = int(d[1])

        if len(ranges) == 0 and lower != 0:
            if lower != 1:
                ranges.append('0-%d' % (lower - 1))
            else:
                ranges.append('0')

        while len(doubles) > 0 and upper >= int(doubles[-1][0] - 1) :
            d2 = doubles.pop()
            if int(d2[1]) > upper:
               upper = int(d2[1])

        if len(doubles) > 0:
            if (upper + 1) != (doubles[-1][0] - 1):
                ranges.append('%d-%d' % (upper + 1, doubles[-1][0] - 1))
            else:
                ranges.append('%d' % (upper + 1))
        else:
            if upper != 65535:
                ranges.append('%d-65535' % (upper + 1))

    return ','.join(ranges)

def paginate(items, request):
    paginator = Paginator(items, 50) # Show 50 policies per page
    page = request.GET.get('page')
    try:
        policies = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        policies = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        policies = paginator.page(paginator.num_pages)
    
    return policies
