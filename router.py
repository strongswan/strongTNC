class DBRouter(object):
    """
    A router that splits django metadata from user data
    """

    def db_for_read(self, model, **hints):
        if model._meta.db_table.startswith('auth_') or \
                model._meta.db_table.startswith('django_') :
            return 'meta'

        return 'cygnet'

    def db_for_write(self, model, **hints):
        if model._meta.db_table.startswith('auth_') or \
                model._meta.db_table.startswith('django_') :
            return 'meta'

        return 'cygnet'
        
