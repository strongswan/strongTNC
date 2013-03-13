class DBRouter(object):
    """
    A router that splits django metadata from user data
    """

    def db_for_read(self, model, **hints):
        if model._meta.db_table[:5] == 'auth_' or model._meta.db_table[:7] == 'django_' :
            print model._meta.db_table + " -> read from meta"
            return 'meta'

        print model._meta.db_table + " -> read from cygnet"
        return 'cygnet'

    def db_for_write(self, model, **hints):
        if model._meta.db_table[:5] == 'auth_' or model._meta.db_table[:7] == 'django_' :
            print model._meta.db_table + " -> write to meta"
            return 'meta'

        print model._meta.db_table + " -> write to cygnet"
        return 'cygnet'
        
