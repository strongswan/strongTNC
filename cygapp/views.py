import base64   
from django.http import HttpResponse
from django.template import Context, loader
from django.shortcuts import get_object_or_404
from models import File,FileHash

def index(request):
    answer='Select view:<br/><a href=./files>Files</a>'
    return HttpResponse(answer)

def files(request):
    flist = File.objects.all()
    template = loader.get_template("cygapp/files.html")
    context = Context({ "flist": flist })
    return HttpResponse(template.render(context))

def fileshashes(request):
    flist = File.objects.all()
    answer = ""

    for f in flist:
        hashes = FileHash.objects.filter(file=f.id)
        answer += f.id.__str__() + ":" 
        for h in hashes:
            answer += h.__str__() + ","

        answer += "\n"
    return HttpResponse(answer)

def fileshashesjson(request):
    flist = File.objects.all()
    answer = "{["

    for file in flist:
        hashes = FileHash.objects.filter(file=file.id)
        answer += ",\n".join(hash.__json__() for hash in hashes)

    answer += "]}"
    return HttpResponse(answer, mimetype="application/json")

def file(request, fileid):
    f = get_object_or_404(File, pk=fileid)
    return HttpResponse(f.path)

def filejson(request, fileid):
    f = get_object_or_404(File, pk=fileid)
    return HttpResponse(f.__json__(), mimetype='application/json')

def filehashes(request, fileid):
    f = get_object_or_404(File, pk=fileid)
    hashes = FileHash.objects.filter(file=f.id)
    if hashes.count() == 0:
        return HttpResponse("No hashes")
    
    return HttpResponse("<br/>\n".join(hash.__str__() for hash in hashes))

def filehashesjson(request, fileid):
    f = get_object_or_404(File, pk=fileid)
    hashes = FileHash.objects.filter(file=f.id)
    if hashes.count() == 0:
        return HttpResponse("{}", mimetype='application/json')

    return HttpResponse("\n".join(hash.__json__() for hash in hashes), mimetype='application/json')

