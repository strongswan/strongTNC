"""
Database Router for strongTNC project
"""
class DBRouter(object):
    """
    A router that splits django metadata from user data
    """

    def db_for_read(self, model, **hints):
        """
        Routes reading access requests
        """
        response = 'default'
        if model._meta.db_table.startswith('auth_') or \
                model._meta.db_table.startswith('django_') :
            response = 'meta'

        return response

    def db_for_write(self, model, **hints):
        """
        Routes writing access requests
        """
        response = 'default'
        if model._meta.db_table.startswith('auth_') or \
                model._meta.db_table.startswith('django_') :
            response = 'meta'

        return response

    def allow_syncdb(self, db, model):
        """
        For manage.py syncdb
        """
        response = 'default'
        if (model._meta.db_table.startswith('auth_') or \
                model._meta.db_table.startswith('django_')):
            response = 'meta'

        return response

