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


class SwidInventoryView(DetailView):
    template_name = 'swid/swid_inventory.html'
    model = tnc_models.Device

    def get_context_data(self, **kwargs):
        context = super(SwidInventoryView, self).get_context_data(**kwargs)
        context['current_session'] = self.object.sessions.latest()
        return context
