from django.apps import AppConfig


class NextstepsConfig(AppConfig):
    name = 'NextSteps'

    def ready(self):

        import NextSteps.signals
        
    