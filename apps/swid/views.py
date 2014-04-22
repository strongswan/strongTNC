from django.views.generic import ListView, DetailView, TemplateView
from . import models
from tncapp import models as tnc_models


class RegidListView(ListView):
    queryset = models.Entity.objects.order_by('regid')
    template_name = 'swid/regid_list.html'


class RegidDetailView(DetailView):
    model = models.Entity
    template_name = 'swid/regid_detail.html'

    def get_context_data(self, **kwargs):
        context = super(RegidDetailView, self).get_context_data(**kwargs)
        context['object_list'] = self.model.objects.order_by('regid')
        return context


class SwidTagListView(ListView):
    queryset = models.Tag.objects.order_by('unique_id')
    template_name = 'swid/tags_list.html'


class SwidTagDetailView(DetailView):
    model = models.Tag
    template_name = 'swid/tags_detail.html'

    def get_context_data(self, **kwargs):
        context = super(SwidTagDetailView, self).get_context_data(**kwargs)
        context['object_list'] = self.model.objects.order_by('unique_id')
        context['entityroles'] = self.object.entityrole_set.all()
        return context
