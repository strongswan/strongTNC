import base64   
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse, HttpResponseRedirect
from django.template import Context, loader, RequestContext
from django.shortcuts import get_object_or_404, render
from models import *

def index(request):
    answer='Select view:<br/><a href=./files>Files</a>'
    return HttpResponse(answer)

def files(request):
    flist = File.objects.all()
    template = loader.get_template('cygapp/files.html')
    context = Context({ 'flist': flist })
    return HttpResponse(template.render(context))

def fileshashes(request):
    flist = File.objects.all()
    answer = ''

    for f in flist:
        hashes = FileHash.objects.filter(file=f.id)
        answer += f.id.__str__() + ':' 
        for h in hashes:
            answer += h.__str__() + ','

        answer += '\n'
    return HttpResponse(answer)

def fileshashesjson(request):
    flist = File.objects.all()
    answer = '{['

    for file in flist:
        hashes = FileHash.objects.filter(file=file.id)
        answer += ',\n'.join(hash.__json__() for hash in hashes)

    answer += ']}'
    return HttpResponse(answer, mimetype='application/json')

def file(request, fileid):
    f = get_object_or_404(File, pk=fileid)
    template = loader.get_template('cygapp/file.html')
    context = Context({ 'file': f})
    return HttpResponse(template.render(context))

def fileedit(request, fileid):
    if request.method == 'GET':
        f = get_object_or_404(File, pk=fileid)
        dirs = Directory.objects.all()
        context = Context({ 'file': f,
                            'dirs': dirs})

        return render(request, 'cygapp/fileedit.html', context)

    elif request.method == 'POST':
        f = get_object_or_404(File, pk=fileid)
        f.name = request.POST['name']
        template = loader.get_template('cygapp/fileedit.html')
        context = {}
        if request.POST['path'] is None or request.POST['path'] == '':
            context['file'] = f
            context['dirs'] = Directory.objects.all()
            context['message'] = 'Path cannot be empty!'
            c = Context(context)
            return render(request, 'cygapp/fileedit.html', context)

        dir, created = Directory.objects.get_or_create( path = request.POST['path'] )
        if created:
            print('Warning: had to create new directory (' + str(dir.id) + ')')

        print(str(dir.id) + ': ' + dir.path)
        f.directory = dir
        f.save()
        return HttpResponseRedirect('/cygapp/files/' + str(f.id) + '/edit')
    
    #No valid HTTP method
    raise Http500


def filejson(request, fileid):
    f = get_object_or_404(File, pk=fileid)
    return HttpResponse(f.__json__(), mimetype='application/json')

def filehashes(request, fileid):
    f = get_object_or_404(File, pk=fileid)
    hashes = FileHash.objects.filter(file=f.id)
    if hashes.count() == 0:
        return HttpResponse('No hashes')
    
    return HttpResponse('<br/>\n'.join(hash.__str__() for hash in hashes))

def filehashesjson(request, fileid):
    f = get_object_or_404(File, pk=fileid)
    hashes = FileHash.objects.filter(file=f.id)
    if hashes.count() == 0:
        return HttpResponse('{}', mimetype='application/json')

    return HttpResponse('\n'.join(hash.__json__() for hash in hashes), mimetype='application/json')

