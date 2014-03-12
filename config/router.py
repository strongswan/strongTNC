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
        if self.is_meta(model):
            response = 'meta'

        return response

    def db_for_write(self, model, **hints):
        """
        Routes writing access requests
        """
        response = 'default'
        if self.is_meta(model):
            response = 'meta'

        return response

    def allow_syncdb(self, db, model):
        """
        For manage.py syncdb make sure data ends up in the right table
        """
        if db == 'meta':
            return self.is_meta(model)
        elif self.is_meta(model):
            return False

        return True

    def is_meta(self, model):
        """
        Check if the given model is Django meta data
        """
        return model._meta.db_table.startswith('auth_') or \
               model._meta.db_table.startswith('django_')

