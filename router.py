class DBRouter(object):
    """
    A router that splits django metadata from user data
    """

    def db_for_read(self, model, **hints):
        if model._meta.db_table.startswith('auth_') or \
                model._meta.db_table.startswith('django_') :
            return 'meta'

        return 'default'

    def db_for_write(self, model, **hints):
        if model._meta.db_table.startswith('auth_') or \
                model._meta.db_table.startswith('django_') :
            return 'meta'

        return 'default'

    def allow_syncdb(self, db, model):
        if (model._meta.db_table.startswith('auth_') or \
                model._meta.db_table.startswith('django_')):
            return db == 'meta'

        else:
            return db == 'default'
        
        
