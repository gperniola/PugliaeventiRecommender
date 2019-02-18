from .models import Utente, Valutazione


class PugliaEventiRouter:

    def db_for_read(self, model, **hints):
        """ reading SomeModel from otherdb """
        if model._meta.app_label == 'api':
            return 'PugliaEventi'
        return None

    def db_for_write(self, model, **hints):
        """ writing SomeModel to otherdb """
        if model._meta.app_label == 'api':
            return 'PugliaEventi'
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if app_label == 'api':
            return db == 'PugliaEventi'
        return None
