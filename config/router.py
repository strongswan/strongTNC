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

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """
        Routes migrations to appropriate database
        """
        meta_apps = app_label == 'auth' or app_label == 'admin' or \
                    app_label == 'contenttypes' or app_label == 'sessions'
        if db == 'meta':
            return meta_apps
        else:
            return not meta_apps

    def is_meta(self, model):
        """
        Check if the given model is Django meta data
        """
        return model._meta.db_table.startswith('auth_') or \
               model._meta.db_table.startswith('django_')

