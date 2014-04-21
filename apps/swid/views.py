from django.views.generic import ListView, DetailView
from django.utils.translation import ugettext_lazy as _
from . import models


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