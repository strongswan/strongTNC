# -*- coding: utf-8 -*-
from __future__ import print_function, division, absolute_import, unicode_literals

from django.contrib.auth.decorators import login_required, permission_required
from django.utils.decorators import method_decorator


class LoginRequiredMixin(object):
    """
    Ensure that user must be authenticated in order to access view.

    Example usage::

        class RegidListView(LoginRequiredMixin, ListView):
            queryset = models.Entity.objects.order_by('regid')
            template_name = 'swid/regid_list.html'

    """
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(LoginRequiredMixin, self).dispatch(*args, **kwargs)


class WritePermissionRequiredMixin(LoginRequiredMixin):
    """
    Ensure that user has the ``auth.write_access`` permission in order to
    access the view.

    This mixin extends the :class:`LoginRequiredMixin`, as there is no use in
    checking permissions for non-authenticated users.

    If a mixin with configurable permission or with multiple permission checks
    is required, it's probably the best idea to start using the django-braces
    package: http://django-braces.readthedocs.org/en/latest/access.html

    Example usage::

        class RegidListView(WritePermissionRequiredMixin, ListView):
            queryset = models.Entity.objects.order_by('regid')
            template_name = 'swid/regid_list.html'

    """
    @method_decorator(permission_required('auth.write_access', raise_exception=True))
    def dispatch(self, *args, **kwargs):
        return super(WritePermissionRequiredMixin, self).dispatch(*args, **kwargs)
