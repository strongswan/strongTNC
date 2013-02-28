from django.http import HttpResponse
from models import File,FileHash

def index(request):
    flist = File.objects.all()
    answer = '<br />\n'.join(file.path for file in flist)
    return HttpResponse(answer)
